"""Tests for the feedback loop (Module 6)."""

from __future__ import annotations

import pytest

from app import feedback, filter as feature_filter


def test_submit_records_a_feedback_entry():
    out = feedback.submit(feature_id="smart_reply", rating="love",
                          comment="great")
    assert out["feature_id"] == "smart_reply"
    assert out["rating"] == "love"
    assert out["comment"] == "great"
    assert feedback.all_entries()[0]["feature_id"] == "smart_reply"


def test_submit_rejects_invalid_rating():
    with pytest.raises(ValueError):
        feedback.submit(feature_id="smart_reply", rating="thumbs_up")


def test_submit_rejects_unknown_feature():
    with pytest.raises(KeyError):
        feedback.submit(feature_id="ghost_feature", rating="love")


def test_long_comments_are_trimmed_to_500_chars():
    long = "x" * 800
    out = feedback.submit(feature_id="smart_reply", rating="ok", comment=long)
    assert out["comment"] is not None
    assert len(out["comment"]) == 500


def test_blank_comment_is_normalised_to_none():
    out = feedback.submit(feature_id="smart_reply", rating="ok", comment="   ")
    assert out["comment"] is None


def test_majority_negative_feedback_yields_disable_suggestion():
    for _ in range(3):
        feedback.submit(feature_id="ai_storymaker", rating="annoying")
    suggestions = feedback.suggestions()
    actions = {(s["feature_id"], s["action"]) for s in suggestions}
    assert ("ai_storymaker", "auto_disable_recommended") in actions


def test_majority_positive_for_disabled_feature_yields_enable_suggestion():
    feature_filter.toggle("magic_eraser", enabled=False)
    for _ in range(3):
        feedback.submit(feature_id="magic_eraser", rating="love")
    suggestions = feedback.suggestions()
    actions = {(s["feature_id"], s["action"]) for s in suggestions}
    assert ("magic_eraser", "auto_enable_recommended") in actions


def test_no_feedback_yields_no_suggestions():
    assert feedback.suggestions() == []
