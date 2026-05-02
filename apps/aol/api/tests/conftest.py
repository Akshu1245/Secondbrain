"""Shared pytest fixtures for the AOL API tests.

Each test gets a fresh, isolated state directory (so ``store`` writes don't
leak between tests) and a fresh, freshly-imported ``app.main`` module so the
slowapi limiter starts with a clean per-IP counter for every test.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def aol_env(tmp_path, monkeypatch):
    """Return a callable that builds a TestClient with the given env vars."""

    def _build(**env: str) -> TestClient:
        # Each test gets its own state dir so reset / event writes don't bleed.
        monkeypatch.setenv("AOL_DATA_DIR", str(tmp_path / "runtime"))
        for k, v in env.items():
            if v is None:
                monkeypatch.delenv(k, raising=False)
            else:
                monkeypatch.setenv(k, v)

        # Force a fresh import so slowapi's in-process limiter and the
        # store module's cached state both reset between tests.
        for mod in [
            "app.main",
            "app.security",
            "app.store",
            "app.usage",
            "app.compute",
            "app.feedback",
            "app.context",
            "app.filter",
        ]:
            sys.modules.pop(mod, None)

        repo_root = Path(__file__).resolve().parents[1]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        main = importlib.import_module("app.main")
        return TestClient(main.app)

    return _build


@pytest.fixture()
def client(aol_env):
    """Default client: no admin token, generous rate limit."""
    return aol_env(
        AOL_ADMIN_TOKEN=None,
        AOL_ALLOWED_ORIGINS=None,
        AOL_RATE_LIMIT_DEFAULT="10000/minute",
        AOL_RATE_LIMIT_WRITE="10000/minute",
        AOL_RATE_LIMIT_ADMIN="10000/minute",
    )
