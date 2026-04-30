"""Tiny in-process pub/sub for SSE updates.

Every connected client gets a queue; publish_event() fans out non-blocking.

publish_event is safe to call from any thread — Starlette runs sync background
tasks in a worker threadpool, but asyncio.Queue is not thread-safe, so we hop
back onto the main loop with call_soon_threadsafe before touching the queues.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

log = logging.getLogger(__name__)

_subscribers: set[asyncio.Queue] = set()
_loop: asyncio.AbstractEventLoop | None = None


def bind_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Remember the main event loop. Called once from FastAPI's lifespan."""
    global _loop
    _loop = loop


def publish_event(evt: dict[str, Any]) -> None:
    payload = json.dumps(evt)
    loop = _loop
    if loop is None or not _subscribers:
        return
    if _is_running_loop(loop):
        _fanout(payload)
    else:
        loop.call_soon_threadsafe(_fanout, payload)


def _is_running_loop(loop: asyncio.AbstractEventLoop) -> bool:
    try:
        return asyncio.get_running_loop() is loop
    except RuntimeError:
        return False


def _fanout(payload: str) -> None:
    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            log.debug("event queue full, dropping for one subscriber")


@asynccontextmanager
async def subscribe():
    q: asyncio.Queue = asyncio.Queue(maxsize=128)
    _subscribers.add(q)
    try:
        yield q
    finally:
        _subscribers.discard(q)
