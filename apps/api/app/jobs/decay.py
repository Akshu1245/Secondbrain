"""Forgetting curve for atomic facts.

Each fact tracks `last_seen_at`, `recall_count`, and `confidence`. Recalling
a fact (via the `recall_facts` MCP tool) bumps `last_seen_at` and
`recall_count`; this nightly job decays `confidence` for facts that
haven't been touched recently. Unused facts fade — but we never delete
them, the user can always restore.

Algorithm (Ebbinghaus-ish):
  * If never recalled and older than 30d → confidence -= 0.1 per 30d
  * Floor at 0.05.
  * Touch `decayed_at` so we don't double-decay in a single window.
"""

from __future__ import annotations

from .. import db


def run() -> dict:
    rows = db.query_all(
        """
        SELECT id, confidence, recall_count,
               julianday('now') - julianday(COALESCE(decayed_at, last_seen_at)) AS age_days
          FROM facts
         WHERE merged_into IS NULL
        """
    )
    decayed = 0
    for r in rows:
        age = float(r["age_days"] or 0)
        if age < 30:
            continue
        steps = int(age // 30)
        decrement = 0.1 * steps * (1.0 if int(r["recall_count"]) == 0 else 0.5)
        new_conf = max(0.05, float(r["confidence"]) - decrement)
        if abs(new_conf - float(r["confidence"])) < 1e-6:
            continue
        db.execute(
            "UPDATE facts SET confidence = ?, decayed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_conf, r["id"]),
        )
        decayed += 1
    return {"decayed": decayed, "detail": f"decayed={decayed}"}
