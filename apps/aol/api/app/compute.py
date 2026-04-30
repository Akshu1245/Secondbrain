"""Module 4 — Compute Optimizer.

Decide whether a feature invocation should run *on-device* or be offloaded
to the *cloud*. Logic is rule-based; the goal is to reduce avoidable cloud
calls (cost + privacy) while keeping perceived latency acceptable.

Each decision is logged so the dashboard can show the optimiser's reasoning
to the user (and to an OEM PM watching the demo).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from . import store

# Heavy tasks generally win latency-wise on cloud. Light tasks usually finish
# faster on-device; routing them to cloud just adds network latency + cost.
LATENCY_BUDGET_MS = 1500       # if local is ≤ this, prefer local
COST_PER_CLOUD_CALL_USD = 0.0008


def route(feature_id: str, *, payload_kb: int = 0) -> dict[str, Any]:
    state = store.get_state()
    feat = state["features"].get(feature_id)
    if not feat:
        raise KeyError(feature_id)

    prefs = state["user_prefs"]
    ms_local = feat["ms_local"]
    ms_cloud = feat["ms_cloud"] + payload_kb // 64       # rough upload penalty

    # Hard rules first.
    if prefs["private_mode"]:
        decision, reason = "local", "private_mode=on"
    elif prefs["data_saver"] and feat["compute_class"] != "heavy":
        decision, reason = "local", "data_saver=on for non-heavy task"
    elif prefs["battery_saver"] and feat["compute_class"] == "heavy":
        decision, reason = "cloud", "battery_saver=on, heavy task → offload"
    elif feat["compute_class"] == "light" and ms_local <= LATENCY_BUDGET_MS:
        decision, reason = "local", f"light task fits budget ({ms_local}ms ≤ {LATENCY_BUDGET_MS}ms)"
    elif feat["compute_class"] == "heavy":
        decision, reason = "cloud", "heavy compute → cloud cheaper on latency"
    elif ms_local <= ms_cloud:
        decision, reason = "local", f"local faster ({ms_local}ms ≤ {ms_cloud}ms)"
    else:
        decision, reason = "cloud", f"cloud faster ({ms_cloud}ms < {ms_local}ms)"

    chosen_ms = ms_local if decision == "local" else ms_cloud
    other_ms  = ms_cloud if decision == "local" else ms_local
    cost_usd = 0.0 if decision == "local" else COST_PER_CLOUD_CALL_USD

    log_entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "feature_id": feature_id,
        "feature_name": feat["name"],
        "compute_class": feat["compute_class"],
        "decision": decision,
        "reason": reason,
        "chosen_ms": chosen_ms,
        "alt_ms": other_ms,
        "cost_usd": cost_usd,
        "payload_kb": payload_kb,
    }
    state["compute_log"].insert(0, log_entry)
    state["compute_log"] = state["compute_log"][:200]
    store.save()
    return log_entry


def recent_log(limit: int = 50) -> list[dict[str, Any]]:
    return store.get_state()["compute_log"][:limit]


def aggregate() -> dict[str, Any]:
    log = store.get_state()["compute_log"]
    n = len(log)
    if n == 0:
        return {"total": 0, "local_pct": 0, "cloud_pct": 0, "saved_usd": 0.0,
                "saved_ms_avg": 0}
    local = [e for e in log if e["decision"] == "local"]
    cloud = [e for e in log if e["decision"] == "cloud"]
    saved_usd = round(len(local) * COST_PER_CLOUD_CALL_USD, 4)
    saved_ms = sum(e["alt_ms"] - e["chosen_ms"] for e in log)
    return {
        "total": n,
        "local_pct": round(100 * len(local) / n, 1),
        "cloud_pct": round(100 * len(cloud) / n, 1),
        "saved_usd": saved_usd,
        "saved_ms_total": saved_ms,
        "saved_ms_avg": round(saved_ms / n, 1),
    }
