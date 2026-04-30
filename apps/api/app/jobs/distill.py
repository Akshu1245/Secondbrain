"""Active distillation — rewrite stale item TLDRs tighter.

Picks items older than 30d whose TLDR is longer than 12 words and asks the
LLM provider for a tighter version. Cap per run is 50 items so the job
stays under a minute even with a remote LLM.

The fallback provider just truncates to the first 18 words — still
useful for keeping the corpus lean even without an LLM key.
"""

from __future__ import annotations

import re

from .. import db
from ..llm import get_provider

CAP = 50


def _shrink(text: str, words: int = 18) -> str:
    parts = re.split(r"\s+", (text or "").strip())
    if len(parts) <= words:
        return text or ""
    return " ".join(parts[:words]).rstrip(",.;:") + "…"


def run() -> dict:
    rows = db.query_all(
        """
        SELECT id, title, tldr, summary, raw_text
          FROM items
         WHERE status = 'ready'
           AND tldr IS NOT NULL
           AND length(tldr) > 80
           AND julianday('now') - julianday(updated_at) > 30
         ORDER BY updated_at ASC
         LIMIT ?
        """,
        (CAP,),
    )
    if not rows:
        return {"distilled": 0, "detail": "nothing stale"}

    provider = get_provider()
    distilled = 0
    for r in rows:
        old = r["tldr"] or ""
        try:
            res = provider.enrich(
                title=r["title"] or "",
                body=(r["summary"] or "") + "\n\n" + (r["raw_text"] or "")[:2000],
                source_url=None,
            )
            new = (res.tldr or "").strip()
        except Exception:  # noqa: BLE001
            new = ""
        if not new or len(new) >= len(old):
            new = _shrink(old)
        if new and new != old:
            db.execute(
                "UPDATE items SET tldr = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new, r["id"]),
            )
            distilled += 1
    return {"distilled": distilled, "detail": f"distilled={distilled}/{len(rows)}"}
