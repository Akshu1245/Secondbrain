"""Defensive hardening for the public AOL API.

This module is the single home for everything that protects the deployed
demo from automated abuse:

* CORS origin allow-list (env-configurable, defaults to ``*`` for backwards
  compatibility with the existing live frontend).
* SlowAPI rate limiter (env-configurable defaults; per-IP).
* ``require_admin`` dependency for the admin-reset endpoint.
* ``security_headers_middleware`` adds conservative response headers.

All toggles read environment variables so the same code runs both for the
fly.io demo and for any OEM-side fork without code changes.
"""

from __future__ import annotations

import logging
import os
import secrets as _secrets
from typing import Iterable

from fastapi import Header, HTTPException, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

log = logging.getLogger("aol.security")

# ── CORS ──────────────────────────────────────────────────────────────────


DEFAULT_ALLOWED_ORIGINS = "*"


def parse_allowed_origins(raw: str | None = None) -> list[str]:
    """Parse ``AOL_ALLOWED_ORIGINS`` into a list FastAPI's CORSMiddleware
    understands.

    * ``None`` / empty / ``"*"`` → ``["*"]`` (open). This is the historical
      default and is preserved so existing deployments keep working.
    * Comma-separated list → trimmed list of origins.
    """
    raw = (raw if raw is not None else os.environ.get("AOL_ALLOWED_ORIGINS"))
    if raw is None:
        raw = DEFAULT_ALLOWED_ORIGINS
    raw = raw.strip()
    if not raw or raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


# ── Rate limiting ─────────────────────────────────────────────────────────


def _default_rate() -> str:
    """Per-IP default for read endpoints. Generous enough for a dashboard
    user; tight enough that a script running flat-out hits the ceiling."""
    return os.environ.get("AOL_RATE_LIMIT_DEFAULT", "120/minute")


def _write_rate() -> str:
    """Per-IP cap on POST endpoints that mutate state."""
    return os.environ.get("AOL_RATE_LIMIT_WRITE", "30/minute")


def _admin_rate() -> str:
    """Per-IP cap on the admin-reset endpoint."""
    return os.environ.get("AOL_RATE_LIMIT_ADMIN", "5/minute")


def make_limiter() -> Limiter:
    return Limiter(
        key_func=get_remote_address,
        default_limits=[_default_rate()],
        # headers_enabled=False keeps the endpoint signatures simple — we
        # don't need slowapi to inject X-RateLimit-* headers (the dashboard
        # doesn't read them) and enabling it requires a `response: Response`
        # parameter on every rate-limited endpoint.
        headers_enabled=False,
    )


def write_limit() -> str:
    return _write_rate()


def admin_limit() -> str:
    return _admin_rate()


# ── Admin-reset gate ──────────────────────────────────────────────────────


def _expected_token() -> str | None:
    tok = os.environ.get("AOL_ADMIN_TOKEN")
    return tok.strip() if tok else None


def require_admin(authorization: str | None = Header(default=None)) -> None:
    """Gate ``/api/admin/reset`` behind a bearer token.

    Behaviour:

    * If ``AOL_ADMIN_TOKEN`` is **set**: the request must include
      ``Authorization: Bearer <token>`` with a constant-time match.
    * If ``AOL_ADMIN_TOKEN`` is **unset**: the endpoint stays open
      (preserves the live-demo "Reset" button) but a warning is logged
      every call so operators see the exposure in their logs.

    Operators are expected to set the env var on any non-demo deploy.
    """
    expected = _expected_token()
    if expected is None:
        log.warning(
            "admin endpoint hit with AOL_ADMIN_TOKEN unset — "
            "set it on production deploys to require Bearer auth"
        )
        return

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    provided = authorization.split(" ", 1)[1].strip()
    if not _secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="invalid bearer token")


# ── Response headers ──────────────────────────────────────────────────────


_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
}


async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    for k, v in _SECURITY_HEADERS.items():
        response.headers.setdefault(k, v)
    return response


def security_headers() -> dict[str, str]:
    """Exposed for tests."""
    return dict(_SECURITY_HEADERS)


__all__: Iterable[str] = (
    "parse_allowed_origins",
    "make_limiter",
    "write_limit",
    "admin_limit",
    "require_admin",
    "security_headers",
    "security_headers_middleware",
)
