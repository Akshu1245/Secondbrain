"""Job runner — entrypoint used by both the cron / CLI and the
`POST /api/jobs/run` endpoint."""

from __future__ import annotations

import logging
from typing import Callable

from .. import db
from . import consolidate, decay, distill, reflect, rollup

log = logging.getLogger(__name__)


_JOBS: dict[str, Callable[[], dict]] = {
    "consolidate": consolidate.run,
    "distill": distill.run,
    "decay": decay.run,
    "reflect": reflect.run,
    "rollup": rollup.run,
}


def run_job(name: str) -> dict:
    fn = _JOBS.get(name)
    if fn is None:
        return {"job": name, "status": "error", "detail": f"no such job: {name}"}
    cur = db.execute("INSERT INTO job_runs(job_name, status) VALUES(?, 'running')", (name,))
    run_id = cur.lastrowid
    try:
        result = fn() or {}
        detail = result.get("detail") or ""
        db.execute(
            "UPDATE job_runs SET status='ok', detail=?, finished_at=CURRENT_TIMESTAMP WHERE id=?",
            (detail, run_id),
        )
        return {"job": name, "status": "ok", **result}
    except Exception as e:  # noqa: BLE001
        log.exception("job %s failed", name)
        db.execute(
            "UPDATE job_runs SET status='error', detail=?, finished_at=CURRENT_TIMESTAMP WHERE id=?",
            (str(e)[:500], run_id),
        )
        return {"job": name, "status": "error", "detail": str(e)}


def run_all_jobs() -> list[dict]:
    """Order matters — consolidate first (so distill / rollup don't waste
    cycles on near-duplicates), reflect last (so it sees the cleaned-up corpus)."""
    return [run_job(n) for n in ("consolidate", "decay", "distill", "rollup", "reflect")]


def list_jobs() -> list[str]:
    return list(_JOBS.keys())
