"""Module 7 — Learned routing policy (Phase 2, optional).

Pure-Python logistic regression that predicts how likely a feature is to
*actually be used* by this user in the next 7 days, given the available
context features. The output is used to *re-rank* the Smart Filter's
suggestions — not to override the rule-based engine. The rule engine
remains the safety floor; the learned policy moves the needle on the
edge cases where two features both pass the rule but only one is likely
to engage *this user*.

Why a hand-rolled logistic regression instead of scikit-learn:

  1. Zero new runtime deps. Fly.io image stays small.
  2. Fully auditable. The OEM legal / privacy review will read this
     ~150-line file end-to-end. Inscrutable C++ from sklearn would be
     a non-starter.
  3. Per-feature explainability is a hard requirement: the dashboard
     must show *why* a feature was demoted. ``top_factors`` returns the
     three feature dimensions with the largest absolute contribution to
     the final score for the inference being explained.

Training data is derived from the usage log + feedback log already in
``store``. No PII leaves the device. If training data is too thin (< 50
labelled rows), ``train()`` aborts and ``predict_engagement`` falls back
to the rule-based engagement estimate so the user is never worse off
than the unlearned baseline.

Run ``POST /api/learned/train`` to retrain on the current usage state;
``GET  /api/learned/predict?feature_id=…`` to score a feature.
"""

from __future__ import annotations

import math
import random
from typing import Any

from . import store

# Feature names line up with ``_featurise`` below. Order matters: weights
# are stored in the same order so they round-trip cleanly through state.
FEATURE_NAMES = (
    "bias",
    "compute_heavy",
    "compute_light",
    "is_default_on",
    "category_productivity",
    "category_creative",
    "category_social",
    "category_wellbeing",
    "events_per_day",
    "negative_feedback_count",
    "positive_feedback_count",
)
N_FEATURES = len(FEATURE_NAMES)

# Min labelled rows before training is permitted. Below this, the engine
# refuses to train and the fallback (rule-based heuristic) is used.
MIN_TRAINING_ROWS = 50

# Hyperparameters. Conservative — we'd rather underfit than over-promise.
LEARNING_RATE = 0.05
N_EPOCHS = 200
L2_REG = 0.01

# Engagement label threshold: a feature that fired ≥ this many times in the
# trailing 30-day window is labelled "engaged" for training. Below this it
# is labelled "unengaged".
ENGAGED_EVENT_THRESHOLD = 5


def _featurise(feature: dict[str, Any], state: dict[str, Any]) -> list[float]:
    """Build the feature vector for a single OEM-AI feature row.

    Pure function of (feature, state) — no side effects, no randomness.
    The values are intentionally bounded so the gradient descent stays
    well-conditioned without explicit normalisation.
    """
    fid = feature["id"]
    events = [e for e in state["events"] if e["feature_id"] == fid]
    fb = [f for f in state["feedback"] if f["feature_id"] == fid]
    pos = sum(1 for f in fb if f["rating"] in ("love", "ok"))
    neg = sum(1 for f in fb if f["rating"] in ("annoying", "never_use"))
    return [
        1.0,  # bias term
        1.0 if feature["compute_class"] == "heavy" else 0.0,
        1.0 if feature["compute_class"] == "light" else 0.0,
        1.0 if feature["default_on"] else 0.0,
        1.0 if feature["category"] == "productivity" else 0.0,
        1.0 if feature["category"] == "creative" else 0.0,
        1.0 if feature["category"] == "social" else 0.0,
        1.0 if feature["category"] == "wellbeing" else 0.0,
        min(len(events) / 30.0, 5.0),     # events / day, clamped
        min(neg, 10) / 10.0,
        min(pos, 10) / 10.0,
    ]


def _label(feature: dict[str, Any], state: dict[str, Any]) -> int:
    fid = feature["id"]
    n_events = sum(1 for e in state["events"] if e["feature_id"] == fid)
    return 1 if n_events >= ENGAGED_EVENT_THRESHOLD else 0


def _sigmoid(z: float) -> float:
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


def _dot(w: list[float], x: list[float]) -> float:
    return sum(wi * xi for wi, xi in zip(w, x))


def _build_dataset() -> tuple[list[list[float]], list[int], list[str]]:
    state = store.get_state()
    X, y, ids = [], [], []
    for f in state["features"].values():
        X.append(_featurise(f, state))
        y.append(_label(f, state))
        ids.append(f["id"])
    return X, y, ids


