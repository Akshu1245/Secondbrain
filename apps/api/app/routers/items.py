"""Item CRUD."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from pydantic import BaseModel

from .. import db
from ..auth import require_token
from ..embeddings import embed_one, vec_to_blob
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


class ItemPatch(BaseModel):
    title: str | None = None
    summary: str | None = None
    tldr: str | None = None
    tags: list[str] | None = None


@router.patch("/items/{item_id}", response_model=ItemOut)
def patch_item(item_id: int, patch: ItemPatch) -> ItemOut:
    """Edit a saved item. Every change is logged as a few-shot exemplar so
    future enrichments can pull (input → corrected output) pairs in-context
    (DSPy-style correction loop)."""
    row = db.query_one(
        "SELECT title, summary, tldr, raw_text FROM items WHERE id=?", (item_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="not found")

    fields: dict[str, str] = {}
    if patch.title is not None and patch.title != row["title"]:
        fields["title"] = patch.title
    if patch.summary is not None and patch.summary != row["summary"]:
        fields["summary"] = patch.summary
    if patch.tldr is not None and patch.tldr != row["tldr"]:
        fields["tldr"] = patch.tldr

    if fields:
        sets = ", ".join(f"{k}=?" for k in fields)
        params = list(fields.values()) + [item_id]
        db.execute(
            f"UPDATE items SET {sets}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            tuple(params),
        )
        # Record an exemplar per corrected field.
        input_text = f"{row['title'] or ''}\n\n{(row['raw_text'] or '')[:4000]}"
        for field, expected in fields.items():
            cur = db.execute(
                "INSERT INTO exemplars(field, input_text, expected) VALUES(?,?,?)",
                (field, input_text, expected),
            )
            try:
                v = embed_one(input_text)
                db.execute(
                    "INSERT OR REPLACE INTO exemplars_vec(exemplar_id, embedding) VALUES(?, ?)",
                    (cur.lastrowid, vec_to_blob(v)),
                )
            except Exception:  # noqa: BLE001
                pass

    if patch.tags is not None:
        # Replace the auto tag set with the user's curated set.
        db.execute("DELETE FROM item_tags WHERE item_id=?", (item_id,))
        for name in dict.fromkeys(t.strip().lower() for t in patch.tags if t.strip()):
            db.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (name,))
            tag_row = db.query_one("SELECT id FROM tags WHERE name=?", (name,))
            if tag_row:
                db.execute(
                    "INSERT OR IGNORE INTO item_tags(item_id, tag_id, source) VALUES(?,?, 'user')",
                    (item_id, tag_row["id"]),
                )

    return _row_to_item(item_id)


@router.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict:
    if not db.query_one("SELECT 1 FROM items WHERE id=?", (item_id,)):
        raise HTTPException(status_code=404, detail="not found")
    # facts_vec is a vec0 virtual table, no FK cascade — drop fact vectors first.
    from ..ingest.pipeline import _delete_facts_for_item

    _delete_facts_for_item(item_id)
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
