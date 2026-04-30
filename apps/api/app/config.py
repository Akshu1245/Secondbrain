"""Runtime configuration."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_data_dir() -> Path:
    # Render mounts persistent disks at a configurable path; honour it.
    env_path = os.environ.get("RENDER_DISK_PATH") or os.environ.get("DATA_DIR")
    return Path(env_path) if env_path else Path("data")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Storage — db_path / media_dir derive from data_dir at init time so they
    # track .env-provided overrides (pydantic-settings doesn't write back to
    # os.environ, so referencing _default_data_dir() at class definition time
    # would leave them out of sync).
    data_dir: Path = _default_data_dir()
    db_path: Path | None = None
    media_dir: Path | None = None

    # LLM
    llm_provider: str = "auto"  # auto | openai | openrouter | ollama | fallback
    llm_model: str = ""  # provider default if empty
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # Whisper
    whisper_model: str = "base"  # base, small, medium, large-v3
    enable_whisper: bool = False  # opt-in; CPU-only is slow

    # Web / CORS
    cors_origins: str = "*"

    # Optional Telegram
    telegram_bot_token: str = ""

    # Auth — single-user shared bearer token for the API (set in production)
    api_token: str = ""

    # Frontend serving (when running standalone w/o Vercel)
    serve_frontend: bool = False
    frontend_dir: Path = Path("web")

    def model_post_init(self, __context: object) -> None:
        if self.db_path is None:
            self.db_path = self.data_dir / "secondbrain.db"
        if self.media_dir is None:
            self.media_dir = self.data_dir / "media"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        assert self.media_dir is not None
        self.media_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
