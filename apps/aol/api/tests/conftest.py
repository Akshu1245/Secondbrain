"""Shared pytest fixtures.

Each test gets a fresh in-memory AOL state so memory / feedback / toggle
tests don't leak into each other.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture()
def _reset(tmp_path, monkeypatch):
    """Point AOL at a tmp data dir and re-seed from scratch."""
    monkeypatch.setenv("AOL_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(store, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(store, "_state", None)
    store.get_state()
    yield
    monkeypatch.setattr(store, "_state", None)


@pytest.fixture()
def client(_reset):
    return TestClient(app)
