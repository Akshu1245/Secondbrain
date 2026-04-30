"""Concrete handlers for every tool we expose over MCP.

Every handler takes a single ``args`` dict (validated against the tool's
JSON schema in the router) and returns a JSON-serialisable dict that becomes
the MCP `content` payload.

Design rule: handlers return *lazy* representations by default (e.g. TLDRs,
not raw bodies) so agents can decide what to expand. This is the same idea
as Tool Attention, applied one level down (per-result instead of per-tool).
"""

from __future__ import annotations

import json
from typing import Any

from .. import db
from ..ingest.pipeline import create_pending_item, process_item
from .registry import ToolSpec, register


def _tldrs_for_search(rows: list[dict]) -> list[dict[str, Any]]:
    return [
        {
            "id": r["id"],
            "title": r["title"] or "(untitled)",
            "tldr": r["tldr"] or "",
            "platform": r["source_platform"],
            "url": r["source_url"],
        }
        for r in rows
    ]


def _search_memory(args: dict[str, Any]) -> dict[str, Any]:
    from ..routers.search import _fts_search, _vec_search

    q = (args.get("query") or "").strip()
    k = int(args.get("k") or 8)
    mode = args.get("mode") or "hybrid"

    scores: dict[int, float] = {}
    if mode in ("hybrid", "lexical"):
        for row in _fts_search(q, k * 2):
            scores[row["id"]] = scores.get(row["id"], 0.0) + float(row["lex_score"])
    if mode in ("hybrid", "semantic"):
        for item_id, vs in _vec_search(q, k * 2):
            scores[item_id] = scores.get(item_id, 0.0) + vs

    ranked_ids = [i for i, _ in sorted(scores.items(), key=lambda kv: -kv[1])[:k]]
    if not ranked_ids:
        return {"hits": [], "note": "no matches"}
    placeholders = ",".join("?" * len(ranked_ids))
    rows = db.query_all(
        f"SELECT id, title, tldr, source_platform, source_url FROM items "
        f"WHERE id IN ({placeholders})",
        tuple(ranked_ids),
    )
    by_id = {r["id"]: r for r in rows}
    return {"hits": _tldrs_for_search([by_id[i] for i in ranked_ids if i in by_id])}


def _get_item(args: dict[str, Any]) -> dict[str, Any]:
    item_id = int(args.get("id"))
    row = db.query_one(
        "SELECT id, title, tldr, summary, raw_text, source_url, source_platform, created_at "
        "FROM items WHERE id=?",
        (item_id,),
    )
    if not row:
        return {"error": f"no item with id {item_id}"}
    return dict(row)


def _add_note(args: dict[str, Any]) -> dict[str, Any]:
    text = (args.get("text") or "").strip()
    if not text:
        return {"error": "text is required"}
    title = args.get("title")
    url = args.get("url")
    actor = args.get("_actor") or "mcp"

    item_id = create_pending_item(text=text, url=url, title=title)
    db.execute(
        "INSERT INTO episodes(item_id, actor, channel) VALUES(?,?,?)",
        (item_id, actor, "mcp"),
    )
    # Run synchronously so the agent gets the enriched item back in one turn.
    try:
        process_item(item_id, text=text, url=url, title=title)
    except Exception as e:  # noqa: BLE001
        return {"item_id": item_id, "status": "queued", "warning": str(e)}
    return {"item_id": item_id, "status": "ready"}


def _recall_facts(args: dict[str, Any]) -> dict[str, Any]:
    q = (args.get("query") or "").strip()
    k = int(args.get("k") or 10)
    if q:
        try:
            from ..embeddings import embed_one, vec_to_blob

            vec = embed_one(q)
            rows = db.query_all(
                """
                SELECT f.id, f.text, f.fact_type, f.confidence, f.item_id,
                       fv.distance
                  FROM facts_vec fv
                  JOIN facts f ON f.id = fv.fact_id
                 WHERE fv.embedding MATCH ?
                 ORDER BY fv.distance
                 LIMIT ?
                """,
                (vec_to_blob(vec), k),
            )
        except Exception:  # noqa: BLE001 — fall back to recency
            rows = db.query_all(
                "SELECT id, text, fact_type, confidence, item_id FROM facts "
                "ORDER BY last_seen_at DESC LIMIT ?",
                (k,),
            )
    else:
        rows = db.query_all(
            "SELECT id, text, fact_type, confidence, item_id FROM facts "
            "ORDER BY last_seen_at DESC LIMIT ?",
            (k,),
        )
    return {"facts": [dict(r) for r in rows]}


