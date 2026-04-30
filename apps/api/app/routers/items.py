"""Item CRUD."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db
from ..auth import require_token
from ..models import EntityOut, ItemListOut, ItemOut, JobEvent, TagOut

router = APIRouter(prefix="/api", tags=["items"], dependencies=[Depends(require_token)])


@router.get("/items", response_model=ItemListOut)
def list_items(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    kind: str | None = None,
    platform: str | None = None,
    tag: str | None = None,
    status: str | None = None,
) -> ItemListOut:
    where: list[str] = []
    params: list = []
    if kind:
        where.append("i.kind = ?")
        params.append(kind)
    if platform:
        where.append("i.source_platform = ?")
        params.append(platform)
    if status:
        where.append("i.status = ?")
        params.append(status)
    if tag:
        where.append(
            "EXISTS (SELECT 1 FROM item_tags it JOIN tags t ON t.id=it.tag_id "
            "WHERE it.item_id=i.id AND t.name=?)"
        )
        params.append(tag.lower())
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = db.query_all(
        f"SELECT i.id FROM items i {where_sql} ORDER BY i.id DESC LIMIT ? OFFSET ?",
        tuple(params + [limit, offset]),
    )
    total_row = db.query_one(f"SELECT COUNT(*) c FROM items i {where_sql}", tuple(params))
    items = [_row_to_item(r["id"]) for r in rows]
    return ItemListOut(items=items, total=total_row["c"] if total_row else len(items))


@router.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int) -> ItemOut:
    return _row_to_item(item_id)


@router.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict:
    if not db.query_one("SELECT 1 FROM items WHERE id=?", (item_id,)):
        raise HTTPException(status_code=404, detail="not found")
    db.execute("DELETE FROM items WHERE id=?", (item_id,))
    db.execute("DELETE FROM item_vectors WHERE item_id=?", (item_id,))
    return {"ok": True}


@router.get("/items/{item_id}/events", response_model=list[JobEvent])
def list_events(item_id: int) -> list[JobEvent]:
    rows = db.query_all(
        "SELECT stage, status, detail, created_at FROM job_events WHERE item_id=? ORDER BY id ASC",
        (item_id,),
    )
    return [JobEvent(**dict(r)) for r in rows]


# ---------- helpers ----------

def _row_to_item(item_id: int) -> ItemOut:
    row = db.query_one("SELECT * FROM items WHERE id=?", (item_id,))
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    tag_rows = db.query_all(
        "SELECT t.id, t.name FROM tags t JOIN item_tags it ON it.tag_id=t.id WHERE it.item_id=?",
        (item_id,),
    )
    ent_rows = db.query_all(
        """
        SELECT e.id, e.name, e.entity_type, e.description, e.canonical_url,
               (SELECT COUNT(*) FROM item_entities ie WHERE ie.entity_id=e.id) mention_count
          FROM entities e
          JOIN item_entities ie ON ie.entity_id = e.id
         WHERE ie.item_id = ?
        """,
        (item_id,),
    )
    return ItemOut(
        id=row["id"],
        kind=row["kind"],
        source_url=row["source_url"],
        source_platform=row["source_platform"],
        title=row["title"],
        author=row["author"],
        summary=row["summary"],
        tldr=row["tldr"],
        raw_text=row["raw_text"],
        media_path=row["media_path"],
        duration_sec=row["duration_sec"],
        status=row["status"],
        error=row["error"],
        created_at=_dt(row["created_at"]),
        updated_at=_dt(row["updated_at"]),
        tags=[TagOut(id=r["id"], name=r["name"]) for r in tag_rows],
        entities=[
            EntityOut(
                id=r["id"],
                name=r["name"],
                entity_type=r["entity_type"],
                description=r["description"],
                canonical_url=r["canonical_url"],
                mention_count=r["mention_count"],
            )
            for r in ent_rows
        ],
    )


def _dt(v) -> datetime:
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow()
    return datetime.utcnow()
