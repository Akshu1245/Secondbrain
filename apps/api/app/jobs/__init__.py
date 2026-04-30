"""Memory upkeep jobs.

These are the brain's "sleep" — tasks that run on a schedule (or on demand
via `POST /api/jobs/run`) to keep the corpus dense, accurate, and useful:

  * **consolidate** — merges near-duplicate items, unions tags, links episodes,
    keeps the best summary. Replaces v1's "warn on duplicate" with real merging.
  * **distill**     — rewrites stale TLDRs tighter so total token cost stays
    flat as the corpus grows for years.
  * **decay**       — bumps last_seen on recalled facts, fades unrecalled ones.
  * **reflect**     — LLM reads the last N days of items + facts and writes
    *meta-facts* into `reflections`.
  * **rollup**      — GraphRAG-style: cluster items by entity overlap and
    write a `communities` row per cluster.
"""

from .runner import run_job, run_all_jobs

__all__ = ["run_job", "run_all_jobs"]
