package ai.aol.demo

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {

    private val vm: AolViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        vm.connect()
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AolDemoScreen(vm)
                }
            }
        }
    }
}

@OptIn(androidx.compose.material3.ExperimentalMaterial3Api::class)
@Composable
private fun AolDemoScreen(vm: AolViewModel) {
    val state by vm.ui.collectAsState()
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("AOL · Moto AI demo") })
        },
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            HeaderCard(rulesVersion = state.rulesVersion)
            ContextCard(
                battery = state.batteryPct,
                dataSaver = state.dataSaver,
                privateMode = state.privateMode,
                onBattery = vm::setBattery,
                onDataSaver = vm::setDataSaver,
                onPrivate = vm::setPrivateMode,
            )
            SurfaceCard(visible = state.visible, hidden = state.hideRecommended)
            ActionsCard(
                visible = state.visible,
                onRoute = { id -> vm.routeAndLog(id, payloadKb = 64) },
                onRouteHeavy = { id -> vm.routeAndLog(id, payloadKb = 512) },
            )
            LogCard(log = state.log)
        }
    }
}

@Composable
private fun HeaderCard(rulesVersion: Int) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp)) {
            Text(
                "AI Optimisation Layer",
                style = MaterialTheme.typography.titleMedium,
            )
            Text(
                "AOL middleware bound via AIDL · rules v$rulesVersion",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun ContextCard(
    battery: Int,
    dataSaver: Boolean,
    privateMode: Boolean,
    onBattery: (Int) -> Unit,
    onDataSaver: (Boolean) -> Unit,
    onPrivate: (Boolean) -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Context (Module 3)", style = MaterialTheme.typography.titleSmall)
            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                Text("Battery $battery%")
                Spacer(Modifier.width(12.dp))
                Button(onClick = { onBattery(if (battery > 20) 12 else 80) }) {
                    Text(if (battery > 20) "→ low (12%)" else "→ healthy (80%)")
                }
            }
            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                Text("Data Saver")
                Spacer(Modifier.width(12.dp))
                Switch(checked = dataSaver, onCheckedChange = onDataSaver)
            }
            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                Text("Private mode")
                Spacer(Modifier.width(12.dp))
                Switch(checked = privateMode, onCheckedChange = onPrivate)
            }
        }
    }
}

@Composable
private fun SurfaceCard(visible: List<String>, hidden: List<String>) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Surface (Module 2)", style = MaterialTheme.typography.titleSmall)
            Text("Visible: ${visible.joinToString(", ")}", style = MaterialTheme.typography.bodySmall)
            if (hidden.isNotEmpty()) {
                Text(
                    "Auto-hidden: ${hidden.joinToString(", ")}",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray,
                )
            }
        }
    }
}

@Composable
private fun ActionsCard(
    visible: List<String>,
    onRoute: (String) -> Unit,
    onRouteHeavy: (String) -> Unit,
) {
    Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Route a feature (Module 4)", style = MaterialTheme.typography.titleSmall)
            visible.take(4).forEach { id ->
                Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                    Text(id, modifier = Modifier.width(180.dp))
                    Button(onClick = { onRoute(id) }) { Text("64kb") }
                    Spacer(Modifier.width(8.dp))
                    Button(onClick = { onRouteHeavy(id) }) { Text("512kb") }
                }
            }
        }
    }
}

@Composable
private fun LogCard(log: List<AolViewModel.LogEntry>) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text("Recent decisions (Module 6)", style = MaterialTheme.typography.titleSmall)
            if (log.isEmpty()) {
                Text("Tap a feature button above to log a decision.")
            }
            log.forEach { e ->
                Text(
                    "${e.featureId}  →  ${e.decision}  · ${e.chosenMs}ms · \$${"%.4f".format(e.costUsd)}",
                    style = MaterialTheme.typography.bodySmall,
                )
                Text(
                    "    ${e.reason}",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray,
                )
            }
        }
    }
}
