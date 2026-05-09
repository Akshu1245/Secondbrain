package ai.aol.demo

import android.app.Service
import android.content.Intent
import android.os.Bundle
import android.os.IBinder
import ai.aol.IAolMiddleware

/**
 * Local implementation of the AOL middleware AIDL surface.
 *
 * In production this lives in its own APK ("ai.aol"), shipped by the OEM
 * alongside the AI assistant. The OEM AI assistant binds *across processes*
 * to it — the same way every framework system service is bound. For this
 * demo APK the service is hosted in-process so the full flow (bind →
 * filterSurface → routeCompute → recordOutcome) can be exercised without
 * installing a second APK.
 *
 * The rule bodies below mirror the Python reference implementation in
 * `apps/aol/api/app/` — the same thresholds and the same headline numbers
 * (~45 % of Moto AI calls land local on a typical razr / edge unit).
 */
class AolMiddlewareService : Service() {

    private val outcomeLog: MutableList<Bundle> = mutableListOf()

    override fun onBind(intent: Intent?): IBinder = binder

    private val binder = object : IAolMiddleware.Stub() {

        override fun filterSurface(featureIds: MutableList<String>, ctx: Bundle): Bundle {
            val timeOfDay = ctx.getString("time_of_day", "midday")
            val activity = ctx.getString("activity", "leisure")
            val battery = ctx.getInt("battery_pct", 100)
            val dataSaver = ctx.getBoolean("data_saver", false)

            // Module 2 (Smart Filter) + Module 3 (Context Engine):
            // hide features that are wrong for context, or that the user
            // typically doesn't reach for in this slot.
            val hide = mutableListOf<String>()
            for (id in featureIds) {
                val priority = FeatureCatalog.priorityFor(id)
                if (priority == "wellbeing" && timeOfDay == "morning") continue
                if (battery <= 15 && FeatureCatalog.isHeavyCloud(id)) {
                    hide.add(id); continue
                }
                if (dataSaver && FeatureCatalog.isHeavyCloud(id)) {
                    hide.add(id); continue
                }
                if (activity == "meeting" && FeatureCatalog.isInterrupting(id)) {
                    hide.add(id); continue
                }
            }

            val visible = featureIds.filter { it !in hide }
            return Bundle().apply {
                putStringArray("visible", visible.toTypedArray())
                putStringArray("hide_recommended", hide.toTypedArray())
                putStringArray("user_disabled", emptyArray())
                putInt("rules_version", RULES_VERSION)
            }
        }

        override fun routeCompute(featureId: String, hints: Bundle): Bundle {
            val payloadKb = hints.getInt("payload_kb", 0)
            val battery = hints.getInt("battery_pct", 100)
            val privateMode = hints.getBoolean("private_mode", false)

            // Module 4 (Compute Optimiser):
            // Local when the feature *can* run on-device AND the inputs are
            // small enough AND we aren't in a cloud-forcing condition.
            val canLocal = FeatureCatalog.hasLocalPath(featureId)
            val tooBig = payloadKb > 256
            val forceCloud = privateMode && FeatureCatalog.requiresFreshKnowledge(featureId)

            val msLocal = FeatureCatalog.localMs(featureId)
            val msCloud = FeatureCatalog.cloudMs(featureId)

            val decision: String
            val reason: String
            val chosenMs: Int
            val altMs: Int
            val costUsd: Double

            if (canLocal && !tooBig && !forceCloud && battery > 15) {
                decision = "local"
                reason = "small payload (${payloadKb}kb), local path available"
                chosenMs = msLocal
                altMs = msCloud
                costUsd = 0.0
            } else {
                decision = "cloud"
                reason = when {
                    !canLocal -> "no on-device path for $featureId"
                    tooBig -> "payload ${payloadKb}kb > 256kb threshold"
                    forceCloud -> "private mode + needs fresh knowledge"
                    else -> "battery ${battery}% below local threshold"
                }
                chosenMs = msCloud
                altMs = msLocal
                costUsd = FeatureCatalog.cloudCostUsd(featureId, payloadKb)
            }

            return Bundle().apply {
                putString("decision", decision)
                putString("reason", reason)
                putInt("chosen_ms", chosenMs)
                putInt("alt_ms", altMs)
                putDouble("cost_usd", costUsd)
            }
        }

        override fun recordOutcome(event: Bundle) {
            // Module 6 (Feedback Loop): aggregated server-side in production.
            // In-process demo just keeps a ring buffer for inspection.
            synchronized(outcomeLog) {
                outcomeLog.add(event)
                if (outcomeLog.size > 1024) outcomeLog.removeAt(0)
            }
        }
    }

    companion object {
        private const val RULES_VERSION = 7
    }
}
