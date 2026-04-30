"""Reflective memory — the brain dreaming.

Every run, we read the last 7 days of items + facts and ask the LLM to
write 1–5 *meta-facts* about what the user has been thinking about. These
are stored in `reflections`, separate from the user's atomic facts so
they don't pollute downstream search.

If no LLM key is configured the fallback provider yields a coarse
heuristic: top 5 most-frequent tags become a single reflection.
"""

from __future__ import annotations

from .. import db
from ..llm import get_provider
from ..llm.base import LLMProvider


def _heuristic_reflection() -> str | None:
    rows = db.query_all(
        """
        SELECT t.name AS tag, COUNT(*) AS n
          FROM item_tags it
          JOIN tags t ON t.id = it.tag_id
          JOIN items i ON i.id = it.item_id
         WHERE julianday('now') - julianday(i.created_at) <= 7
         GROUP BY t.id
         ORDER BY n DESC
         LIMIT 5
        """
    )
    if not rows:
        return None
    tags = ", ".join(r["tag"] for r in rows)
    return f"Over the last 7 days the dominant themes were: {tags}."


def _llm_reflection(provider: LLMProvider) -> list[str]:
    items = db.query_all(
        """
        SELECT id, title, tldr
          FROM items
         WHERE julianday('now') - julianday(created_at) <= 7
         ORDER BY id DESC
         LIMIT 80
        """
    )
    facts = db.query_all(
        """
        SELECT text, fact_type
          FROM facts
         WHERE julianday('now') - julianday(created_at) <= 7
         ORDER BY id DESC
         LIMIT 80
        """
    )
    if not items and not facts:
        return []
    body_lines = ["Recent items:"]
    body_lines += [f"- [{r['id']}] {r['title'] or '(untitled)'} — {r['tldr'] or ''}" for r in items]
    body_lines.append("\nRecent facts:")
    body_lines += [f"- ({r['fact_type']}) {r['text']}" for r in facts]
    body = "\n".join(body_lines)
    try:
        res = provider.enrich(
            title="Reflect on the week",
            body=body,
            source_url=None,
        )
        # We piggyback on the standard enrichment surface — the TLDR + each
        # AtomicFact text becomes a separate reflection.
        out: list[str] = []
        if res.tldr:
            out.append(res.tldr.strip())
        for f in (res.facts or [])[:4]:
            text = (getattr(f, "text", "") or "").strip()
            if text:
                out.append(text)
        return out
    except Exception:  # noqa: BLE001
        return []


def run() -> dict:
    provider = get_provider()
    reflections = _llm_reflection(provider)
    if not reflections:
        h = _heuristic_reflection()
        if h:
            reflections = [h]
    for text in reflections:
        db.execute(
            "INSERT INTO reflections(text, period_start, period_end, confidence) "
            "VALUES(?, datetime('now', '-7 days'), CURRENT_TIMESTAMP, ?)",
            (text, 0.6),
        )
    return {"wrote": len(reflections), "detail": f"reflections={len(reflections)}"}
