"""Tests for the smart feature filter (Module 2)."""

from __future__ import annotations

import pytest

from app import filter as feature_filter
from app import store, usage


def test_low_usage_features_outside_priority_categories_are_hidden():
    usage.simulate(days=30, seed=42)
    out = feature_filter.optimised_surface()
    visible_ids = {r["id"] for r in out["visible"]}
    hide_ids = {r["id"] for r in out["hide_recommended"]}
    # Features with 0–2 events that aren't in a priority category should hide.
    for r in out["hide_recommended"]:
        assert r["events"] < feature_filter.LOW_USAGE_THRESHOLD
        prio = set(store.get_state()["user_prefs"]["priority_categories"])
        assert r["category"] not in prio
    # No id should appear in both lists.
    assert visible_ids.isdisjoint(hide_ids)


def test_user_disabled_features_never_appear_in_visible_or_hidden():
    feature_filter.toggle("smart_reply", enabled=False)
    out = feature_filter.optimised_surface()
    assert "smart_reply" not in {r["id"] for r in out["visible"]}
    assert "smart_reply" not in {r["id"] for r in out["hide_recommended"]}
    assert "smart_reply" in {r["id"] for r in out["user_disabled"]}


def test_priority_category_features_are_kept_visible_even_at_low_usage():
    # Force priority to a single category that has a low-usage member, then
    # explicitly enable that feature so it isn't excluded by the disabled rule.
    feature_filter.set_prefs(priority_categories=["wellbeing"])
    feature_filter.toggle("focus_mode", enabled=True)
    usage.simulate(days=30, seed=42)
    out = feature_filter.optimised_surface()
    # focus_mode is wellbeing; even if events < threshold it should be visible.
    visible_ids = {r["id"] for r in out["visible"]}
    assert "focus_mode" in visible_ids


def test_visible_ordering_priority_first_then_by_events_desc():
    feature_filter.set_prefs(priority_categories=["productivity", "messaging"])
    usage.simulate(days=30, seed=42)
    out = feature_filter.optimised_surface()
    visible = out["visible"]
    state = store.get_state()
    prio = set(state["user_prefs"]["priority_categories"])
    # All priority-category visibles come before any non-priority visible.
    seen_non_prio = False
    for r in visible:
        if r["category"] not in prio:
            seen_non_prio = True
        elif seen_non_prio:
            pytest.fail("priority feature appeared after a non-priority feature")
    # Within the same priority bucket, events count is descending.
    prio_events = [r["events"] for r in visible if r["category"] in prio]
    assert prio_events == sorted(prio_events, reverse=True)


def test_toggle_unknown_feature_raises_keyerror():
    with pytest.raises(KeyError):
        feature_filter.toggle("definitely_not_a_real_feature", enabled=False)


def test_set_prefs_dedupes_priority_categories_and_preserves_order():
    out = feature_filter.set_prefs(
        priority_categories=["calls", "messaging", "calls", "productivity", "messaging"]
    )
    assert out["priority_categories"] == ["calls", "messaging", "productivity"]
