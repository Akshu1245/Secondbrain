"""Module 1 — Feature Usage Tracker.

Records every (user, feature, context, success) event and aggregates them so
the rest of the layer can ask "which features actually matter to this user".
"""

from __future__ import annotations

import random
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from . import store

# Realistic usage shape: a few features dominate, a long tail is forgotten.
# These weights drive the simulator AND validate the filter.
_USAGE_WEIGHTS = {
    "smart_reply":          120,
    "screenshot_text":       95,
    "spam_call_filter":      70,
    "morning_briefing":      55,
    "circle_to_search":      48,
    "live_caption":          42,
    "note_summary":          38,
    "smart_calendar":        30,
    "navigation_hint":       28,
    "battery_advisor":       18,
    "magic_eraser":          14,
    "ai_translate_camera":   12,
    "live_translate":        10,
    "voice_recorder_summary": 8,
    "call_screening":         7,
    "generative_fill":        4,
    "expression_meme":        2,
    "wallpaper_studio":       2,
    "auto_wallpaper_swap":    1,
    "emoji_kitchen":          1,
    "ai_music_remix":         0,
    "sleep_sound_gen":        0,
    "ai_storymaker":          0,
    "focus_mode":             3,
}

_CONTEXTS = [
    ("morning",   ["commute",   "exercise"]),
    ("midday",    ["work",      "meeting"]),
    ("evening",   ["leisure",   "errands"]),
    ("night",     ["winddown",  "sleeping"]),
]


def simulate(days: int = 30, seed: int = 42) -> dict[str, Any]:
    """Replay `days` worth of synthetic usage events into the store.

    Used by the demo's "Generate sample data" button and at first-run if the
    store has no events yet. Idempotent against `store.reset()`.
    """
    state = store.get_state()
    state["events"].clear()
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    feature_ids = list(state["features"].keys())
    weights = [_USAGE_WEIGHTS.get(fid, 0) + 1 for fid in feature_ids]
    for _ in range(int(sum(weights) * days / 30)):
        fid = rng.choices(feature_ids, weights=weights, k=1)[0]
        delta = rng.uniform(0, days)
        ts = now - timedelta(days=delta)
        bucket, activities = rng.choices(_CONTEXTS, weights=[3, 4, 3, 2])[0]
        state["events"].append(
            {
                "ts": ts.isoformat(),
                "feature_id": fid,
                "success": rng.random() > 0.05,
                "time_of_day": bucket,
                "activity": rng.choice(activities),
            }
        )
    state["events"].sort(key=lambda e: e["ts"])
    store.save()
    return summarise()


def record(feature_id: str, *, success: bool, time_of_day: str, activity: str) -> None:
    state = store.get_state()
    state["events"].append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "feature_id": feature_id,
            "success": success,
            "time_of_day": time_of_day,
            "activity": activity,
        }
    )
    store.save()


def summarise() -> dict[str, Any]:
    """Aggregate counts → ranks → "most used" / "least used" lists."""
    state = store.get_state()
    counts = Counter(e["feature_id"] for e in state["events"])
    total = max(sum(counts.values()), 1)
    rows = []
    for fid, feat in state["features"].items():
        n = counts.get(fid, 0)
        rows.append(
            {
                "id": fid,
                "name": feat["name"],
                "category": feat["category"],
                "events": n,
                "share_pct": round(100 * n / total, 2),
                "compute_class": feat["compute_class"],
                "enabled": feat["enabled"],
            }
        )
    rows.sort(key=lambda r: r["events"], reverse=True)
    most_used = [r for r in rows if r["events"] > 0][:6]
    least_used = [r for r in rows if r["events"] <= 1]
    return {
        "total_events": total,
        "most_used": most_used,
        "least_used": least_used,
        "all": rows,
    }
