"""Module 2 — Smart Feature Filter.

Hide low-usage features, prioritise high-usage ones, respect the user's
explicit toggles and category preferences. Returns a *cleaned* feature list
in the order the OEM should surface them.

Rules (in order):
  1. Explicit user toggle wins. `enabled=False` → never surface.
  2. Features that fired ≥ 3 times in the last 30d are "active".
  3. Features that fired 0 times in the last 30d *and* are not in the user's
     priority categories are "hide_recommended".
  4. Active features are ordered by (priority_category_match, usage_share).
"""

from __future__ import annotations

from typing import Any

from . import store, usage

LOW_USAGE_THRESHOLD = 3


def optimised_surface() -> dict[str, Any]:
    state = store.get_state()
    summary = usage.summarise()
    by_id = {r["id"]: r for r in summary["all"]}
    prio = set(state["user_prefs"]["priority_categories"])

    visible: list[dict[str, Any]] = []
    hide_recommended: list[dict[str, Any]] = []
    user_disabled: list[dict[str, Any]] = []
    for fid, feat in state["features"].items():
        row = by_id[fid] | {
            "description": feat["description"],
            "ms_local": feat["ms_local"],
            "ms_cloud": feat["ms_cloud"],
        }
        if not feat["enabled"]:
            user_disabled.append(row)
            continue
        if row["events"] < LOW_USAGE_THRESHOLD and feat["category"] not in prio:
            hide_recommended.append(row)
            continue
        visible.append(row)

    visible.sort(
        key=lambda r: (
            0 if r["category"] in prio else 1,
            -r["events"],
            r["name"].lower(),
        )
    )
    hide_recommended.sort(key=lambda r: r["events"])
    return {
        "visible": visible,
        "hide_recommended": hide_recommended,
        "user_disabled": user_disabled,
        "rules": {
            "low_usage_threshold_events_30d": LOW_USAGE_THRESHOLD,
            "priority_categories": sorted(prio),
        },
    }


def toggle(feature_id: str, enabled: bool) -> dict[str, Any]:
    state = store.get_state()
    if feature_id not in state["features"]:
        raise KeyError(feature_id)
    state["features"][feature_id]["enabled"] = enabled
    store.save()
    return {"feature_id": feature_id, "enabled": enabled}


def set_prefs(*, priority_categories: list[str] | None = None,
              battery_saver: bool | None = None,
              data_saver: bool | None = None,
              private_mode: bool | None = None) -> dict[str, Any]:
    state = store.get_state()
    if priority_categories is not None:
        state["user_prefs"]["priority_categories"] = list(dict.fromkeys(priority_categories))
    if battery_saver is not None:
        state["user_prefs"]["battery_saver"] = battery_saver
    if data_saver is not None:
        state["user_prefs"]["data_saver"] = data_saver
    if private_mode is not None:
        state["user_prefs"]["private_mode"] = private_mode
    store.save()
    return state["user_prefs"]
