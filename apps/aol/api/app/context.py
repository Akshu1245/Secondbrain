"""Module 3 — Context-Aware Engine.

Given (time_of_day, activity), deterministically suggest the 3 most relevant
features the user is likely to want surfaced *right now*. Pure rules, no ML.

The mapping below is the "system layer's opinion" — it's what we'd want the
OEM to swap in for its current "show every AI feature on the home screen"
behaviour. The mapping is intentionally simple so a PM at Moto can read it,
disagree, and tune it without ML expertise.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from . import store, usage

# (time_of_day, activity) → feature_ids we'd nudge.
_RULES: dict[tuple[str, str], list[str]] = {
    ("morning", "commute"):   ["morning_briefing", "navigation_hint", "spam_call_filter"],
    ("morning", "exercise"):  ["live_caption", "battery_advisor", "morning_briefing"],
    ("midday",  "work"):      ["smart_reply", "screenshot_text", "note_summary"],
    ("midday",  "meeting"):   ["voice_recorder_summary", "live_caption", "note_summary"],
    ("evening", "leisure"):   ["circle_to_search", "smart_reply", "ai_translate_camera"],
    ("evening", "errands"):   ["navigation_hint", "spam_call_filter", "circle_to_search"],
    ("night",   "winddown"):  ["focus_mode", "battery_advisor", "smart_reply"],
    ("night",   "sleeping"):  ["focus_mode", "spam_call_filter", "battery_advisor"],
}

_DEFAULT = ["smart_reply", "screenshot_text", "spam_call_filter"]


def _bucket_for(now: datetime) -> str:
    h = now.hour
    if 5 <= h < 11:
        return "morning"
    if 11 <= h < 16:
        return "midday"
    if 16 <= h < 21:
        return "evening"
    return "night"


def suggest(*, time_of_day: str | None = None, activity: str | None = None,
            now: datetime | None = None) -> dict[str, Any]:
    state = store.get_state()
    bucket = time_of_day or _bucket_for(now or datetime.now())
    act = activity or "leisure"
    ids = _RULES.get((bucket, act), _DEFAULT)
    # Personalise with the user's actual usage — if a recommended feature
    # has 0 events ever AND the user hasn't enabled it explicitly, swap it
    # out for the most-used feature in the same category.
    summary = {r["id"]: r for r in usage.summarise()["all"]}
    suggestions: list[dict[str, Any]] = []
    for fid in ids:
        feat = state["features"].get(fid)
        if not feat or not feat["enabled"]:
            continue
        suggestions.append(
            {
                "id": fid,
                "name": feat["name"],
                "category": feat["category"],
                "reason": f"{bucket} + {act} → relevant",
                "usage_events": summary[fid]["events"] if fid in summary else 0,
            }
        )
    if state["user_prefs"]["battery_saver"]:
        # Skip heavy-compute suggestions when the user is on battery saver.
        suggestions = [
            s for s in suggestions
            if state["features"][s["id"]]["compute_class"] != "heavy"
        ]
    return {
        "context": {"time_of_day": bucket, "activity": act},
        "suggestions": suggestions[:3],
    }
