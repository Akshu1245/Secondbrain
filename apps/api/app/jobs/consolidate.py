"""Memory consolidation — merge near-duplicate items.

Whereas v1's ingest pipeline only *warns* about ≥0.95 cosine matches, this
job actually consolidates them: keeps the older item as the canonical
record, unions tags + facts + episodes from the duplicate(s), records a
`merged_into` link in `memory_links`, and deletes the loser cleanly.

Runs in O(items × top-1 vector lookup); cheap.
"""

from __future__ import annotations

from .. import db

THRESHOLD = 0.95


def _cos_from_l2(d: float) -> float:
    return 1.0 - (d * d) / 2.0


def _merge(canonical_id: int, loser_id: int) -> None:
    """Move every reference from loser → canonical, then drop the loser."""
    # Tags
    db.execute(
        "INSERT OR IGNORE INTO item_tags(item_id, tag_id, source) "
        "SELECT ?, tag_id, source FROM item_tags WHERE item_id = ?",
        (canonical_id, loser_id),
    )
    # Entities
    db.execute(
        "INSERT OR IGNORE INTO item_entities(item_id, entity_id, confidence, context) "
        "SELECT ?, entity_id, confidence, context FROM item_entities WHERE item_id = ?",
        (canonical_id, loser_id),
    )
    # Facts (re-point — fact text might be unique to the loser, keep it)
    db.execute("UPDATE facts SET item_id = ? WHERE item_id = ?", (canonical_id, loser_id))
    # Episodes
    db.execute("UPDATE episodes SET item_id = ? WHERE item_id = ?", (canonical_id, loser_id))
    # Record the merge as an explicit memory link before destroying the row.
    db.execute(
        "INSERT OR IGNORE INTO memory_links(src_kind, src_id, dst_kind, dst_id, relation) "
        "VALUES('item', ?, 'item', ?, 'merged_into')",
        (loser_id, canonical_id),
    )
    # Drop the loser. CASCADE handles item_tags/item_entities/job_events that
    # weren't migrated; item_vectors and facts_vec need explicit cleanup.
    fact_rows = db.query_all("SELECT id FROM facts WHERE item_id = ?", (loser_id,))
    for fr in fact_rows:
        db.execute("DELETE FROM facts_vec WHERE fact_id = ?", (fr["id"],))
    db.execute("DELETE FROM item_vectors WHERE item_id = ?", (loser_id,))
    db.execute("DELETE FROM items WHERE id = ?", (loser_id,))


def run() -> dict:
    rows = db.query_all(
        "SELECT iv.item_id, iv.embedding FROM item_vectors iv "
        "JOIN items i ON i.id = iv.item_id WHERE i.status = 'ready' ORDER BY iv.item_id"
    )
    merged = 0
    seen: set[int] = set()
    for r in rows:
        item_id = int(r["item_id"])
        if item_id in seen:
            continue
        try:
            cands = db.query_all(
                "SELECT item_id, distance FROM item_vectors "
                "WHERE embedding MATCH ? ORDER BY distance LIMIT 4",
                (r["embedding"],),
            )
        except Exception:  # noqa: BLE001
            continue
        for c in cands:
            other = int(c["item_id"])
            if other == item_id or other in seen:
                continue
            sim = _cos_from_l2(float(c["distance"]))
            if sim < THRESHOLD:
                continue
            # Always keep the older (lower-id) item as canonical.
            canonical, loser = sorted((item_id, other))
            _merge(canonical, loser)
            seen.add(loser)
            merged += 1
    return {"merged": merged, "detail": f"merged={merged}"}
