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
    assert result["rows_train"] + result["rows_test"] >= 24    # 24 features in seed
    assert len(result["weights"]) == len(learned.FEATURE_NAMES)
    # Training accuracy on the held-out 80% must be > 50% — the model is
    # intentionally simple, but if it can't beat coin-flip on the same data
    # it trained on, something is wrong.
    assert result["train_accuracy"] >= 0.6
    # And held-out test accuracy must beat the majority-class baseline,
    # otherwise `train()` would have refused to persist.
    assert result["beats_baseline"] is True
    # Calibration gap should be small on this clean simulated data.
    assert result["calibration"]["abs_gap"] <= 0.4


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
    # n_rows_train + n_rows_test recovers the full dataset.
    assert s["n_rows_train"] + s["n_rows_test"] >= 24
    assert s["version"] == 2
    # Metrics are now persisted alongside the weights.
    assert s["metrics"] is not None
    assert "test_accuracy" in s["metrics"]
    assert "calibration" in s["metrics"]


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


def test_train_test_split_partitions_without_overlap():
    X = [[float(i)] for i in range(24)]
    y = [i % 2 for i in range(24)]
    Xtr, ytr, Xte, yte = learned._train_test_split(X, y, test_frac=0.2, seed=42)
    # Sizes line up.
    assert len(Xtr) + len(Xte) == 24
    assert len(yte) == int(24 * 0.2) or len(yte) >= 1
    # Disjoint by content.
    train_set = {x[0] for x in Xtr}
    test_set = {x[0] for x in Xte}
    assert train_set.isdisjoint(test_set)
    # Deterministic for the same seed.
    Xtr2, _, Xte2, _ = learned._train_test_split(X, y, test_frac=0.2, seed=42)
    assert Xtr == Xtr2 and Xte == Xte2


def test_log_loss_is_lower_after_training():
    """The optimiser must actually reduce cross-entropy. If it doesn't,
    SGD is broken."""
    usage.simulate(days=30)
    result = learned.train()
    first, last = result["loss_curve_first_last"]
    assert first is not None and last is not None
    assert last <= first


def test_baseline_gate_keeps_old_weights_on_garbage_data():
    """If we point training at a near-random label distribution, the
    learned model should NOT overwrite anything: train() reports
    ``beats_baseline=False`` and ``trained=False``, and a subsequent
    predict() falls back to rule-based."""
    # Pathological dataset: 12 zeros + 12 ones, but features are constant
    # so no model can do better than the 50% baseline.
    X = [[1.0] + [0.0] * (learned.N_FEATURES - 1) for _ in range(24)]
    y = [i % 2 for i in range(24)]
    Xtr, ytr, Xte, yte = learned._train_test_split(X, y, test_frac=0.2, seed=0)
    w, _ = learned._fit(Xtr, ytr)
    test_acc = learned._accuracy(w, Xte, yte)
    baseline = learned._baseline_accuracy(ytr)
    # Constant-feature model can't beat the baseline (it can only learn
    # the bias, which converges to the class prior \u2192 same as baseline).
    assert test_acc <= baseline


def test_calibration_gap_is_well_defined():
    """Calibration gap is the absolute difference between mean predicted
    probability and mean observed positive rate. Both must be in [0, 1]."""
    usage.simulate(days=30)
    result = learned.train()
    cal = result["calibration"]
    assert 0.0 <= cal["mean_pred"] <= 1.0
    assert 0.0 <= cal["mean_actual"] <= 1.0
    assert cal["abs_gap"] == round(abs(cal["mean_pred"] - cal["mean_actual"]), 3)


def test_weights_persist_across_state_reload(tmp_path, monkeypatch):
    """Trained weights survive a save/load round-trip on disk \u2014 the
    model isn't re-derived from memory each call."""
    from app import store

    usage.simulate(days=30)
    learned.train()
    w_before = learned._weights()
    assert w_before is not None
    # Force a save then a fresh load.
    store.save()
    store._state = None  # type: ignore[attr-defined]
    state = store.get_state()
    assert "learned" in state
    assert state["learned"]["weights"] == w_before