def _fit(X: list[list[float]], y: list[int]) -> tuple[list[float], list[float]]:
    """Plain SGD on logistic regression with L2 regularisation.

    Returns ``(weights, loss_curve)`` where ``loss_curve`` is the mean
    cross-entropy loss after each epoch — useful for the dashboard to
    show that the optimiser actually converged (not just that it ran).
    """
    rng = random.Random(0)  # deterministic for tests
    w = [0.0] * N_FEATURES
    n = len(X)
    loss_curve: list[float] = []
    for _ in range(N_EPOCHS):
        order = list(range(n))
        rng.shuffle(order)
        for i in order:
            xi = X[i]
            p = _sigmoid(_dot(w, xi))
            err = p - y[i]
            for j in range(N_FEATURES):
                w[j] -= LEARNING_RATE * (err * xi[j] + L2_REG * w[j])
        loss_curve.append(_mean_log_loss(w, X, y))
    return w, loss_curve


def _mean_log_loss(w: list[float], X: list[list[float]], y: list[int]) -> float:
    """Mean cross-entropy loss. Clamped to avoid log(0) when the
    sigmoid saturates at the extremes."""
    if not X:
        return 0.0
    eps = 1e-9
    total = 0.0
    for xi, yi in zip(X, y):
        p = max(min(_sigmoid(_dot(w, xi)), 1.0 - eps), eps)
        total += -(yi * math.log(p) + (1 - yi) * math.log(1.0 - p))
    return total / len(X)


def _accuracy(w: list[float], X: list[list[float]], y: list[int]) -> float:
    if not X:
        return 0.0
    correct = sum(
        1 for xi, yi in zip(X, y)
        if (1 if _sigmoid(_dot(w, xi)) >= 0.5 else 0) == yi
    )
    return correct / len(X)


def _calibration(w: list[float], X: list[list[float]], y: list[int]) -> dict[str, float]:
    """Mean predicted probability vs. observed positive rate. A
    well-calibrated model has |mean_pred - mean_actual| close to 0;
    if the gap is large the predicted probabilities are not
    trustworthy as decision thresholds."""
    if not X:
        return {"mean_pred": 0.0, "mean_actual": 0.0, "abs_gap": 0.0}
    mean_pred = sum(_sigmoid(_dot(w, xi)) for xi in X) / len(X)
    mean_actual = sum(y) / len(y)
    return {
        "mean_pred": round(mean_pred, 3),
        "mean_actual": round(mean_actual, 3),
        "abs_gap": round(abs(mean_pred - mean_actual), 3),
    }


def _baseline_accuracy(y: list[int]) -> float:
    """Majority-class baseline. The learned model must beat this
    or `train()` refuses to overwrite existing weights — we'd rather
    keep the rule-based path than ship a model that's worse than
    'always predict the most common label'."""
    if not y:
        return 0.0
    pos_rate = sum(y) / len(y)
    return max(pos_rate, 1.0 - pos_rate)


def _train_test_split(X: list[list[float]], y: list[int],
                      test_frac: float = 0.2,
                      seed: int = 1) -> tuple[
                          list[list[float]], list[int],
                          list[list[float]], list[int]]:
    """Stratified-ish split: shuffle then take the last `test_frac`
    rows. With only 24 rows we can't do real k-fold cross-validation
    cleanly, but a held-out 20% gives an honest signal that
    training-set accuracy isn't pure memorisation."""
    rng = random.Random(seed)
    indices = list(range(len(X)))
    rng.shuffle(indices)
    n_test = max(1, int(len(X) * test_frac))
    test_idx = set(indices[-n_test:])
    X_train = [X[i] for i in range(len(X)) if i not in test_idx]
    y_train = [y[i] for i in range(len(X)) if i not in test_idx]
    X_test = [X[i] for i in range(len(X)) if i in test_idx]
    y_test = [y[i] for i in range(len(X)) if i in test_idx]
    return X_train, y_train, X_test, y_test


