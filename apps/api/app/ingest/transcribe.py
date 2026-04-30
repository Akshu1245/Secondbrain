"""Audio transcription stage — only runs if faster-whisper is installed and enabled."""

from __future__ import annotations

import logging
from pathlib import Path

from ..config import settings

log = logging.getLogger(__name__)

_model = None
_loaded = False


def _load() -> None:
    global _model, _loaded
    if _loaded:
        return
    _loaded = True
    if not settings.enable_whisper:
        return
    try:
        from faster_whisper import WhisperModel

        _model = WhisperModel(settings.whisper_model, device="auto", compute_type="auto")
        log.info("loaded faster-whisper model %s", settings.whisper_model)
    except Exception as e:  # noqa: BLE001
        log.warning("faster-whisper unavailable: %s", e)
        _model = None


def transcribe(media_path: str | Path) -> str:
    """Return plain-text transcript of an audio/video file, or '' if unavailable."""
    _load()
    if _model is None:
        return ""
    try:
        segments, _info = _model.transcribe(str(media_path), beam_size=1, vad_filter=True)
        return " ".join(seg.text.strip() for seg in segments if seg.text)
    except Exception as e:  # noqa: BLE001
        log.warning("transcription failed for %s: %s", media_path, e)
        return ""
