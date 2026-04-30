"""Memory-upkeep job endpoints.

These endpoints are how a cron / Render scheduled job (or you, manually)
trigger the brain's "sleep cycle" — consolidate / decay / distill / rollup /
reflect. They're idempotent and safe to re-run.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import db
from ..auth import require_token
from ..jobs.runner import list_jobs, run_all_jobs, run_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"], dependencies=[Depends(require_token)])


@router.get("")
def list_job_state() -> dict:
    rows = db.query_all(
        "SELECT job_name, status, detail, started_at, finished_at "
        "FROM job_runs ORDER BY id DESC LIMIT 50"
    )
    return {"available": list_jobs(), "recent": [dict(r) for r in rows]}


@router.post("/run")
def run(name: str | None = None) -> dict:
    """Run one job by name, or the full nightly suite if name is omitted."""
    if name:
        if name not in list_jobs():
            raise HTTPException(status_code=404, detail=f"unknown job: {name}")
        return {"results": [run_job(name)]}
    return {"results": run_all_jobs()}
