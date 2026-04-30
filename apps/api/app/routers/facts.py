"""Facts CRUD — atomic memory primitives extracted from items."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db
from ..auth import require_token

router = APIRouter(prefix="/api", tags=["facts"], dependencies=[Depends(require_token)])


@router.get("/facts")
def list_facts(
    item_id: int | None = None,
    fact_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict:
    where: list[str] = []
    params: list = []
    if item_id is not None:
        where.append("item_id = ?")
        params.append(item_id)
    if fact_type:
        where.append("fact_type = ?")
        params.append(fact_type.lower())
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    rows = db.query_all(
        f"SELECT id, item_id, text, fact_type, confidence, last_seen_at "
        f"FROM facts {where_sql} ORDER BY last_seen_at DESC LIMIT ? OFFSET ?",
        tuple(params + [limit, offset]),
    )
    total_row = db.query_one(f"SELECT COUNT(*) c FROM facts {where_sql}", tuple(params))
    return {"facts": [dict(r) for r in rows], "total": int(total_row["c"]) if total_row else 0}


@router.delete("/facts/{fact_id}")
def delete_fact(fact_id: int) -> dict:
    if not db.query_one("SELECT 1 FROM facts WHERE id=?", (fact_id,)):
        raise HTTPException(status_code=404, detail="not found")
    db.execute("DELETE FROM facts WHERE id=?", (fact_id,))
    db.execute("DELETE FROM facts_vec WHERE fact_id=?", (fact_id,))
    return {"ok": True}
