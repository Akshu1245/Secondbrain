"""Lightweight bearer-token auth for the API.

If `api_token` is unset, the API is open (useful for local dev / demos).
If set, every protected route requires `Authorization: Bearer <token>`.
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from .config import settings


async def require_token(request: Request) -> None:
    if not settings.api_token:
        return  # open mode
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        token = header.split(" ", 1)[1].strip()
        if token == settings.api_token:
            return
    # Allow ?token=... for share-target / Shortcut convenience
    qs_token = request.query_params.get("token")
    if qs_token and qs_token == settings.api_token:
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
