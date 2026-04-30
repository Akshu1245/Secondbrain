/*
 * AolClient.kt
 *
 * A reference Kotlin client showing how the OEM AI assistant (Moto AI,
 * Galaxy AI, OxygenOS AI, ...) plugs into the AOL middleware service.
 *
 * This is the file an integration engineer at the OEM would copy into their
 * existing AI assistant module. Three call sites exist in a typical flagship
 * AI-assistant launcher:
 *
 *   1. Before rendering the home strip → call `filterSurface()`
 *   2. Right before dispatching a feature → call `routeCompute()`
 *   3. After the feature finishes (or after explicit feedback) → call
 *      `recordOutcome()`
 *
 * AOL handles the rest: state, persistence, nightly improvement suggestions,
 * Control Panel, etc. The OEM assistant doesn't have to model any of this.
 */

package com.example.oem.ai.assistant

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.IBinder
import android.os.RemoteException
import android.util.Log
import ai.aol.IAolMiddleware

class AolClient(private val ctx: Context) {

    private var service: IAolMiddleware? = null

    /** Bind once, near app startup. */
    fun connect(onReady: () -> Unit) {
        val intent = Intent("ai.aol.IAolMiddleware").apply {
            // The AOL APK declares its service with this exported component
            // name; the OEM assistant can hard-code it.
            component = ComponentName("ai.aol", "ai.aol.AolMiddlewareService")
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

    /**
     * Call **before** rendering the AI feature strip on the home screen / pull-down.
     * Returns the cleaned, ordered list of feature IDs the OEM assistant should
     * actually display, plus the IDs that AOL recommends hiding.
     */
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
            visible          = out.getStringArray("visible")?.toList()           ?: rawFeatureIds,
            hideRecommended  = out.getStringArray("hide_recommended")?.toList()  ?: emptyList(),
            userDisabled     = out.getStringArray("user_disabled")?.toList()     ?: emptyList(),
            rulesVersion     = out.getInt("rules_version", 0),
        )
    }

    /**
     * Call **before** dispatching a feature invocation. The decision tells
     * the assistant whether to call its on-device path or its cloud backend
     * (Gemini / Perplexity / first-party).
     */
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
            reason   = out.getString("reason", "AOL unreachable, fallback"),
            chosenMs = out.getInt("chosen_ms", -1),
            altMs    = out.getInt("alt_ms", -1),
            costUsd  = out.getDouble("cost_usd", 0.0),
        )
    }

    /**
     * Record an outcome (or user feedback). One-way / fire-and-forget — never
     * blocks the UI thread. AOL aggregates these into the Control Panel
     * "improvement suggestions" feed.
     */
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

    // ── Fallbacks ─────────────────────────────────────────────────────────
    // Crucial: the OEM assistant must keep working even if AOL is uninstalled
    // or crashed. These match the "don't optimise" behaviour: show everything
    // and route everything to cloud (the existing default).

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
        val decision: String,    // "local" or "cloud"
        val reason: String,
        val chosenMs: Int,
        val altMs: Int,
        val costUsd: Double,
    )

    companion object {
        private const val TAG = "AolClient"
    }
}

/* ── End-to-end usage example, inside the OEM AI assistant launcher: ───────

class MotoAiLauncherFragment : Fragment() {

    private lateinit var aol: AolClient

    override fun onResume() {
        super.onResume()
        aol = AolClient(requireContext())
        aol.connect {
            renderHomeStrip()
        }
    }

    private fun renderHomeStrip() {
        val rawIds = listOf(
            "smart_reply", "magic_eraser", "live_translate",
            "wallpaper_studio", "circle_to_search", // ...
        )
        val surface = aol.filterSurface(
            rawFeatureIds = rawIds,
            timeOfDay     = currentTimeOfDay(),
            activity      = currentActivity(),
            batteryPct    = currentBattery(),
            dataSaver     = isDataSaver(),
        )
        showFeatures(surface.visible)
        // surface.hideRecommended → optionally show as "More AI features"
    }

    private fun onFeatureTapped(id: String, payloadKb: Int) {
        val r = aol.routeCompute(id, payloadKb, currentBattery(), isPrivateMode())
        if (r.decision == "local") runOnDevice(id) else callCloud(id)
        aol.recordOutcome(id, success = true)
    }
}

──────────────────────────────────────────────────────────────────────────── */
