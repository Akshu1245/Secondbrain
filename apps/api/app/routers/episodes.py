"""Episodic-memory queries — "what did I save from where, and when".

Backed by the v1 `episodes` table that records actor / device / channel
on every ingest.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from .. import db
from ..auth import require_token

router = APIRouter(prefix="/api", tags=["memory"], dependencies=[Depends(require_token)])


@router.get("/communities")
def list_communities(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    rows = db.query_all(
        "SELECT id, label, summary, member_ids, period_start, period_end, created_at "
        "FROM communities ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return {"communities": [dict(r) for r in rows]}


@router.get("/reflections")
def list_reflections(limit: int = Query(default=20, ge=1, le=100)) -> dict:
    rows = db.query_all(
        "SELECT id, text, period_start, period_end, confidence, created_at "
        "FROM reflections ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return {"reflections": [dict(r) for r in rows]}


@router.get("/episodes")
def list_episodes(
    actor: str | None = None,
    channel: str | None = None,
    since: str | None = Query(default=None, description="ISO 8601 timestamp"),
    until: str | None = None,
    limit: int = Query(default=50, ge=1, le=500),
) -> dict:
    where: list[str] = []
    params: list = []
    if actor:
        where.append("e.actor = ?")
        params.append(actor)
    if channel:
        where.append("e.channel = ?")
        params.append(channel)
    if since:
        where.append("e.created_at >= ?")
        params.append(since)
    if until:
        where.append("e.created_at <= ?")
        params.append(until)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = db.query_all(
        f"""
        SELECT e.id, e.item_id, e.actor, e.device, e.channel, e.note, e.created_at,
               i.title, i.tldr, i.source_url, i.source_platform
          FROM episodes e
          LEFT JOIN items i ON i.id = e.item_id
        {where_sql}
         ORDER BY e.id DESC
         LIMIT ?
        """,
        tuple(params + [limit]),
    )
    total_row = db.query_one(
        f"SELECT COUNT(*) AS c FROM episodes e {where_sql}", tuple(params)
    )
    return {
        "episodes": [dict(r) for r in rows],
        "total": int(total_row["c"]) if total_row else 0,
    }
