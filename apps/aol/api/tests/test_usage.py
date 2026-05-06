"""Tests for the usage tracker (Module 1)."""

from __future__ import annotations

from app import store, usage


def test_simulate_is_deterministic_for_a_fixed_seed():
    a = usage.simulate(days=30, seed=42)
    counts_a = {r["id"]: r["events"] for r in a["all"]}

    store.reset()

    b = usage.simulate(days=30, seed=42)
    counts_b = {r["id"]: r["events"] for r in b["all"]}

    assert counts_a == counts_b


def test_simulate_clears_existing_events_before_replaying():
    usage.simulate(days=30, seed=1)
    first_total = sum(r["events"] for r in usage.summarise()["all"])

    usage.simulate(days=30, seed=1)
    second_total = sum(r["events"] for r in usage.summarise()["all"])

    assert first_total == second_total


def test_record_appends_a_single_event():
    state = store.get_state()
    starting = len(state["events"])
    usage.record(
        "smart_reply", success=True, time_of_day="midday", activity="work"
    )
    assert len(state["events"]) == starting + 1
    last = state["events"][-1]
    assert last["feature_id"] == "smart_reply"
    assert last["success"] is True
    assert last["time_of_day"] == "midday"


def test_summarise_share_pct_sums_to_about_100():
    usage.simulate(days=30, seed=7)
    rows = usage.summarise()["all"]
    total = sum(r["share_pct"] for r in rows)
    # Floating-point round() can drift; allow a small tolerance.
    assert abs(total - 100.0) < 0.5


def test_summarise_orders_descending_by_event_count():
    usage.simulate(days=30, seed=7)
    rows = usage.summarise()["all"]
    counts = [r["events"] for r in rows]
    assert counts == sorted(counts, reverse=True)
