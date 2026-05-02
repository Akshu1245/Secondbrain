package ai.aol.demo

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

/**
 * UI state for the AOL demo screen.
 *
 * Holds the current surface decision (which Moto AI features should show)
 * and an event log that grows as the user routes / records outcomes.
 */
class AolViewModel(app: Application) : AndroidViewModel(app) {

    private val client = AolClient(app)
    private val _ui = MutableStateFlow(UiState())
    val ui: StateFlow<UiState> = _ui.asStateFlow()

    fun connect() {
        client.connect {
            refreshSurface()
        }
    }

    fun refreshSurface() {
        val all = FeatureCatalog.all()
        val s = client.filterSurface(
            rawFeatureIds = all,
            timeOfDay = _ui.value.timeOfDay,
            activity = _ui.value.activity,
            batteryPct = _ui.value.batteryPct,
            dataSaver = _ui.value.dataSaver,
        )
        _ui.update {
            it.copy(
                visible = s.visible,
                hideRecommended = s.hideRecommended,
                rulesVersion = s.rulesVersion,
            )
        }
    }

    fun setTimeOfDay(t: String) {
        _ui.update { it.copy(timeOfDay = t) }
        refreshSurface()
    }

    fun setBattery(pct: Int) {
        _ui.update { it.copy(batteryPct = pct) }
        refreshSurface()
    }

    fun setDataSaver(on: Boolean) {
        _ui.update { it.copy(dataSaver = on) }
        refreshSurface()
    }

    fun setPrivateMode(on: Boolean) {
        _ui.update { it.copy(privateMode = on) }
    }

    fun routeAndLog(featureId: String, payloadKb: Int) {
        val r = client.routeCompute(
            featureId = featureId,
            payloadKb = payloadKb,
            batteryPct = _ui.value.batteryPct,
            privateMode = _ui.value.privateMode,
        )
        client.recordOutcome(featureId, success = true)
        _ui.update {
            val entry = LogEntry(
                featureId = featureId,
                decision = r.decision,
                reason = r.reason,
                chosenMs = r.chosenMs,
                altMs = r.altMs,
                costUsd = r.costUsd,
            )
            it.copy(log = (listOf(entry) + it.log).take(20))
        }
    }

    data class UiState(
        val visible: List<String> = emptyList(),
        val hideRecommended: List<String> = emptyList(),
        val rulesVersion: Int = 0,
        val timeOfDay: String = "midday",
        val activity: String = "leisure",
        val batteryPct: Int = 80,
        val dataSaver: Boolean = false,
        val privateMode: Boolean = false,
        val log: List<LogEntry> = emptyList(),
    )

    data class LogEntry(
        val featureId: String,
        val decision: String,
        val reason: String,
        val chosenMs: Int,
        val altMs: Int,
        val costUsd: Double,
    )
}
