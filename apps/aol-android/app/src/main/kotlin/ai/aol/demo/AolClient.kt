package ai.aol.demo

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.IBinder
import android.os.RemoteException
import android.util.Log
import ai.aol.IAolMiddleware

/**
 * Reference Kotlin client showing how the OEM AI assistant (Moto AI,
 * Galaxy AI, OxygenOS AI ...) plugs into the AOL middleware service.
 *
 * Three call sites in a typical AI-assistant launcher:
 *   1. Before rendering the home strip → [filterSurface]
 *   2. Right before dispatching a feature → [routeCompute]
 *   3. After the feature finishes → [recordOutcome] / [recordFeedback]
 *
 * AOL handles the rest: state, persistence, nightly improvement
 * suggestions, Control Panel. The OEM AI assistant doesn't model any
 * of this.
 *
 * If AOL is uninstalled or crashed, every method falls back to the
 * "show everything / route to cloud" default so the OEM assistant
 * keeps working.
 */
class AolClient(private val ctx: Context) {

    @Volatile private var service: IAolMiddleware? = null

    fun connect(onReady: () -> Unit) {
        val intent = Intent("ai.aol.IAolMiddleware").apply {
            // In production this points at the AOL APK ("ai.aol"). For the
            // self-contained demo APK we point at our in-process service.
            component = ComponentName(ctx.packageName, "ai.aol.demo.AolMiddlewareService")
        }
        ctx.bindService(intent, object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
                service = IAolMiddleware.Stub.asInterface(binder)
                onReady()
            }

            override fun onServiceDisconnected(name: ComponentName?) {
                service = null
            }
        }, Context.BIND_AUTO_CREATE)
    }

    fun filterSurface(
        rawFeatureIds: List<String>,
        timeOfDay: String,
        activity: String,
        batteryPct: Int,
        dataSaver: Boolean,
    ): SurfaceDecision {
        val ctxBundle = Bundle().apply {
            putString("time_of_day", timeOfDay)
            putString("activity", activity)
            putInt("battery_pct", batteryPct)
            putBoolean("data_saver", dataSaver)
        }
        val out: Bundle = try {
            service?.filterSurface(rawFeatureIds, ctxBundle) ?: defaultSurface(rawFeatureIds)
        } catch (e: RemoteException) {
            Log.w(TAG, "AOL filterSurface failed; falling back to raw surface", e)
            defaultSurface(rawFeatureIds)
        }
        return SurfaceDecision(
            visible = out.getStringArray("visible")?.toList() ?: rawFeatureIds,
            hideRecommended = out.getStringArray("hide_recommended")?.toList() ?: emptyList(),
            userDisabled = out.getStringArray("user_disabled")?.toList() ?: emptyList(),
            rulesVersion = out.getInt("rules_version", 0),
        )
    }

    fun routeCompute(
        featureId: String,
        payloadKb: Int,
        batteryPct: Int,
        privateMode: Boolean,
    ): RouteDecision {
        val hints = Bundle().apply {
            putInt("payload_kb", payloadKb)
            putInt("battery_pct", batteryPct)
            putBoolean("private_mode", privateMode)
        }
        val out: Bundle = try {
            service?.routeCompute(featureId, hints) ?: defaultRoute()
        } catch (e: RemoteException) {
            Log.w(TAG, "AOL routeCompute failed; defaulting to cloud", e)
            defaultRoute()
        }
        return RouteDecision(
            decision = out.getString("decision", "cloud"),
            reason = out.getString("reason", "AOL unreachable, fallback"),
            chosenMs = out.getInt("chosen_ms", -1),
            altMs = out.getInt("alt_ms", -1),
            costUsd = out.getDouble("cost_usd", 0.0),
        )
    }

    fun recordOutcome(featureId: String, success: Boolean) {
        val ev = Bundle().apply {
            putString("feature_id", featureId)
            putString("kind", "outcome")
            putBoolean("success", success)
            putLong("ts_ms", System.currentTimeMillis())
        }
        try { service?.recordOutcome(ev) } catch (_: RemoteException) {}
    }

    fun recordFeedback(featureId: String, rating: String) {
        val ev = Bundle().apply {
            putString("feature_id", featureId)
            putString("kind", "feedback")
            putString("rating", rating)
            putLong("ts_ms", System.currentTimeMillis())
        }
        try { service?.recordOutcome(ev) } catch (_: RemoteException) {}
    }

    private fun defaultSurface(ids: List<String>): Bundle = Bundle().apply {
        putStringArray("visible", ids.toTypedArray())
        putStringArray("hide_recommended", emptyArray())
        putStringArray("user_disabled", emptyArray())
        putInt("rules_version", 0)
    }

    private fun defaultRoute(): Bundle = Bundle().apply {
        putString("decision", "cloud")
        putString("reason", "AOL unreachable")
        putInt("chosen_ms", -1)
        putInt("alt_ms", -1)
        putDouble("cost_usd", 0.0)
    }

    data class SurfaceDecision(
        val visible: List<String>,
        val hideRecommended: List<String>,
        val userDisabled: List<String>,
        val rulesVersion: Int,
    )

    data class RouteDecision(
        val decision: String,
        val reason: String,
        val chosenMs: Int,
        val altMs: Int,
        val costUsd: Double,
    )

    companion object {
        private const val TAG = "AolClient"
    }
}
