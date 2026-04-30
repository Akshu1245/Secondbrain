"""Command-line entrypoints."""

from __future__ import annotations

import argparse
import sys

from .db import init_db


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="second-brain")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db", help="Create the SQLite schema")
    args = parser.parse_args(argv)

    if args.cmd == "init-db":
        init_db()
        print("database initialised")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
