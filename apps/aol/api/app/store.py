"""Single-file JSON store for the AOL MVP.

Why JSON, not SQLite: the spec says "Local JSON / mock database", and the
demo flow is fully observable when the data lives in a file you can `cat`.
This module is the *only* place that touches disk.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any


def _resolve_seed_path() -> Path:
    """Find ``seed.json`` whether we're running from the monorepo (where it
    lives at ``<repo>/data/seed.json``) or from a packaged container build
    where the only thing shipped is ``apps/api`` (and the seed is bundled
    next to the package at ``app/data/seed.json``)."""
    here = Path(__file__).resolve()
    candidates = [
        # Bundled with the package (production / fly.io image).
        here.parent / "data" / "seed.json",
        # Monorepo dev layout: apps/api/app/store.py → repo root /data/seed.json
        here.parents[3] / "data" / "seed.json" if len(here.parents) >= 4 else None,
    ]
    for c in candidates:
        if c is not None and c.exists():
            return c
    # Last resort: clearer error than IndexError on parents[3].
    raise FileNotFoundError(
        f"could not locate seed.json (looked in {[str(c) for c in candidates if c]})"
    )


SEED_PATH = _resolve_seed_path()
# Runtime state path is configurable so the deployed container can write to a
# writable location (the bundled `app/` dir is mounted read-only by some
# platforms).
STATE_PATH = Path(
    os.environ.get("AOL_DATA_DIR", str(SEED_PATH.parent / "runtime"))
) / "state.json"

_lock = threading.RLock()
_state: dict[str, Any] | None = None


def _bootstrap() -> dict[str, Any]:
    """Materialise the runtime state from the seed if it doesn't exist."""
    seed = json.loads(SEED_PATH.read_text())
    return {
        "features": {f["id"]: dict(f, enabled=f["default_on"]) for f in seed["features"]},
        "user_prefs": dict(seed["user_prefs"]),
        "events": [],          # usage events (chronological)
        "feedback": [],        # explicit user feedback
        "compute_log": [],     # routing decisions (most recent first)
        "version": 1,
    }


def get_state() -> dict[str, Any]:
    global _state
    with _lock:
        if _state is None:
            STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            if STATE_PATH.exists():
                try:
                    _state = json.loads(STATE_PATH.read_text())
                except json.JSONDecodeError:
                    _state = _bootstrap()
            else:
                _state = _bootstrap()
        return _state


def save() -> None:
    with _lock:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(get_state(), indent=2, default=str))


def reset() -> None:
    """Wipe runtime state and re-seed. Used by the demo's `Reset` button."""
    global _state
    with _lock:
        _state = _bootstrap()
        save()
