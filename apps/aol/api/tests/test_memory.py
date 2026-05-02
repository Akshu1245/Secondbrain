"""Tests for the Second Brain × AOL memory-informed feedback module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app import feedback, memory, store
from app import filter as feature_filter


def _pick_feature() -> str:
    state = store.get_state()
    return next(iter(state["features"]))


def test_recall_returns_empty_snapshot_when_no_events(_reset):
    fid = _pick_feature()
    snap = memory.recall(fid)
    assert snap["feature_id"] == fid
    assert snap["disable_count"] == 0
    assert snap["negative_ratings"] == 0
    assert snap["positive_ratings"] == 0
    assert snap["disables"] == []


def test_recall_raises_on_unknown_feature(_reset):
    try:
        memory.recall("no-such-feature")
    except KeyError:
        return
    raise AssertionError("expected KeyError for unknown feature id")


def test_toggle_off_is_written_to_memory_log(_reset):
    fid = _pick_feature()
    feature_filter.toggle(fid, False)
    feature_filter.toggle(fid, False)

    snap = memory.recall(fid)
    assert snap["disable_count"] == 2
    # toggle-on should NOT count as a disable.
    feature_filter.toggle(fid, True)
    assert memory.recall(fid)["disable_count"] == 2


def test_recall_window_filters_old_episodes(_reset):
    """Episodes older than the window must be excluded."""
    fid = _pick_feature()
    state = store.get_state()
    state.setdefault("toggle_log", []).extend([
        {
            "ts": (datetime.now(timezone.utc) - timedelta(days=120)).isoformat(),
            "feature_id": fid,
            "enabled": False,
        },
        {
            "ts": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
            "feature_id": fid,
            "enabled": False,
        },
    ])
    assert memory.recall(fid, days=90)["disable_count"] == 1
    assert memory.recall(fid, days=180)["disable_count"] == 2


def test_memory_suggestions_require_durable_evidence(_reset):
    """A single disable must NOT produce an auto-hide recommendation —
    the whole point of the memory layer is to avoid flapping on one bad
    interaction."""
    fid = _pick_feature()
    feature_filter.toggle(fid, False)

    out = memory.memory_suggestions()
    assert all(s["feature_id"] != fid for s in out), (
        "single disable should not trigger auto-hide; got "
        f"{[s for s in out if s['feature_id'] == fid]}"
    )


def test_memory_suggestions_fire_on_repeated_disables(_reset):
    fid = _pick_feature()
    feature_filter.toggle(fid, False)
    feature_filter.toggle(fid, True)
    feature_filter.toggle(fid, False)

    out = memory.memory_suggestions()
    rec = next((s for s in out if s["feature_id"] == fid), None)
    assert rec is not None, f"expected memory suggestion for {fid}; got {out}"
    assert rec["action"] == "auto_hide_durable"
    assert rec["signals"]["disable_count"] >= 2
    assert any("disabled" in e for e in rec["evidence"])


def test_memory_suggestion_confidence_is_high_with_two_signals(_reset):
    """Disables + negative ratings = high-confidence recommendation."""
    fid = _pick_feature()
    feature_filter.toggle(fid, False)
    feature_filter.toggle(fid, False)
    feedback.submit(feature_id=fid, rating="annoying")
    feedback.submit(feature_id=fid, rating="never_use")

    out = memory.memory_suggestions()
    rec = next((s for s in out if s["feature_id"] == fid), None)
    assert rec is not None
    assert rec["confidence"] == "high"
    assert len(rec["evidence"]) == 2


def test_memory_suggestions_never_contradict_positive_ratings(_reset):
    """A feature with 3 'love' ratings and no disables must not be
    recommended for auto-hide."""
    fid = _pick_feature()
    feedback.submit(feature_id=fid, rating="love")
    feedback.submit(feature_id=fid, rating="love")
    feedback.submit(feature_id=fid, rating="love")

    out = memory.memory_suggestions()
    assert all(s["feature_id"] != fid for s in out)


def test_feedback_list_endpoint_shape_includes_memory_suggestions(client, _reset):
    fid = _pick_feature()
    feature_filter.toggle(fid, False)
    feature_filter.toggle(fid, False)

    r = client.get("/api/feedback")
    assert r.status_code == 200
    data = r.json()
    assert "memory_suggestions" in data
    ids = [s["feature_id"] for s in data["memory_suggestions"]]
    assert fid in ids


def test_memory_recall_endpoint_404s_on_unknown_feature(client, _reset):
    r = client.get("/api/memory/recall", params={"feature_id": "bogus"})
    assert r.status_code == 404


def test_memory_recall_endpoint_returns_snapshot(client, _reset):
    fid = _pick_feature()
    feature_filter.toggle(fid, False)
    r = client.get("/api/memory/recall", params={"feature_id": fid, "days": 30})
    assert r.status_code == 200
    snap = r.json()
    assert snap["feature_id"] == fid
    assert snap["window_days"] == 30
    assert snap["disable_count"] == 1
