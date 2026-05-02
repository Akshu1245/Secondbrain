"""AOL × Second Brain — memory-informed feedback loop.

The **Second Brain** companion product (`apps/api/`, shipped in PRs #1–#3)
stores episodic memory of everything the user has done on-device: feature
disables, explicit feedback, contextual hides, outcome successes. This
module is the **AOL-side contract** for that memory: the functions below
describe the recall shape AOL needs; in production they proxy to the
Second Brain MCP server (`/recall?feature_id=...&days=90`).

For this demo the implementation is **local** (same JSON store that backs
AOL itself) so the integration story runs end-to-end without spinning up
a second service. Replacing the bodies of `_recall_disables`,
`_recall_ratings` and `_recall_context_hides` with HTTP calls against the
Second Brain MCP server is the only change required for production.

The memory-informed suggestions are strictly **stronger** than the raw
feedback-only suggestions — they never contradict them, they just provide
extra evidence (e.g. "disabled 3 times in last 90 days across 2 different
contexts") that an OEM Control Panel can surface as a high-confidence
"auto-hide this?" prompt.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from . import store

DEFAULT_WINDOW_DAYS = 90
MIN_DISABLES_FOR_AUTOHIDE = 2
MIN_NEGATIVE_RATINGS_FOR_AUTOHIDE = 2


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _cutoff(days: int) -> datetime:
    return _now() - timedelta(days=days)


def _parse_ts(s: str) -> datetime | None:
    try:
        ts = datetime.fromisoformat(s)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except (ValueError, TypeError):
        return None


# ── Recall primitives ───────────────────────────────────────────────────
# These are the three calls that, in production, hit the Second Brain MCP
# server. For the demo they read the same local state the rest of AOL
# writes to.


def _recall_disables(feature_id: str, *, days: int) -> list[dict[str, Any]]:
    """Episodes where the user explicitly toggled this feature OFF."""
    cut = _cutoff(days)
    state = store.get_state()
    out: list[dict[str, Any]] = []
    for ev in state.get("toggle_log", []):
        if ev.get("feature_id") != feature_id:
            continue
        if ev.get("enabled") is not False:
            continue
        ts = _parse_ts(ev.get("ts", ""))
        if ts is None or ts < cut:
            continue
        out.append(ev)
    return out


def _recall_ratings(feature_id: str, *, days: int) -> list[dict[str, Any]]:
    """Explicit feedback ratings for this feature, newest first."""
    cut = _cutoff(days)
    state = store.get_state()
    out: list[dict[str, Any]] = []
    for ev in state.get("feedback", []):
        if ev.get("feature_id") != feature_id:
            continue
        ts = _parse_ts(ev.get("ts", ""))
        if ts is None or ts < cut:
            continue
        out.append(ev)
    return out


def _recall_context_hides(feature_id: str, *, days: int) -> list[dict[str, Any]]:
    """Contexts in which AOL auto-hid this feature (Module 3 + Module 2).

    In production these are written to SB as ``hide`` episodes whenever
    ``filterSurface`` excludes a feature. For the demo we just consult the
    compute_log — features that the user never invoked when they *were*
    visible can be inferred as low-value in that context.
    """
    cut = _cutoff(days)
    state = store.get_state()
    out: list[dict[str, Any]] = []
    for ev in state.get("compute_log", []):
        if ev.get("feature_id") != feature_id and ev.get("feature_name") != feature_id:
            continue
        ts = _parse_ts(ev.get("ts", ""))
        if ts is None or ts < cut:
            continue
        out.append(ev)
    return out


# ── Public API ──────────────────────────────────────────────────────────


def recall(feature_id: str, *, days: int = DEFAULT_WINDOW_DAYS) -> dict[str, Any]:
    """Return the Second Brain memory snapshot for a single feature.

    Shape matches the SB MCP server's ``/recall`` response so the OEM
    Control Panel can render it unchanged whether the data came from AOL's
    local mock or a real SB backend.
    """
    state = store.get_state()
    if feature_id not in state["features"]:
        raise KeyError(feature_id)

    disables = _recall_disables(feature_id, days=days)
    ratings = _recall_ratings(feature_id, days=days)
    context_hides = _recall_context_hides(feature_id, days=days)

    rating_counts = Counter(r["rating"] for r in ratings)
    negative = rating_counts.get("annoying", 0) + rating_counts.get("never_use", 0)
    positive = rating_counts.get("love", 0)

    return {
        "feature_id": feature_id,
        "window_days": days,
        "disable_count": len(disables),
        "rating_counts": dict(rating_counts),
        "negative_ratings": negative,
        "positive_ratings": positive,
        "context_hide_count": len(context_hides),
        "disables": disables[-5:],
        "ratings": ratings[:5],
    }


def memory_suggestions(*, days: int = DEFAULT_WINDOW_DAYS) -> list[dict[str, Any]]:
    """Produce memory-informed recommendations for the Control Panel.

    Combines three signals per feature: repeated toggle-offs, repeated
    negative feedback, and context hides. A feature surfaces here only if
    the pattern is **durable** — at least two events spread over time —
    so the Control Panel never ships a "auto-hide this?" prompt on a
    single bad interaction.
    """
    state = store.get_state()
    out: list[dict[str, Any]] = []
    for fid, feat in state["features"].items():
        snap = recall(fid, days=days)
        reasons: list[str] = []
        if snap["disable_count"] >= MIN_DISABLES_FOR_AUTOHIDE:
            reasons.append(
                f"disabled {snap['disable_count']}× in last {days}d"
            )
        if snap["negative_ratings"] >= MIN_NEGATIVE_RATINGS_FOR_AUTOHIDE:
            reasons.append(
                f"{snap['negative_ratings']} negative ratings "
                f"(love: {snap['positive_ratings']})"
            )
        if not reasons:
            continue
        confidence = "high" if len(reasons) > 1 else "medium"
        out.append(
            {
                "feature_id": fid,
                "name": feat["name"],
                "action": "auto_hide_durable",
                "confidence": confidence,
                "evidence": reasons,
                "window_days": days,
                "signals": {
                    "disable_count": snap["disable_count"],
                    "negative_ratings": snap["negative_ratings"],
                    "positive_ratings": snap["positive_ratings"],
                },
            }
        )
    out.sort(key=lambda r: (r["confidence"] != "high", -len(r["evidence"])))
    return out


def record_toggle(feature_id: str, *, enabled: bool) -> None:
    """Append a toggle event to the memory log.

    Called by ``filter.toggle`` so every on/off the user makes becomes a
    future recall episode — this is what feeds `memory_suggestions`.
    """
    state = store.get_state()
    state.setdefault("toggle_log", []).append(
        {
            "ts": _now().isoformat(),
            "feature_id": feature_id,
            "enabled": bool(enabled),
        }
    )
    state["toggle_log"] = state["toggle_log"][-2000:]
