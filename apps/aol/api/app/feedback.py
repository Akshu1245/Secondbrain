"""Module 6 — Feedback Loop.

Collect explicit user feedback on individual features (rating + optional
comment), produce machine-readable improvement suggestions for the next
optimisation cycle. Pure heuristic — no model.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from . import store

VALID_RATINGS = {"love", "ok", "annoying", "never_use"}


def submit(*, feature_id: str, rating: str, comment: str | None = None) -> dict[str, Any]:
    if rating not in VALID_RATINGS:
        raise ValueError(f"rating must be one of {sorted(VALID_RATINGS)}")
    state = store.get_state()
    if feature_id not in state["features"]:
        raise KeyError(feature_id)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "feature_id": feature_id,
        "rating": rating,
        "comment": (comment or "").strip()[:500] or None,
    }
    state["feedback"].insert(0, entry)
    state["feedback"] = state["feedback"][:1000]
    store.save()
    return entry


def all_entries(limit: int = 100) -> list[dict[str, Any]]:
    return store.get_state()["feedback"][:limit]


def suggestions() -> list[dict[str, Any]]:
    """Translate raw feedback + usage into actionable system-layer changes."""
    state = store.get_state()
    by_feat: dict[str, list[str]] = defaultdict(list)
    for f in state["feedback"]:
        by_feat[f["feature_id"]].append(f["rating"])

    out: list[dict[str, Any]] = []
    for fid, ratings in by_feat.items():
        bad = sum(1 for r in ratings if r in {"annoying", "never_use"})
        good = sum(1 for r in ratings if r == "love")
        feat = state["features"].get(fid)
        if not feat:
            continue
        if bad >= max(2, len(ratings) // 2):
            out.append(
                {
                    "feature_id": fid,
                    "name": feat["name"],
                    "action": "auto_disable_recommended",
                    "reason": f"{bad}/{len(ratings)} ratings are negative",
                }
            )
        elif good >= max(2, len(ratings) // 2) and not feat["enabled"]:
            out.append(
                {
                    "feature_id": fid,
                    "name": feat["name"],
                    "action": "auto_enable_recommended",
                    "reason": f"{good}/{len(ratings)} ratings are positive but feature is disabled",
                }
            )
    return out
