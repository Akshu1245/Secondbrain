"""Command-line entrypoints."""

from __future__ import annotations

import argparse
import json
import sys

from .db import init_db


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="second-brain")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db", help="Create the SQLite schema")

    job_p = sub.add_parser("run-jobs", help="Run nightly memory-upkeep jobs")
    job_p.add_argument(
        "--name", help="Single job to run (consolidate|decay|distill|rollup|reflect)"
    )

    args = parser.parse_args(argv)

    if args.cmd == "init-db":
        init_db()
        print("database initialised")
        return 0

    if args.cmd == "run-jobs":
        init_db()
        from .jobs.runner import run_all_jobs, run_job

        results = [run_job(args.name)] if args.name else run_all_jobs()
        print(json.dumps(results, indent=2, default=str))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
