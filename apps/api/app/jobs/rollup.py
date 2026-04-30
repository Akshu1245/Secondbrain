"""GraphRAG-style community rollups.

Cluster ``items`` by shared-entity overlap, then ask the LLM provider for
a 1-paragraph summary of each cluster. Clusters become rows in
``communities`` so the UI / agents can surface "themes you've been
exploring" without re-reading the underlying items.

The clustering itself is a cheap union-find over the
``item_entities → entity → item_entities`` join, so we don't need a
real graph database. Limits per run keep the cost bounded.
"""

from __future__ import annotations

import json

from .. import db
from ..llm import get_provider

MAX_COMMUNITIES = 12
MIN_CLUSTER_SIZE = 3


class _UF:
    def __init__(self) -> None:
        self.p: dict[int, int] = {}

    def find(self, x: int) -> int:
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def _cluster_items() -> dict[int, list[int]]:
    pairs = db.query_all(
        """
        SELECT a.item_id AS a, b.item_id AS b
          FROM item_entities a
          JOIN item_entities b ON a.entity_id = b.entity_id AND a.item_id < b.item_id
        """
    )
    items = db.query_all("SELECT id FROM items WHERE status='ready'")
    uf = _UF()
    for it in items:
        uf.find(int(it["id"]))
    for p in pairs:
        uf.union(int(p["a"]), int(p["b"]))
    clusters: dict[int, list[int]] = {}
    for it in items:
        root = uf.find(int(it["id"]))
        clusters.setdefault(root, []).append(int(it["id"]))
    return {root: ids for root, ids in clusters.items() if len(ids) >= MIN_CLUSTER_SIZE}


def _label_and_summarise(item_ids: list[int]) -> tuple[str, str]:
    rows = db.query_all(
        f"SELECT id, title, tldr FROM items WHERE id IN ({','.join('?' * len(item_ids))})",
        tuple(item_ids),
    )
    tag_rows = db.query_all(
        f"""
        SELECT t.name AS tag, COUNT(*) AS n
          FROM item_tags it JOIN tags t ON t.id = it.tag_id
         WHERE it.item_id IN ({','.join('?' * len(item_ids))})
         GROUP BY t.id ORDER BY n DESC LIMIT 5
        """,
        tuple(item_ids),
    )
    label = ", ".join(r["tag"] for r in tag_rows) or f"Cluster of {len(item_ids)} items"

    body = "\n".join(f"- [{r['id']}] {r['title'] or ''} — {r['tldr'] or ''}" for r in rows[:30])
    provider = get_provider()
    try:
        res = provider.enrich(title=f"Theme: {label}", body=body, source_url=None)
        summary = (res.summary or res.tldr or "").strip()
    except Exception:  # noqa: BLE001
        summary = ""
    if not summary:
        summary = f"Theme covering {len(item_ids)} items, dominant tags: {label}."
    return label, summary


def run() -> dict:
    clusters = _cluster_items()
    if not clusters:
        return {"communities": 0, "detail": "no clusters"}

    # Build the new rows *first* (this is where LLM calls / DB lookups can
    # fail) and only swap them in inside an explicit transaction. The
    # connection is in autocommit mode, so DELETE + INSERT must be wrapped
    # in BEGIN/COMMIT to avoid readers seeing an empty `communities` table
    # if a later step throws.
    new_rows: list[tuple[str, str, str]] = []
    for ids in sorted(clusters.values(), key=lambda c: -len(c))[:MAX_COMMUNITIES]:
        label, summary = _label_and_summarise(ids)
        new_rows.append((label, summary, json.dumps(ids)))
    if not new_rows:
        return {"communities": 0, "detail": "no rows produced"}

    conn = db.get_conn()
    conn.execute("BEGIN")
    try:
        conn.execute("DELETE FROM communities")
        conn.executemany(
            "INSERT INTO communities(label, summary, member_ids, period_start, period_end) "
            "VALUES(?, ?, ?, datetime('now', '-30 days'), CURRENT_TIMESTAMP)",
            new_rows,
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return {"communities": len(new_rows), "detail": f"communities={len(new_rows)}"}
