"""Tiny in-process pub/sub for SSE updates.

Every connected client gets a queue; publish_event() fans out non-blocking.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

log = logging.getLogger(__name__)

_subscribers: set[asyncio.Queue] = set()


def publish_event(evt: dict[str, Any]) -> None:
    payload = json.dumps(evt)
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
