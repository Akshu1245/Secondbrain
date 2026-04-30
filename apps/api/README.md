# Second Brain — API

FastAPI backend.

```bash
uv sync
uv run python -m app.cli init-db
uv run uvicorn app.main:app --reload --port 8000
```

Optional extras:

```bash
uv sync --extra whisper   # local audio transcription
uv sync --extra ocr       # on-screen text from video frames
uv sync --extra telegram  # Telegram bot inbox
```
