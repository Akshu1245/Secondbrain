"""Tests for the JSON state store."""

from __future__ import annotations

from app import store


def test_bootstrap_seeds_features_and_user_prefs():
    state = store.get_state()
    assert len(state["features"]) == 24
    # Every feature has the runtime keys we expect.
    sample = next(iter(state["features"].values()))
    for key in ("name", "category", "compute_class", "ms_local", "ms_cloud",
                "default_on", "enabled"):
        assert key in sample
    # `enabled` mirrors `default_on` on a fresh bootstrap.
    for f in state["features"].values():
        assert f["enabled"] == f["default_on"]


def test_save_and_reload_round_trip():
    state = store.get_state()
    state["features"]["smart_reply"]["enabled"] = False
    store.save()

    # Force a re-read from disk by clearing the in-memory cache.
    store._state = None  # type: ignore[attr-defined]
    fresh = store.get_state()
    assert fresh["features"]["smart_reply"]["enabled"] is False


def test_reset_wipes_runtime_changes():
    state = store.get_state()
    state["events"].append({"hello": "world"})
    state["features"]["smart_reply"]["enabled"] = False

    store.reset()

    state = store.get_state()
    assert state["events"] == []
    assert state["features"]["smart_reply"]["enabled"] is True
