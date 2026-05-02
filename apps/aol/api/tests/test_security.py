"""Tests for the defensive hardening layer (apps/aol/api/app/security.py)."""

from __future__ import annotations


# ── Admin-reset gate ──────────────────────────────────────────────────────


def test_admin_reset_open_when_token_unset(client):
    """Backwards-compat: with no AOL_ADMIN_TOKEN set, the live demo's
    Reset button keeps working."""
    r = client.post("/api/admin/reset")
    assert r.status_code == 200, r.text
    assert r.json() == {"ok": True}


def test_admin_reset_requires_bearer_when_token_set(aol_env):
    c = aol_env(
        AOL_ADMIN_TOKEN="s3cr3t",
        AOL_RATE_LIMIT_ADMIN="10000/minute",
        AOL_RATE_LIMIT_DEFAULT="10000/minute",
        AOL_RATE_LIMIT_WRITE="10000/minute",
    )
    # Missing header.
    assert c.post("/api/admin/reset").status_code == 401
    # Wrong scheme.
    assert c.post("/api/admin/reset", headers={"Authorization": "Token s3cr3t"}).status_code == 401
    # Wrong token.
    assert c.post("/api/admin/reset", headers={"Authorization": "Bearer nope"}).status_code == 401
    # Correct token.
    r = c.post("/api/admin/reset", headers={"Authorization": "Bearer s3cr3t"})
    assert r.status_code == 200, r.text


# ── Parameter bounds ──────────────────────────────────────────────────────


def test_simulate_days_bounded(client):
    # In-range works.
    assert client.post("/api/usage/simulate?days=10").status_code == 200
    # Above max → 422.
    assert client.post("/api/usage/simulate?days=10000").status_code == 422
    # Below min → 422.
    assert client.post("/api/usage/simulate?days=0").status_code == 422


def test_compute_log_limit_bounded(client):
    assert client.get("/api/compute/log?limit=10").status_code == 200
    assert client.get("/api/compute/log?limit=99999").status_code == 422
    assert client.get("/api/compute/log?limit=0").status_code == 422


def test_feedback_limit_bounded(client):
    assert client.get("/api/feedback?limit=10").status_code == 200
    assert client.get("/api/feedback?limit=99999").status_code == 422


def test_compute_route_payload_kb_bounded(client):
    feats = client.get("/api/features").json()["features"]
    fid = feats[0]["id"]
    assert client.post(
        "/api/compute/route", json={"feature_id": fid, "payload_kb": 0}
    ).status_code == 200
    # > 16384 KB → 422.
    assert client.post(
        "/api/compute/route", json={"feature_id": fid, "payload_kb": 999999}
    ).status_code == 422
    # Negative → 422.
    assert client.post(
        "/api/compute/route", json={"feature_id": fid, "payload_kb": -1}
    ).status_code == 422


# ── Security response headers ─────────────────────────────────────────────


def test_security_headers_on_responses(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("Referrer-Policy") == "no-referrer"


# ── CORS env var parsing ──────────────────────────────────────────────────


def test_cors_default_allows_all(client):
    r = client.options(
        "/api/health",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "*"


def test_cors_restricts_to_configured_origins(aol_env):
    c = aol_env(
        AOL_ALLOWED_ORIGINS="https://allowed.example.com",
        AOL_RATE_LIMIT_DEFAULT="10000/minute",
        AOL_RATE_LIMIT_WRITE="10000/minute",
        AOL_RATE_LIMIT_ADMIN="10000/minute",
    )
    # Allowed origin echoes back.
    r = c.options(
        "/api/health",
        headers={
            "Origin": "https://allowed.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "https://allowed.example.com"
    # Disallowed origin: header is absent.
    r = c.options(
        "/api/health",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") in (None, "")


# ── Rate limiting ─────────────────────────────────────────────────────────


def test_rate_limit_returns_429_after_threshold(aol_env):
    """Configure a tiny write limit and hammer a write endpoint."""
    c = aol_env(
        AOL_ADMIN_TOKEN=None,
        AOL_RATE_LIMIT_DEFAULT="10000/minute",
        AOL_RATE_LIMIT_WRITE="3/minute",
        AOL_RATE_LIMIT_ADMIN="10000/minute",
    )
    feats = c.get("/api/features").json()["features"]
    fid = feats[0]["id"]
    body = {"feature_id": fid, "payload_kb": 0}
    statuses = [c.post("/api/compute/route", json=body).status_code for _ in range(6)]
    # First three should pass; at least one of the next three should hit 429.
    assert statuses[0] == 200
    assert 429 in statuses, f"expected at least one 429, got {statuses}"


def test_admin_reset_rate_limit(aol_env):
    c = aol_env(
        AOL_ADMIN_TOKEN=None,
        AOL_RATE_LIMIT_DEFAULT="10000/minute",
        AOL_RATE_LIMIT_WRITE="10000/minute",
        AOL_RATE_LIMIT_ADMIN="2/minute",
    )
    statuses = [c.post("/api/admin/reset").status_code for _ in range(4)]
    assert statuses[:2] == [200, 200]
    assert 429 in statuses[2:], f"expected admin rate limit to fire, got {statuses}"