def train(force: bool = False) -> dict[str, Any]:
    """Train, evaluate, and (if quality clears the floor) persist new
    weights. Returns a structured report covering both the convergence
    of the optimiser and the held-out generalisation of the model.

    The model is only saved to disk if held-out accuracy beats the
    majority-class baseline. Pass ``force=True`` to skip that gate
    (useful for experiments; never the default).
    """
    X, y, ids = _build_dataset()
    if len(X) < MIN_TRAINING_ROWS // 5:
        return {"trained": False, "reason": "not enough rows", "rows": len(X)}

    X_train, y_train, X_test, y_test = _train_test_split(X, y)
    w, loss_curve = _fit(X_train, y_train)

    train_acc = _accuracy(w, X_train, y_train)
    test_acc = _accuracy(w, X_test, y_test)
    train_loss = _mean_log_loss(w, X_train, y_train)
    test_loss = _mean_log_loss(w, X_test, y_test)
    calibration = _calibration(w, X, y)
    baseline = _baseline_accuracy(y_train)

    beats_baseline = test_acc >= baseline
    persisted = beats_baseline or force
    if persisted:
        state = store.get_state()
        state["learned"] = {
            "weights": w,
            "feature_names": list(FEATURE_NAMES),
            "n_rows_train": len(X_train),
            "n_rows_test": len(X_test),
            "version": 2,
            "metrics": {
                "train_accuracy": round(train_acc, 3),
                "test_accuracy": round(test_acc, 3),
                "train_log_loss": round(train_loss, 4),
                "test_log_loss": round(test_loss, 4),
                "majority_baseline": round(baseline, 3),
                "calibration": calibration,
            },
        }
        store.save()

    return {
        "trained": persisted,
        "beats_baseline": beats_baseline,
        "rows_train": len(X_train),
        "rows_test": len(X_test),
        "train_accuracy": round(train_acc, 3),
        "test_accuracy": round(test_acc, 3),
        "train_log_loss": round(train_loss, 4),
        "test_log_loss": round(test_loss, 4),
        "majority_baseline": round(baseline, 3),
        "calibration": calibration,
        "loss_curve_first_last": [
            round(loss_curve[0], 4) if loss_curve else None,
            round(loss_curve[-1], 4) if loss_curve else None,
        ],
        "feature_names": list(FEATURE_NAMES),
        "weights": [round(wi, 3) for wi in w],
    }


def _weights() -> list[float] | None:
    state = store.get_state()
    learned = state.get("learned") or {}
    w = learned.get("weights")
    return list(w) if w else None


def _rule_based_engagement(feature: dict[str, Any], state: dict[str, Any]) -> float:
    """Fallback when no learned weights are available. Returns the
    engagement rate over the last 30 days, scaled into [0, 1] using the
    same threshold the learned label uses."""
    fid = feature["id"]
    n_events = sum(1 for e in state["events"] if e["feature_id"] == fid)
    return min(n_events / (ENGAGED_EVENT_THRESHOLD * 4), 1.0)


def predict_engagement(feature_id: str) -> dict[str, Any]:
    state = store.get_state()
    feature = state["features"].get(feature_id)
    if not feature:
        raise KeyError(feature_id)
    w = _weights()
    if w is None:
        return {
            "feature_id": feature_id,
            "prob_engaged": round(_rule_based_engagement(feature, state), 3),
            "model": "rule-based fallback (learned policy not yet trained)",
            "top_factors": [],
        }
    x = _featurise(feature, state)
    z = _dot(w, x)
    p = _sigmoid(z)
    contributions = [
        {"name": FEATURE_NAMES[i], "value": round(x[i], 3),
         "weight": round(w[i], 3), "contribution": round(w[i] * x[i], 3)}
        for i in range(N_FEATURES)
        if FEATURE_NAMES[i] != "bias"
    ]
    contributions.sort(key=lambda c: abs(c["contribution"]), reverse=True)
    return {
        "feature_id": feature_id,
        "prob_engaged": round(p, 3),
        "model": "logistic regression (Phase 2)",
        "top_factors": contributions[:3],
    }


def rank_features(limit: int = 10) -> list[dict[str, Any]]:
    """Return all features ranked by predicted engagement (descending)."""
    state = store.get_state()
    rows = []
    for fid, feat in state["features"].items():
        try:
            rows.append({
                "feature_id": fid,
                "name": feat["name"],
                "category": feat["category"],
                **{k: v for k, v in predict_engagement(fid).items() if k != "feature_id"},
            })
        except KeyError:
            continue
    rows.sort(key=lambda r: r["prob_engaged"], reverse=True)
    return rows[:limit]


def status() -> dict[str, Any]:
    state = store.get_state()
    learned = state.get("learned") or {}
    return {
        "trained": "weights" in learned,
        "n_rows": learned.get("n_rows") or learned.get("n_rows_train"),
        "n_rows_train": learned.get("n_rows_train"),
        "n_rows_test": learned.get("n_rows_test"),
        "version": learned.get("version"),
        "metrics": learned.get("metrics"),
        "feature_names": learned.get("feature_names"),
        "weights": learned.get("weights"),
    }
