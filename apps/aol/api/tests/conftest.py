"""Pytest config for the AOL backend.

Each test gets a clean, isolated runtime state so we don't pollute the real
on-disk JSON store. The session-wide tmpdir is set via ``AOL_DATA_DIR`` *before*
the ``app.store`` module is imported, since ``store.STATE_PATH`` is computed
at import time. The directory is removed in a session-scoped teardown so we
don't leak ``aol-tests-*`` directories across runs.
"""

from __future__ import annotations

import os
import shutil
import tempfile

import pytest

# Must run before any `from app import ...` in test modules.
_TMPDIR = tempfile.mkdtemp(prefix="aol-tests-")
os.environ["AOL_DATA_DIR"] = _TMPDIR


@pytest.fixture(scope="session", autouse=True)
def _cleanup_tmpdir():
    """Remove the per-session tmpdir after the suite finishes."""
    yield
    shutil.rmtree(_TMPDIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def fresh_state():
    """Reset the in-memory + on-disk state before every test."""
    from app import store

    store.reset()
    yield
    store.reset()
