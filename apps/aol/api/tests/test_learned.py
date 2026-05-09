"""Tests for the learned engagement-prediction policy (Module 7).

The learned policy is intentionally Phase-2 / optional: untrained, the
system MUST fall back to the rule-based engagement estimate so the user
is never worse off than the unlearned baseline. These tests pin the
falls-back-cleanly behaviour as well as the trains-on-current-state
behaviour.
"""

from __future__ import annotations

import math

from app import learned, usage


def test_predict_falls_back_to_rule_based_when_untrained():
    out = learned.predict_engagement("smart_reply")
    assert "rule-based fallback" in out["model"]
    assert 0.0 <= out["prob_engaged"] <= 1.0
    assert out["top_factors"] == []


def test_predict_unknown_feature_raises_keyerror():
    import pytest

    with pytest.raises(KeyError):
        learned.predict_engagement("not_a_real_feature")


def test_train_on_simulated_state_produces_valid_weights():
    usage.simulate(days=30)
    result = learned.train()
    assert result["trained"] is True
    assert result["rows"] >= 24                           # 24 features in seed
    assert len(result["weights"]) == len(learned.FEATURE_NAMES)
    # Training accuracy on this small dataset must be > 50% — the model is
    # intentionally simple, but if it can't beat coin-flip on the same data
    # it trained on, something is wrong.
    assert result["training_accuracy"] >= 0.6


def test_predict_after_training_returns_explainable_factors():
    usage.simulate(days=30)
    learned.train()
    out = learned.predict_engagement("smart_reply")
    assert "logistic regression" in out["model"]
    assert 0.0 <= out["prob_engaged"] <= 1.0
    assert len(out["top_factors"]) == 3
    for factor in out["top_factors"]:
        assert {"name", "value", "weight", "contribution"} <= factor.keys()
    # Top factors are sorted by absolute contribution.
    contribs = [abs(f["contribution"]) for f in out["top_factors"]]
    assert contribs == sorted(contribs, reverse=True)


def test_status_reports_trained_state():
    assert learned.status()["trained"] is False
    usage.simulate(days=30)
    learned.train()
    s = learned.status()
    assert s["trained"] is True
    assert s["n_rows"] >= 24
    assert s["version"] == 1


def test_rank_features_returns_descending_probabilities():
    usage.simulate(days=30)
    learned.train()
    ranked = learned.rank_features(limit=24)
    assert len(ranked) == 24
    probs = [r["prob_engaged"] for r in ranked]
    assert probs == sorted(probs, reverse=True)


def test_predict_is_deterministic_after_training():
    usage.simulate(days=30)
    r1 = learned.train()
    r2 = learned.train()
    # Same dataset, same RNG seed → identical weights.
    assert r1["weights"] == r2["weights"]


def test_sigmoid_handles_extreme_inputs_without_overflow():
    # _sigmoid is module-private but tested here so the underflow guard
    # doesn't silently regress (negative-z branch).
    assert math.isclose(learned._sigmoid(0.0), 0.5)
    # Negative-z branch must underflow to 0.0, not raise OverflowError.
    assert learned._sigmoid(-1000.0) == 0.0
    # Positive-z branch must saturate to 1.0, not raise OverflowError.
    assert learned._sigmoid(1000.0) == 1.0


def test_endpoint_train_predict_round_trip(client):
    # Untrained: endpoint reports rule-based fallback.
    r = client.get("/api/learned/predict?feature_id=smart_reply")
    assert r.status_code == 200
    assert "rule-based fallback" in r.json()["model"]

    # Train.
    r = client.post("/api/learned/train")
    assert r.status_code == 200
    body = r.json()
    assert body["trained"] is True

    # Trained: top_factors populated.
    r = client.get("/api/learned/predict?feature_id=smart_reply")
    body = r.json()
    assert "logistic regression" in body["model"]
    assert len(body["top_factors"]) == 3

    # Rank endpoint returns 10 by default.
    r = client.get("/api/learned/rank")
    assert len(r.json()["ranked"]) == 10
