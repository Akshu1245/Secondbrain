"""Ingest endpoints — accept URLs, notes, and share-target submissions."""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Request

from ..auth import require_token
from ..ingest.pipeline import create_pending_item, process_item
from ..models import IngestRequest, ItemOut
from .items import _row_to_item

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ingest"], dependencies=[Depends(require_token)])


@router.post("/ingest", response_model=ItemOut)
async def ingest(req: IngestRequest, background: BackgroundTasks) -> ItemOut:
    if not (req.text or req.url):
        raise HTTPException(status_code=400, detail="provide text or url")
    item_id = create_pending_item(text=req.text, url=req.url, title=req.title)
    background.add_task(process_item, item_id, text=req.text, url=req.url, title=req.title)
    return _row_to_item(item_id)


@router.post("/share")
async def share_target(
    request: Request,
    background: BackgroundTasks,
    title: str | None = Form(default=None),
    text: str | None = Form(default=None),
    url: str | None = Form(default=None),
) -> dict:
    """Web Share Target endpoint.

    PWAs registered as share targets receive title/text/url either as
    application/x-www-form-urlencoded or multipart/form-data. We also accept
    iOS Shortcuts that POST raw text.
    """
    if not any([title, text, url]):
        # Try raw body for iOS Shortcuts that just stuff a string in.
        raw = (await request.body()).decode("utf-8", errors="ignore").strip()
        if raw:
            text = raw
    payload = " ".join(p for p in [url, text] if p) or title or ""
    if not payload:
        raise HTTPException(status_code=400, detail="empty share")
    item_id = create_pending_item(text=payload, url=url, title=title)
    background.add_task(process_item, item_id, text=payload, url=url, title=title)
    return {"ok": True, "item_id": item_id}
