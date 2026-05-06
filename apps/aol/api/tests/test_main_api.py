"""Smoke tests for the FastAPI surface."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app import main, usage


def _client() -> TestClient:
    # Seed a clean, deterministic dataset so before/after numbers are stable.
    usage.simulate(days=30, seed=42)
    return TestClient(main.app)


def test_health_endpoint():
    r = _client().get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True


def test_root_endpoint_lists_known_routes():
    r = _client().get("/")
    assert r.status_code == 200
    endpoints = r.json()["endpoints"]
    for k in ("features", "optimised", "before_after", "context",
              "compute_route", "compute_log", "feedback", "analytics", "docs"):
        assert k in endpoints


def test_before_after_shows_24_features_and_some_hidden():
    r = _client().get("/api/before-after")
    assert r.status_code == 200
    body = r.json()
    assert body["before"]["feature_count"] == 24
    assert body["after"]["feature_count"] >= 1
    assert body["after"]["hidden_count"] >= 1
    # Headline pitch number: "24 → 18, ~25% hidden". Allow some tolerance
    # for seed drift, but pin the order of magnitude.
    pct = body["savings"]["features_hidden_pct"]
    assert 10.0 <= pct <= 50.0


def test_compute_route_records_a_log_entry_and_returns_a_decision():
    c = _client()
    r = c.post("/api/compute/route", json={"feature_id": "smart_reply"})
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] in {"local", "cloud"}
    assert "reason" in body

    log = c.get("/api/compute/log").json()
    assert log["log"][0]["feature_id"] == "smart_reply"


def test_compute_route_unknown_feature_returns_404():
    r = _client().post("/api/compute/route",
                       json={"feature_id": "ghost_feature"})
    assert r.status_code == 404


def test_feedback_post_validates_rating_enum():
    r = _client().post("/api/feedback",
                       json={"feature_id": "smart_reply", "rating": "thumbs_up"})
    assert r.status_code == 422  # FastAPI Pydantic-validated regex


def test_admin_reset_clears_routing_log_then_reseeds_events():
    c = _client()
    c.post("/api/compute/route", json={"feature_id": "smart_reply"})
    assert len(c.get("/api/compute/log").json()["log"]) >= 1

    r = c.post("/api/admin/reset")
    assert r.status_code == 200

    after = c.get("/api/compute/log").json()
    assert after["log"] == []
    # Usage events are re-seeded by the reset handler so the dashboard
    # never looks empty post-reset.
    assert c.get("/api/usage").json()["total_events"] > 0


def test_features_toggle_round_trip():
    c = _client()
    r = c.post("/api/features/smart_reply/toggle", json={"enabled": False})
    assert r.status_code == 200
    assert r.json() == {"feature_id": "smart_reply", "enabled": False}

    surface = c.get("/api/features/optimised").json()
    assert "smart_reply" in {f["id"] for f in surface["user_disabled"]}
