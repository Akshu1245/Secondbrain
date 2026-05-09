"""Top-level entry point so deploy tooling that expects ``main:app`` at
the project root can discover the FastAPI instance. The actual app is
defined in ``app/main.py``."""

from app.main import app  # noqa: F401
