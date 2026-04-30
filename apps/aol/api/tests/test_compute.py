"""Tests for the compute optimiser (Module 4).

The most important test in this file is
``test_aggregate_saved_ms_is_summed_over_local_routes_only`` — it pins the
fix from commit ``b550b2d`` so the headline ``saved_ms`` number can never
silently regress to a ~50× inflated value (the bug was: the original code
summed ``alt_ms - chosen_ms`` over *all* routes including cloud, where the
delta is negative and the "saving" is fictitious).
"""

from __future__ import annotations

import pytest

from app import compute, filter as feature_filter, store


def _route_many(feature_id: str, n: int = 3) -> list[dict]:
    return [compute.route(feature_id) for _ in range(n)]


def test_private_mode_forces_local_for_any_feature():
    feature_filter.set_prefs(private_mode=True)
    out = compute.route("live_translate")  # heavy, would normally go cloud
    assert out["decision"] == "local"
    assert "private_mode" in out["reason"]


def test_data_saver_routes_non_heavy_locally():
    feature_filter.set_prefs(data_saver=True)
    out = compute.route("smart_reply")  # light
    assert out["decision"] == "local"
    assert "data_saver" in out["reason"]


def test_battery_saver_offloads_heavy_to_cloud():
    feature_filter.set_prefs(battery_saver=True)
    out = compute.route("live_translate")  # heavy
    assert out["decision"] == "cloud"
    assert "battery_saver" in out["reason"]


def test_light_task_under_latency_budget_runs_locally():
    out = compute.route("smart_reply")
    state = store.get_state()
    feat = state["features"]["smart_reply"]
    assert feat["compute_class"] == "light"
    assert feat["ms_local"] <= compute.LATENCY_BUDGET_MS
    assert out["decision"] == "local"


def test_heavy_task_defaults_to_cloud():
    out = compute.route("live_translate")
    assert out["decision"] == "cloud"


def test_unknown_feature_id_raises_keyerror():
    with pytest.raises(KeyError):
        compute.route("not_a_real_feature")


def test_recent_log_returns_decisions_in_reverse_chronological_order():
    compute.route("smart_reply")
    compute.route("live_translate")
    log = compute.recent_log()
    assert log[0]["feature_id"] == "live_translate"
    assert log[1]["feature_id"] == "smart_reply"


def test_aggregate_saved_ms_is_summed_over_local_routes_only():
    """Regression-pin for commit b550b2d.

    Before the fix, ``saved_ms`` summed ``alt_ms - chosen_ms`` over ALL
    routes — including cloud routes where the local alternative was much
    slower, which inflated the headline figure ~50× (1,904 ms vs the
    honest ~38 ms).
    """
    _route_many("smart_reply", n=5)       # → local, contributes savings
    _route_many("live_translate", n=5)    # → cloud, must NOT contribute

    log = compute.recent_log(limit=200)
    locals_ = [e for e in log if e["decision"] == "local"]
    clouds = [e for e in log if e["decision"] == "cloud"]
    assert len(locals_) == 5
    assert len(clouds) == 5

    expected_local_savings = sum(e["alt_ms"] - e["chosen_ms"] for e in locals_)
    # Adversarial sanity: the buggy version would have included cloud
    # routes, where alt_ms - chosen_ms is *negative* (local is slower for
    # heavy features) — so totals would diverge if the bug regressed.
    naive_buggy_sum = sum(e["alt_ms"] - e["chosen_ms"] for e in log)
    assert naive_buggy_sum != expected_local_savings, (
        "test setup failed to construct a divergence; pick features whose "
        "local/cloud deltas have opposite signs"
    )

    agg = compute.aggregate()
    assert agg["saved_ms_total"] == expected_local_savings
    # And `saved_ms_avg` must be amortised over the *full* decision count
    # (the savings number is cumulative, the average is per request).
    assert agg["saved_ms_avg"] == round(expected_local_savings / agg["total"], 1)


def test_aggregate_zero_routes_returns_safe_defaults():
    agg = compute.aggregate()
    assert agg["total"] == 0
    assert agg["saved_ms_avg"] == 0


def test_aggregate_saved_usd_only_counts_local_routes():
    _route_many("smart_reply", n=3)        # local: 3 × $0.0008 saved
    _route_many("live_translate", n=2)     # cloud: $0 saved
    agg = compute.aggregate()
    assert agg["saved_usd"] == round(3 * compute.COST_PER_CLOUD_CALL_USD, 4)
