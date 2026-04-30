"""Ingestion orchestrator.

Stages:
  1. capture     — fetch URL / read note
  2. transcribe  — (optional) whisper on downloaded media
  3. enrich      — LLM summary, tldr, tags, entities (or fallback)
  4. embed       — store sentence embeddings for semantic search
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .. import db
from ..embeddings import embed_one, vec_to_blob
from ..events import publish_event
from ..llm import get_provider
from .capture import capture, detect_url
from .transcribe import transcribe

log = logging.getLogger(__name__)


def create_pending_item(*, text: str | None, url: str | None, title: str | None) -> int:
    """Insert a placeholder row immediately so the UI can show 'processing'."""
    src_url = url or detect_url(text or "")
    cur = db.execute(
        """
        INSERT INTO items (kind, source_url, source_platform, title, raw_text, status)
        VALUES ('note', ?, 'manual', ?, ?, 'pending')
        """,
        (src_url, title or (src_url or (text or "")[:80] or "Untitled"), text or ""),
    )
    item_id = cur.lastrowid
    _log_event(item_id, "queue", "ok", "queued")
    return item_id


def process_item(item_id: int, *, text: str | None, url: str | None, title: str | None) -> None:
    """Run the full pipeline for one item. Designed to be invoked from a BackgroundTask."""
    publish_event({"type": "item.processing", "item_id": item_id})
    db.execute("UPDATE items SET status='processing' WHERE id=?", (item_id,))
    try:
        # 1. capture
        cap = capture(url or text or "", given_title=title)
        _log_event(item_id, "capture", "ok", f"kind={cap.kind} platform={cap.platform}")

        body_parts = [cap.body or ""]

        # When the caller supplied BOTH a url and free-form text (e.g. Web Share
        # Target gives us page title + selected text alongside the URL), keep
        # the user's text so it's part of the summary / embedding / search.
        if url and text and text.strip() and text.strip() != url.strip():
            body_parts.append(text.strip())

        # 2. transcribe (if we got media)
        if cap.media_path:
            t = transcribe(cap.media_path)
            if t:
                body_parts.append(t)
                _log_event(item_id, "transcribe", "ok", f"len={len(t)}")
            else:
                _log_event(item_id, "transcribe", "skip", "no transcript")
        else:
            _log_event(item_id, "transcribe", "skip", "no media")

        body = "\n\n".join(b.strip() for b in body_parts if b)

        # 3. enrich
        provider = get_provider()
        enrich = provider.enrich(title=cap.title, body=body, source_url=cap.metadata.get("source_url"))
        _log_event(item_id, "enrich", "ok", f"provider={enrich.provider} entities={len(enrich.entities)}")

        db.execute(
            """
            UPDATE items
               SET kind=?, source_url=?, source_platform=?, title=?, author=?,
                   raw_text=?, summary=?, tldr=?, media_path=?, duration_sec=?,
                   metadata_json=?, updated_at=CURRENT_TIMESTAMP
             WHERE id=?
            """,
            (
                cap.kind,
                cap.metadata.get("source_url"),
                cap.platform,
                cap.title,
                cap.author,
                body,
                enrich.summary,
                enrich.tldr,
                cap.media_path,
                cap.duration_sec,
                json.dumps(cap.metadata, default=str),
                item_id,
            ),
        )
        _save_tags(item_id, enrich.tags)
        _save_entities(item_id, [(e.name, e.entity_type, e.description, e.canonical_url) for e in enrich.entities])

        # 4. embed (item-level)
        text_for_embed = "\n".join(filter(None, [cap.title, enrich.tldr, enrich.summary, body[:4000]]))
        item_vec: list[float] | None = None
        try:
            item_vec = embed_one(text_for_embed)
            db.execute(
                "INSERT OR REPLACE INTO item_vectors(item_id, embedding) VALUES(?, ?)",
                (item_id, vec_to_blob(item_vec)),
            )
            _log_event(item_id, "embed", "ok", f"dim={len(item_vec)}")
        except Exception as e:  # noqa: BLE001
            _log_event(item_id, "embed", "error", str(e))

        # 5. atomic facts (Mem0-style): one row + embedding per fact
        if enrich.facts:
            _save_facts(item_id, enrich.facts)
            _log_event(item_id, "facts", "ok", f"n={len(enrich.facts)}")

        # 6. semantic dedupe — flag near-duplicates so the user can merge
        if item_vec is not None:
            dup_id = _find_near_duplicate(item_id, item_vec, threshold=0.95)
            if dup_id is not None:
                _log_event(item_id, "dedupe", "warn", f"near-duplicate of item {dup_id}")

        db.execute("UPDATE items SET status='ready', error=NULL WHERE id=?", (item_id,))
        publish_event({"type": "item.ready", "item_id": item_id})
    except Exception as e:  # noqa: BLE001
        log.exception("pipeline failed for item %s", item_id)
        db.execute("UPDATE items SET status='failed', error=? WHERE id=?", (str(e)[:500], item_id))
        _log_event(item_id, "pipeline", "error", str(e))
        publish_event({"type": "item.failed", "item_id": item_id, "error": str(e)})


# ---------- helpers ----------

def _log_event(item_id: int, stage: str, status: str, detail: str | None = None) -> None:
    db.execute(
        "INSERT INTO job_events(item_id, stage, status, detail) VALUES(?,?,?,?)",
        (item_id, stage, status, detail),
    )


def _save_tags(item_id: int, tags: list[str]) -> None:
    db.execute("DELETE FROM item_tags WHERE item_id=?", (item_id,))
    for name in dict.fromkeys(t.strip().lower() for t in tags if t.strip()):
        db.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (name,))
        row = db.query_one("SELECT id FROM tags WHERE name=?", (name,))
        if row:
            db.execute(
                "INSERT OR IGNORE INTO item_tags(item_id, tag_id, source) VALUES(?,?, 'auto')",
                (item_id, row["id"]),
            )


def _save_entities(item_id: int, entities: list[tuple[str, str, Any, Any]]) -> None:
    db.execute("DELETE FROM item_entities WHERE item_id=?", (item_id,))
    seen: set[tuple[str, str]] = set()
    for name, etype, desc, url in entities:
        name = (name or "").strip()
        etype = (etype or "concept").strip().lower()
        if not name or (name.lower(), etype) in seen:
            continue
        seen.add((name.lower(), etype))
        db.execute(
            """
            INSERT INTO entities(name, entity_type, description, canonical_url)
            VALUES(?,?,?,?)
            ON CONFLICT(name, entity_type) DO UPDATE SET
                description = COALESCE(excluded.description, entities.description),
                canonical_url = COALESCE(excluded.canonical_url, entities.canonical_url)
            """,
            (name, etype, desc, url),
        )
        row = db.query_one("SELECT id FROM entities WHERE name=? AND entity_type=?", (name, etype))
        if row:
            db.execute(
                "INSERT OR IGNORE INTO item_entities(item_id, entity_id) VALUES(?,?)",
                (item_id, row["id"]),
            )


def _delete_facts_for_item(item_id: int) -> None:
    """Drop facts for an item *and* their vec entries. ``facts_vec`` is a vec0
    virtual table so it doesn't participate in foreign-key cascades — every
    caller that removes from ``facts`` must call this helper instead."""
    old = db.query_all("SELECT id FROM facts WHERE item_id=?", (item_id,))
    for fr in old:
        db.execute("DELETE FROM facts_vec WHERE fact_id=?", (fr["id"],))
    db.execute("DELETE FROM facts WHERE item_id=?", (item_id,))


def _save_facts(item_id: int, facts: list) -> None:
    _delete_facts_for_item(item_id)
    for f in facts:
        text = (getattr(f, "text", None) or "").strip()
        if not text:
            continue
        cur = db.execute(
            """
            INSERT INTO facts(item_id, text, fact_type, confidence)
            VALUES(?,?,?,?)
            """,
            (item_id, text, getattr(f, "fact_type", "general"), float(getattr(f, "confidence", 1.0))),
        )
        fact_id = cur.lastrowid
        try:
            v = embed_one(text)
            db.execute(
                "INSERT OR REPLACE INTO facts_vec(fact_id, embedding) VALUES(?, ?)",
                (fact_id, vec_to_blob(v)),
            )
        except Exception:  # noqa: BLE001 — embeddings are best-effort
            pass


def _find_near_duplicate(item_id: int, vec: list[float], *, threshold: float) -> int | None:
    """Return the id of an existing item whose embedding is ≥ threshold cosine
    to ``vec``, ignoring ``item_id`` itself. Returns None when no match.

    sqlite-vec's vec0 virtual tables only support `MATCH` for KNN queries —
    arbitrary `WHERE item_id != ?` filters are silently dropped — so we fetch
    the top-2 nearest neighbours and post-filter the self-match in Python.
    """
    try:
        rows = db.query_all(
            """
            SELECT item_id, distance
              FROM item_vectors
             WHERE embedding MATCH ?
             ORDER BY distance
             LIMIT 2
            """,
            (vec_to_blob(vec),),
        )
    except Exception:  # noqa: BLE001
        return None
    for row in rows:
        if int(row["item_id"]) == item_id:
            continue
        # sqlite-vec returns L2 distance for normalised vecs; map to cosine sim.
        d = float(row["distance"])
        cos_sim = 1.0 - (d * d) / 2.0
        if cos_sim >= threshold:
            return int(row["item_id"])
        return None
    return None
