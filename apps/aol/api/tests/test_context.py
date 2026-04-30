"""Tests for the context-aware engine (Module 3)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app import context, filter as feature_filter, store


@pytest.mark.parametrize(
    "hour,bucket",
    [
        (4,  "night"),
        (5,  "morning"),
        (10, "morning"),
        (11, "midday"),
        (15, "midday"),
        (16, "evening"),
        (20, "evening"),
        (21, "night"),
        (23, "night"),
    ],
)
def test_bucket_for_hour_boundaries(hour: int, bucket: str):
    now = datetime(2026, 4, 30, hour, 0, tzinfo=timezone.utc)
    assert context._bucket_for(now) == bucket


def test_explicit_time_of_day_and_activity_pick_the_matching_rule():
    out = context.suggest(time_of_day="morning", activity="commute")
    ids = [s["id"] for s in out["suggestions"]]
    assert ids == ["morning_briefing", "navigation_hint", "spam_call_filter"]
    for s in out["suggestions"]:
        assert "morning + commute" in s["reason"]


def test_unknown_context_falls_back_to_default():
    out = context.suggest(time_of_day="morning", activity="completely_made_up")
    ids = [s["id"] for s in out["suggestions"]]
    # Default rule (smart_reply / screenshot_text / spam_call_filter).
    assert "smart_reply" in ids


def test_battery_saver_drops_heavy_compute_suggestions():
    feature_filter.set_prefs(battery_saver=True)
    # Pick a context whose rule includes a heavy-class feature.
    state = store.get_state()
    # Build a rule on the fly: stuff a heavy feature into the morning_commute slot.
    from app import context as ctx_mod

    original = dict(ctx_mod._RULES)
    ctx_mod._RULES[("morning", "commute")] = ["live_translate", "smart_reply"]
    try:
        out = ctx_mod.suggest(time_of_day="morning", activity="commute")
        ids = [s["id"] for s in out["suggestions"]]
        assert "live_translate" not in ids   # heavy → suppressed
        assert "smart_reply" in ids          # light → kept
    finally:
        ctx_mod._RULES.clear()
        ctx_mod._RULES.update(original)


def test_disabled_features_are_excluded_from_suggestions():
    feature_filter.toggle("morning_briefing", enabled=False)
    out = context.suggest(time_of_day="morning", activity="commute")
    ids = [s["id"] for s in out["suggestions"]]
    assert "morning_briefing" not in ids
