"""Entities + Tool Memory."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db
from ..auth import require_token
from ..models import EntityOut, ItemOut
from .items import _row_to_item

router = APIRouter(prefix="/api", tags=["entities"], dependencies=[Depends(require_token)])


@router.get("/entities", response_model=list[EntityOut])
def list_entities(
    entity_type: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[EntityOut]:
    where = "WHERE e.entity_type = ?" if entity_type else ""
    params = (entity_type, limit) if entity_type else (limit,)
    rows = db.query_all(
        f"""
        SELECT e.*, COUNT(ie.item_id) AS mention_count
          FROM entities e
          LEFT JOIN item_entities ie ON ie.entity_id = e.id
          {where}
         GROUP BY e.id
         ORDER BY mention_count DESC, e.name ASC
         LIMIT ?
        """,
        params,
    )
    return [
        EntityOut(
            id=r["id"],
            name=r["name"],
            entity_type=r["entity_type"],
            description=r["description"],
            canonical_url=r["canonical_url"],
            mention_count=int(r["mention_count"] or 0),
        )
        for r in rows
    ]


@router.get("/entities/{entity_id}/items", response_model=list[ItemOut])
def items_for_entity(entity_id: int) -> list[ItemOut]:
    if not db.query_one("SELECT 1 FROM entities WHERE id=?", (entity_id,)):
        raise HTTPException(status_code=404, detail="not found")
    rows = db.query_all(
        "SELECT item_id FROM item_entities WHERE entity_id=? ORDER BY item_id DESC",
        (entity_id,),
    )
    return [_row_to_item(r["item_id"]) for r in rows]


@router.get("/tools", response_model=list[EntityOut])
def tool_memory(limit: int = Query(default=200, ge=1, le=1000)) -> list[EntityOut]:
    """Specialised view: every tool/app/website ever extracted, by mention count."""
    rows = db.query_all(
        """
        SELECT e.*, COUNT(ie.item_id) AS mention_count
          FROM entities e
          LEFT JOIN item_entities ie ON ie.entity_id = e.id
         WHERE e.entity_type IN ('tool','app','website')
         GROUP BY e.id
         ORDER BY mention_count DESC, e.name ASC
         LIMIT ?
        """,
        (limit,),
    )
    return [
        EntityOut(
            id=r["id"],
            name=r["name"],
            entity_type=r["entity_type"],
            description=r["description"],
            canonical_url=r["canonical_url"],
            mention_count=int(r["mention_count"] or 0),
        )
        for r in rows
    ]
