"""Procedural memory — skills the agent quotes verbatim.

A "skill" is a short, high-confidence "how I do X" note ("How I deploy
to Render", "How I debug Postgres locks"). Stored separately from items
so distillation never compresses them.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from .. import db
from ..auth import require_token
from ..embeddings import embed_one, vec_to_blob

router = APIRouter(prefix="/api/skills", tags=["skills"], dependencies=[Depends(require_token)])


class SkillIn(BaseModel):
    name: str
    summary: str
    body: str
    tags: list[str] | None = None


class SkillPatch(BaseModel):
    summary: str | None = None
    body: str | None = None
    tags: list[str] | None = None


@router.get("")
def list_skills(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    rows = db.query_all(
        "SELECT id, name, summary, tags_json, use_count, created_at, updated_at "
        "FROM skills ORDER BY use_count DESC, id DESC LIMIT ?",
        (limit,),
    )
    return {"skills": [dict(r) for r in rows]}


@router.get("/{skill_id}")
def get_skill(skill_id: int) -> dict:
    r = db.query_one("SELECT * FROM skills WHERE id = ?", (skill_id,))
    if not r:
        raise HTTPException(status_code=404, detail="not found")
    db.execute("UPDATE skills SET use_count = use_count + 1 WHERE id = ?", (skill_id,))
    return dict(r)


@router.post("")
def create_skill(skill: SkillIn) -> dict:
    cur = db.execute(
        "INSERT INTO skills(name, summary, body, tags_json) VALUES(?,?,?,?) "
        "ON CONFLICT(name) DO UPDATE SET "
        "  summary = excluded.summary, body = excluded.body, "
        "  tags_json = excluded.tags_json, updated_at = CURRENT_TIMESTAMP",
        (skill.name, skill.summary, skill.body, json.dumps(skill.tags or [])),
    )
    row = db.query_one("SELECT id FROM skills WHERE name = ?", (skill.name,))
    if row is None:
        raise HTTPException(status_code=500, detail="failed to upsert skill")
    skill_id = int(row["id"])
    try:
        v = embed_one(f"{skill.name}\n{skill.summary}\n{skill.body}")
        db.execute(
            "INSERT OR REPLACE INTO skills_vec(skill_id, embedding) VALUES(?, ?)",
            (skill_id, vec_to_blob(v)),
        )
    except Exception:  # noqa: BLE001 — embeddings are best-effort
        pass
    _ = cur  # silence unused
    return {"id": skill_id, "name": skill.name}


@router.patch("/{skill_id}")
def patch_skill(skill_id: int, patch: SkillPatch) -> dict:
    row = db.query_one("SELECT id, name, summary, body FROM skills WHERE id = ?", (skill_id,))
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    fields: dict[str, object] = {}
    if patch.summary is not None:
        fields["summary"] = patch.summary
    if patch.body is not None:
        fields["body"] = patch.body
    if patch.tags is not None:
        fields["tags_json"] = json.dumps(patch.tags)
    if fields:
        sets = ", ".join(f"{k} = ?" for k in fields)
        params = list(fields.values()) + [skill_id]
        db.execute(
            f"UPDATE skills SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            tuple(params),
        )
        # re-embed if any text changed
        if "summary" in fields or "body" in fields:
            updated = db.query_one(
                "SELECT name, summary, body FROM skills WHERE id = ?", (skill_id,)
            )
            try:
                v = embed_one(
                    f"{updated['name']}\n{updated['summary']}\n{updated['body']}"
                )
                db.execute(
                    "INSERT OR REPLACE INTO skills_vec(skill_id, embedding) VALUES(?, ?)",
                    (skill_id, vec_to_blob(v)),
                )
            except Exception:  # noqa: BLE001
                pass
    return {"ok": True}


@router.delete("/{skill_id}")
def delete_skill(skill_id: int) -> dict:
    if not db.query_one("SELECT 1 FROM skills WHERE id = ?", (skill_id,)):
        raise HTTPException(status_code=404, detail="not found")
    db.execute("DELETE FROM skills_vec WHERE skill_id = ?", (skill_id,))
    db.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
    return {"ok": True}
