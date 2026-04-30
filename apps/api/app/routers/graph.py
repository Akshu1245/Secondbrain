"""Knowledge graph: items <-> entities <-> tags."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from .. import db
from ..auth import require_token
from ..models import GraphEdge, GraphNode, GraphResponse

router = APIRouter(prefix="/api", tags=["graph"], dependencies=[Depends(require_token)])


@router.get("/graph", response_model=GraphResponse)
def graph(limit_items: int = Query(default=200, ge=1, le=1000)) -> GraphResponse:
    item_rows = db.query_all(
        "SELECT id, title, kind, source_platform FROM items WHERE status='ready' "
        "ORDER BY id DESC LIMIT ?",
        (limit_items,),
    )
    item_ids = [r["id"] for r in item_rows]

    nodes: list[GraphNode] = [
        GraphNode(
            id=f"item:{r['id']}",
            label=(r["title"] or f"Item {r['id']}")[:80],
            type="item",
            meta={"kind": r["kind"], "platform": r["source_platform"]},
        )
        for r in item_rows
    ]

    edges: list[GraphEdge] = []
    if item_ids:
        placeholder = ",".join("?" * len(item_ids))
        ent_rows = db.query_all(
            f"""
            SELECT ie.item_id, e.id AS entity_id, e.name, e.entity_type
              FROM item_entities ie
              JOIN entities e ON e.id = ie.entity_id
             WHERE ie.item_id IN ({placeholder})
            """,
            tuple(item_ids),
        )
        seen_entities: set[int] = set()
        for r in ent_rows:
            eid = r["entity_id"]
            if eid not in seen_entities:
                seen_entities.add(eid)
                nodes.append(
                    GraphNode(
                        id=f"entity:{eid}",
                        label=r["name"][:60],
                        type="entity",
                        meta={"entity_type": r["entity_type"]},
                    )
                )
            edges.append(
                GraphEdge(source=f"item:{r['item_id']}", target=f"entity:{eid}", kind="mentions")
            )

        tag_rows = db.query_all(
            f"""
            SELECT it.item_id, t.id AS tag_id, t.name
              FROM item_tags it
              JOIN tags t ON t.id = it.tag_id
             WHERE it.item_id IN ({placeholder})
            """,
            tuple(item_ids),
        )
        seen_tags: set[int] = set()
        for r in tag_rows:
            tid = r["tag_id"]
            if tid not in seen_tags:
                seen_tags.add(tid)
                nodes.append(
                    GraphNode(id=f"tag:{tid}", label=f"#{r['name']}", type="tag")
                )
            edges.append(
                GraphEdge(source=f"item:{r['item_id']}", target=f"tag:{tid}", kind="tagged")
            )

    return GraphResponse(nodes=nodes, edges=edges)
