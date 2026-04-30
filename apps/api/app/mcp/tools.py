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
    """Multi-hop fact recall.

    Phase 1 — direct: cosine search over `facts_vec` for the query.
    Phase 2 — neighbourhood: for each direct hit, pull *sibling* facts
              from the same item plus facts from items that share
              entities (HippoRAG-style 2-hop walk).
    Each recalled fact bumps `recall_count` + `last_seen_at` so the
    nightly decay job spares it.
    """
    q = (args.get("query") or "").strip()
    k = int(args.get("k") or 10)
    multi_hop = bool(args.get("multi_hop", True))

    direct: list[dict] = []
    if q:
        try:
            from ..embeddings import embed_one, vec_to_blob

            vec = embed_one(q)
            rows = db.query_all(
                """
                SELECT f.id, f.text, f.fact_type, f.confidence, f.item_id,
                       fv.distance, f.recall_count
                  FROM facts_vec fv
                  JOIN facts f ON f.id = fv.fact_id
                 WHERE fv.embedding MATCH ?
                   AND f.merged_into IS NULL
                 ORDER BY fv.distance
                 LIMIT ?
                """,
                (vec_to_blob(vec), k),
            )
            direct = [dict(r) | {"hop": 0} for r in rows]
        except Exception:  # noqa: BLE001 — fall back to recency
            rows = db.query_all(
                "SELECT id, text, fact_type, confidence, item_id, recall_count FROM facts "
                "WHERE merged_into IS NULL ORDER BY last_seen_at DESC LIMIT ?",
                (k,),
            )
            direct = [dict(r) | {"hop": 0} for r in rows]
    else:
        rows = db.query_all(
            "SELECT id, text, fact_type, confidence, item_id, recall_count FROM facts "
            "WHERE merged_into IS NULL ORDER BY last_seen_at DESC LIMIT ?",
            (k,),
        )
        direct = [dict(r) | {"hop": 0} for r in rows]

    hits: list[dict] = list(direct)
    if multi_hop and direct:
        seed_item_ids = sorted({int(r["item_id"]) for r in direct if r.get("item_id")})
        seen_fact_ids = {int(r["id"]) for r in direct}
        if seed_item_ids:
            placeholders = ",".join("?" * len(seed_item_ids))
            # Hop 1 — sibling facts on the same items
            sibling = db.query_all(
                f"""
                SELECT id, text, fact_type, confidence, item_id, recall_count
                  FROM facts
                 WHERE item_id IN ({placeholders})
                   AND merged_into IS NULL
                 ORDER BY confidence DESC, last_seen_at DESC
                """,
                tuple(seed_item_ids),
            )
            for r in sibling:
                if int(r["id"]) in seen_fact_ids:
                    continue
                hits.append(dict(r) | {"hop": 1})
                seen_fact_ids.add(int(r["id"]))
            # Hop 2 — facts on items sharing an entity with any seed item
            entity_neighbours = db.query_all(
                f"""
                SELECT DISTINCT b.item_id AS nb_item
                  FROM item_entities a
                  JOIN item_entities b ON a.entity_id = b.entity_id
                 WHERE a.item_id IN ({placeholders})
                   AND b.item_id NOT IN ({placeholders})
                """,
                tuple(seed_item_ids + seed_item_ids),
            )
            nb_ids = sorted({int(r["nb_item"]) for r in entity_neighbours})
            if nb_ids:
                ph2 = ",".join("?" * len(nb_ids))
                hop2 = db.query_all(
                    f"""
                    SELECT id, text, fact_type, confidence, item_id, recall_count
                      FROM facts
                     WHERE item_id IN ({ph2})
                       AND merged_into IS NULL
                     ORDER BY confidence DESC, last_seen_at DESC
                     LIMIT ?
                    """,
                    tuple(list(nb_ids) + [k]),
                )
                for r in hop2:
                    if int(r["id"]) in seen_fact_ids:
                        continue
                    hits.append(dict(r) | {"hop": 2})
                    seen_fact_ids.add(int(r["id"]))

    hits = hits[: max(k * 3, k)]
    if hits:
        ids = [int(h["id"]) for h in hits]
        ph = ",".join("?" * len(ids))
        db.execute(
            f"UPDATE facts SET recall_count = recall_count + 1, "
            f"last_seen_at = CURRENT_TIMESTAMP WHERE id IN ({ph})",
            tuple(ids),
        )
    return {"facts": hits, "hops_used": int(multi_hop)}


