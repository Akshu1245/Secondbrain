"""SQLite + sqlite-vec connection management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Prefer pysqlite3 (modern SQLite + extension loading) when available.
# Stock CPython on Ubuntu is built without `--enable-loadable-sqlite-extensions`,
# so the bundled `sqlite3` cannot load `sqlite-vec`.
try:
    import pysqlite3 as sqlite3  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - mac/windows path
    import sqlite3  # type: ignore[no-redef]

import sqlite_vec

from .config import settings

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def _connect(path: Path | str | None = None) -> sqlite3.Connection:
    db_path = Path(path) if path else settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
        detect_types=sqlite3.PARSE_DECLTYPES,
        isolation_level=None,  # autocommit; we use explicit transactions
    )
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = _connect()
    return _conn


def init_db() -> None:
    """Create schema if missing."""
    conn = get_conn()
    schema = _SCHEMA_PATH.read_text()
    # sqlite-vec virtual tables can't run inside a transaction with other DDL,
    # so just executescript — autocommit is on.
    conn.executescript(schema)
    _apply_migrations(conn)


def _apply_migrations(conn: sqlite3.Connection) -> None:
    """Idempotent ALTER TABLE migrations for columns that can't go in
    `CREATE TABLE IF NOT EXISTS` without losing data on existing rows."""
    fact_cols = {row["name"] for row in conn.execute("PRAGMA table_info(facts)").fetchall()}
    if "recall_count" not in fact_cols:
        conn.execute("ALTER TABLE facts ADD COLUMN recall_count INTEGER NOT NULL DEFAULT 0")
    if "decayed_at" not in fact_cols:
        conn.execute("ALTER TABLE facts ADD COLUMN decayed_at TIMESTAMP")
    if "merged_into" not in fact_cols:
        conn.execute("ALTER TABLE facts ADD COLUMN merged_into INTEGER")


def query_all(sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    return list(get_conn().execute(sql, params).fetchall())


def query_one(sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    return get_conn().execute(sql, params).fetchone()


def execute(sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
    return get_conn().execute(sql, params)


def executemany(sql: str, seq: list[tuple[Any, ...]]) -> sqlite3.Cursor:
    return get_conn().executemany(sql, seq)