def _list_themes(args: dict[str, Any]) -> dict[str, Any]:
    rows = db.query_all(
        """
        SELECT t.name AS tag, COUNT(*) AS n
          FROM tags t JOIN item_tags it ON it.tag_id = t.id
         GROUP BY t.id
         ORDER BY n DESC
         LIMIT ?
        """,
        (int(args.get("k") or 12),),
    )
    return {"themes": [dict(r) for r in rows]}


def _delete_item(args: dict[str, Any]) -> dict[str, Any]:
    item_id = int(args.get("id"))
    if not db.query_one("SELECT 1 FROM items WHERE id=?", (item_id,)):
        return {"error": f"no item with id {item_id}"}
    # facts_vec is a vec0 virtual table, no FK cascade — drop fact vectors first.
    from ..ingest.pipeline import _delete_facts_for_item

    _delete_facts_for_item(item_id)
    db.execute("DELETE FROM items WHERE id=?", (item_id,))
    db.execute("DELETE FROM item_vectors WHERE item_id=?", (item_id,))
    return {"deleted": item_id}


# ── Registry ──────────────────────────────────────────────────────────────

def register_all() -> None:
    register(ToolSpec(
        name="search_memory",
        summary="Search the user's saved notes, articles, videos, and reels by meaning or keywords; returns short TLDRs.",
        description=(
            "Hybrid lexical+semantic search across every captured item. Returns "
            "compact TLDRs with item ids; use `get_item` to expand any single hit."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "natural-language query"},
                "k": {"type": "integer", "default": 8, "minimum": 1, "maximum": 50},
                "mode": {"type": "string", "enum": ["hybrid", "lexical", "semantic"], "default": "hybrid"},
            },
            "required": ["query"],
        },
        handler=_search_memory,
        state_predicates=("requires_items",),
    ))
    register(ToolSpec(
        name="get_item",
        summary="Fetch the full content (summary + raw text + metadata) of one saved item by id.",
        description="Returns the full body of a saved item — use only after a search hit looks promising.",
        input_schema={
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
        handler=_get_item,
        state_predicates=("requires_items",),
    ))
    register(ToolSpec(
        name="add_note",
        summary="Save a new note, link, or piece of text into the user's Second Brain.",
        description=(
            "Captures a URL or free-form text and runs the full enrichment pipeline "
            "(summary, tldr, tags, entities, embeddings). Use this any time the user "
            "shares something worth remembering."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "title": {"type": "string"},
                "url": {"type": "string"},
            },
            "required": ["text"],
        },
        handler=_add_note,
    ))
    register(ToolSpec(
        name="recall_facts",
        summary="Recall atomic facts the user has saved (preferences, identity, how-tos).",
        description=(
            "Atomic facts are short standalone sentences extracted from saved items "
            "(Mem0-style). Cheaper for agents than re-reading whole items."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
            },
        },
        handler=_recall_facts,
        state_predicates=("requires_facts",),
    ))
    register(ToolSpec(
        name="list_themes",
        summary="List the user's most-active topics (top tags).",
        description="Use to orient on what the user has been thinking about lately.",
        input_schema={
            "type": "object",
            "properties": {"k": {"type": "integer", "default": 12, "minimum": 1, "maximum": 50}},
        },
        handler=_list_themes,
        state_predicates=("requires_items",),
    ))
    register(ToolSpec(
        name="delete_item",
        summary="Permanently delete a saved item by id.",
        description="Destructive. Only call when the user explicitly asks to remove an item.",
        input_schema={
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
        handler=_delete_item,
        state_predicates=("requires_items",),
    ))


def serialise_result(result: dict[str, Any]) -> str:
    """Stable JSON for MCP `content[].text` field."""
    return json.dumps(result, ensure_ascii=False, default=str)
