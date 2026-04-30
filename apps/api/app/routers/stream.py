"""Server-Sent Events for real-time UI updates across devices."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from ..auth import require_token
from ..events import subscribe

router = APIRouter(prefix="/api", tags=["stream"], dependencies=[Depends(require_token)])


@router.get("/events")
async def stream_events(request: Request) -> EventSourceResponse:
    async def gen():
        async with subscribe() as q:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield {"event": "update", "data": payload}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "{}"}
    return EventSourceResponse(gen())