def _recall_skill(args: dict[str, Any]) -> dict[str, Any]:
    q = (args.get("query") or "").strip()
    k = int(args.get("k") or 3)
    if q:
        try:
            from ..embeddings import embed_one, vec_to_blob

            vec = embed_one(q)
            rows = db.query_all(
                """
                SELECT s.id, s.name, s.summary, s.body, s.use_count, sv.distance
                  FROM skills_vec sv
                  JOIN skills s ON s.id = sv.skill_id
                 WHERE sv.embedding MATCH ?
                 ORDER BY sv.distance
                 LIMIT ?
                """,
                (vec_to_blob(vec), k),
            )
        except Exception:  # noqa: BLE001
            rows = db.query_all(
                "SELECT id, name, summary, body, use_count FROM skills "
                "ORDER BY use_count DESC LIMIT ?",
                (k,),
            )
    else:
        rows = db.query_all(
            "SELECT id, name, summary, body, use_count FROM skills "
            "ORDER BY use_count DESC LIMIT ?",
            (k,),
        )
    if rows:
        ids = [int(r["id"]) for r in rows]
        ph = ",".join("?" * len(ids))
        db.execute(
            f"UPDATE skills SET use_count = use_count + 1 WHERE id IN ({ph})",
            tuple(ids),
        )
    return {"skills": [dict(r) for r in rows]}


def _recall_episodes(args: dict[str, Any]) -> dict[str, Any]:
    actor = args.get("actor")
    channel = args.get("channel")
    days = int(args.get("days") or 7)
    k = int(args.get("k") or 25)
    where = ["julianday('now') - julianday(e.created_at) <= ?"]
    params: list = [days]
    if actor:
        where.append("e.actor = ?")
        params.append(actor)
    if channel:
        where.append("e.channel = ?")
        params.append(channel)
    rows = db.query_all(
        f"""
        SELECT e.id, e.actor, e.channel, e.note, e.created_at,
               i.id AS item_id, i.title, i.tldr, i.source_url
          FROM episodes e
          LEFT JOIN items i ON i.id = e.item_id
         WHERE {' AND '.join(where)}
         ORDER BY e.id DESC
         LIMIT ?
        """,
        tuple(params + [k]),
    )
    return {"episodes": [dict(r) for r in rows]}


def _list_communities(args: dict[str, Any]) -> dict[str, Any]:
    rows = db.query_all(
        "SELECT id, label, summary, member_ids, period_start, period_end "
        "FROM communities ORDER BY id DESC LIMIT ?",
        (int(args.get("k") or 12),),
    )
    return {"communities": [dict(r) for r in rows]}


def _list_reflections(args: dict[str, Any]) -> dict[str, Any]:
    rows = db.query_all(
        "SELECT id, text, period_start, period_end, confidence, created_at "
        "FROM reflections ORDER BY id DESC LIMIT ?",
        (int(args.get("k") or 10),),
    )
    return {"reflections": [dict(r) for r in rows]}


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
        summary="Recall atomic facts the user has saved (preferences, identity, how-tos); walks 2 hops by default.",
        description=(
            "Atomic facts are short standalone sentences extracted from saved items "
            "(Mem0-style). When `multi_hop=true` (default) we also pull sibling facts "
            "from the same items and entity-linked items (HippoRAG-style)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
                "multi_hop": {"type": "boolean", "default": True},
            },
        },
        handler=_recall_facts,
        state_predicates=("requires_facts",),
    ))
    register(ToolSpec(
        name="recall_skill",
        summary="Recall procedural how-to skills the user has saved (e.g. 'how I deploy').",
        description=(
            "Skills are verbatim procedural-memory entries the agent should quote. "
            "Use this for deployment recipes, debugging playbooks, repeatable processes."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "k": {"type": "integer", "default": 3, "minimum": 1, "maximum": 20},
            },
        },
        handler=_recall_skill,
    ))
    register(ToolSpec(
        name="recall_episodes",
        summary="Look up where saved items came from (which agent, device, channel) over a recent window.",
        description=(
            "Episodic provenance: 'what did I save from Claude Code this week?' or "
            "'what did I share into Second Brain from my phone today?'."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "actor": {"type": "string"},
                "channel": {"type": "string"},
                "days": {"type": "integer", "default": 7, "minimum": 1, "maximum": 365},
                "k": {"type": "integer", "default": 25, "minimum": 1, "maximum": 200},
            },
        },
        handler=_recall_episodes,
    ))
    register(ToolSpec(
        name="list_communities",
        summary="List GraphRAG-style theme summaries written by the nightly rollup job.",
        description="Each row is a coherent cluster of related items with an LLM-written summary.",
        input_schema={
            "type": "object",
            "properties": {"k": {"type": "integer", "default": 12, "minimum": 1, "maximum": 50}},
        },
        handler=_list_communities,
    ))
    register(ToolSpec(
        name="list_reflections",
        summary="Show meta-facts the brain wrote about itself in the latest reflection job.",
        description="Reflections are short LLM observations about the user's recent thinking patterns.",
        input_schema={
            "type": "object",
            "properties": {"k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50}},
        },
        handler=_list_reflections,
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
