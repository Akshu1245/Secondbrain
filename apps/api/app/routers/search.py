"""Hybrid search — FTS5 lexical + sqlite-vec semantic."""

from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, Query

from .. import db
from ..auth import require_token
from ..embeddings import embed_one, vec_to_blob
from ..models import SearchHit, SearchResponse
from .items import _row_to_item

router = APIRouter(prefix="/api", tags=["search"], dependencies=[Depends(require_token)])


@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(min_length=1),
    k: int = Query(default=20, ge=1, le=100),
    mode: str = Query(default="hybrid", pattern="^(hybrid|lexical|semantic)$"),
) -> SearchResponse:
    scores: dict[int, float] = defaultdict(float)
    snippets: dict[int, str] = {}

    if mode in ("hybrid", "lexical"):
        for row in _fts_search(q, k * 2):
            scores[row["id"]] += float(row["lex_score"])
            snippets[row["id"]] = row["snippet"] or ""

    if mode in ("hybrid", "semantic"):
        for item_id, vec_score in _vec_search(q, k * 2):
            scores[item_id] += vec_score

    ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:k]
    hits: list[SearchHit] = []
    for item_id, score in ranked:
        try:
            item = _row_to_item(item_id)
        except Exception:  # noqa: BLE001
            continue
        hits.append(SearchHit(item=item, score=round(float(score), 4), snippet=snippets.get(item_id)))
    return SearchResponse(query=q, hits=hits)


def _fts_search(q: str, k: int) -> list:
    # Build a permissive prefix query: every word becomes word*
    terms = [t for t in q.split() if t.strip()]
    if not terms:
        return []
    fts_q = " OR ".join(f'"{t.replace("\"", "")}"*' for t in terms)
    return db.query_all(
        """
        SELECT items.id        AS id,
               bm25(items_fts) AS bm25,
               -- bm25() returns <= 0; more negative == better match.
               -- Negate so higher == better, matching the vec score direction.
               (-1.0 * bm25(items_fts)) AS lex_score,
               snippet(items_fts, 1, '\x02', '\x03', '…', 12) AS snippet
          FROM items_fts
          JOIN items ON items.id = items_fts.rowid
         WHERE items_fts MATCH ?
         ORDER BY bm25 ASC
         LIMIT ?
        """,
        (fts_q, k),
    )


def _vec_search(q: str, k: int) -> list[tuple[int, float]]:
    try:
        vec = embed_one(q)
        rows = db.query_all(
            """
            SELECT item_id, distance
              FROM item_vectors
             WHERE embedding MATCH ?
             ORDER BY distance
             LIMIT ?
            """,
            (vec_to_blob(vec), k),
        )
    except Exception:  # noqa: BLE001
        return []
    return [(int(r["item_id"]), 1.0 / (1.0 + float(r["distance"]))) for r in rows]
