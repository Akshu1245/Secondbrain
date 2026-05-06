"""AOL FastAPI app — wires the 6 modules together."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import compute, context, feedback
from . import filter as feature_filter
from . import store, usage


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    state = store.get_state()
    if not state["events"]:
        usage.simulate(days=30)
    yield


app = FastAPI(
    title="AI Optimization Layer (AOL)",
    version="0.1.0",
    description=(
        "Middleware that sits between a smartphone user and the OEM AI "
        "assistant. Filters features, suggests by context, routes compute "
        "between local + cloud, and learns from feedback. Rule-based, no ML."
    ),
    lifespan=_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Module 1: Usage Tracker ───────────────────────────────────────────────


class UsageEventIn(BaseModel):
    feature_id: str
    success: bool = True
    time_of_day: str = Field(default="midday", pattern="^(morning|midday|evening|night)$")
    activity: str = "work"


@app.get("/api/usage")
def get_usage() -> dict[str, Any]:
    return usage.summarise()


@app.post("/api/usage/event")
def post_usage(event: UsageEventIn) -> dict[str, Any]:
    state = store.get_state()
    if event.feature_id not in state["features"]:
        raise HTTPException(404, f"unknown feature: {event.feature_id}")
    usage.record(
        event.feature_id,
        success=event.success,
        time_of_day=event.time_of_day,
        activity=event.activity,
    )
    return {"ok": True}


@app.post("/api/usage/simulate")
def post_simulate(days: int = 30) -> dict[str, Any]:
    return usage.simulate(days=days)


# ── Module 2: Smart Feature Filter ────────────────────────────────────────


class TogglePayload(BaseModel):
    enabled: bool


@app.get("/api/features")
def list_features() -> dict[str, Any]:
    state = store.get_state()
    return {"features": list(state["features"].values()), "user_prefs": state["user_prefs"]}


@app.get("/api/features/optimised")
def list_optimised() -> dict[str, Any]:
    return feature_filter.optimised_surface()


@app.post("/api/features/{feature_id}/toggle")
def toggle_feature(feature_id: str, payload: TogglePayload) -> dict[str, Any]:
    try:
        return feature_filter.toggle(feature_id, payload.enabled)
    except KeyError:
        raise HTTPException(404, f"unknown feature: {feature_id}")


class PrefsPayload(BaseModel):
    priority_categories: list[str] | None = None
    battery_saver: bool | None = None
    data_saver: bool | None = None
    private_mode: bool | None = None


@app.post("/api/prefs")
def set_prefs(p: PrefsPayload) -> dict[str, Any]:
    return feature_filter.set_prefs(
        priority_categories=p.priority_categories,
        battery_saver=p.battery_saver,
        data_saver=p.data_saver,
        private_mode=p.private_mode,
    )


# ── Module 3: Context-Aware Engine ────────────────────────────────────────


@app.get("/api/context/now")
def get_context(time_of_day: str | None = None, activity: str | None = None) -> dict[str, Any]:
    return context.suggest(time_of_day=time_of_day, activity=activity)


# ── Module 4: Compute Optimizer ───────────────────────────────────────────


class RoutePayload(BaseModel):
    feature_id: str
    payload_kb: int = 0


@app.post("/api/compute/route")
def compute_route(p: RoutePayload) -> dict[str, Any]:
    try:
        return compute.route(p.feature_id, payload_kb=p.payload_kb)
    except KeyError:
        raise HTTPException(404, f"unknown feature: {p.feature_id}")


@app.get("/api/compute/log")
def compute_log(limit: int = 50) -> dict[str, Any]:
    return {"log": compute.recent_log(limit), "stats": compute.aggregate()}


# ── Module 6: Feedback Loop ───────────────────────────────────────────────


class FeedbackPayload(BaseModel):
    feature_id: str
    rating: str = Field(pattern="^(love|ok|annoying|never_use)$")
    comment: str | None = None


@app.post("/api/feedback")
def post_feedback(p: FeedbackPayload) -> dict[str, Any]:
    try:
        return feedback.submit(feature_id=p.feature_id, rating=p.rating, comment=p.comment)
    except (KeyError, ValueError) as e:
        raise HTTPException(400, str(e))


@app.get("/api/feedback")
def get_feedback(limit: int = 100) -> dict[str, Any]:
    return {
        "entries": feedback.all_entries(limit),
        "improvement_suggestions": feedback.suggestions(),
    }


# ── Module 5: Demo / Analytics endpoints ──────────────────────────────────


@app.get("/api/before-after")
def before_after() -> dict[str, Any]:
    """The canonical demo endpoint — returns the OEM's "raw" surface (every
    feature default-on, no ordering, no context, no compute routing) and the
    AOL-optimised surface side by side."""
    state = store.get_state()
    raw = sorted(
        ({"id": fid, "name": f["name"], "category": f["category"],
          "compute_class": f["compute_class"], "default_on": f["default_on"]}
         for fid, f in state["features"].items()),
        key=lambda r: r["name"].lower(),
    )
    optimised = feature_filter.optimised_surface()
    return {
        "before": {"feature_count": len(raw), "features": raw},
        "after": {
            "feature_count": len(optimised["visible"]),
            "features": optimised["visible"],
            "hidden_count": len(optimised["hide_recommended"]),
        },
        "savings": {
            "features_hidden_pct": round(
                100 * len(optimised["hide_recommended"]) / max(1, len(raw)), 1
            ),
            "compute": compute.aggregate(),
        },
    }


@app.get("/api/analytics")
def analytics() -> dict[str, Any]:
    summary = usage.summarise()
    surface = feature_filter.optimised_surface()
    cat: dict[str, dict[str, int]] = {}
    for r in summary["all"]:
        c = cat.setdefault(r["category"], {"events": 0, "features": 0})
        c["events"] += r["events"]
        c["features"] += 1
    return {
        "category_breakdown": cat,
        "top_features": summary["most_used"],
        "tail": summary["least_used"],
        "visible_count": len(surface["visible"]),
        "hidden_count": len(surface["hide_recommended"]),
        "user_disabled": len(surface["user_disabled"]),
        "compute": compute.aggregate(),
        "feedback_suggestions": feedback.suggestions(),
    }


@app.post("/api/admin/reset")
def reset_all() -> dict[str, Any]:
    store.reset()
    usage.simulate(days=30)
    return {"ok": True}


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "version": "0.1.0"}


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "AI Optimization Layer (AOL)",
        "endpoints": {
            "features": "/api/features",
            "optimised": "/api/features/optimised",
            "before_after": "/api/before-after",
            "context": "/api/context/now?time_of_day=morning&activity=commute",
            "compute_route": "POST /api/compute/route",
            "compute_log": "/api/compute/log",
            "feedback": "/api/feedback",
            "analytics": "/api/analytics",
            "docs": "/docs",
        },
    }
