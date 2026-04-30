"""Embeddings via fastembed (ONNX, no torch dep).

Falls back to a deterministic hashed bag-of-character-ngrams projection if
fastembed can't load (e.g. no internet to fetch the model). The fallback keeps
the sqlite-vec dimension stable so search keeps working — quality drops, but
the schema stays valid.
"""

from __future__ import annotations

import hashlib
import logging
import math
import struct
from typing import Iterable

from .config import settings

log = logging.getLogger(__name__)

_model = None
_use_fallback = False


def _load() -> None:
    global _model, _use_fallback
    if _model is not None or _use_fallback:
        return
    try:
        from fastembed import TextEmbedding

        _model = TextEmbedding(model_name=settings.embedding_model)
        log.info("loaded embedding model %s", settings.embedding_model)
    except Exception as e:  # noqa: BLE001
        log.warning("fastembed unavailable (%s) — using hashed fallback", e)
        _use_fallback = True


def embed(texts: list[str]) -> list[list[float]]:
    _load()
    if _model is not None:
        return [list(map(float, v)) for v in _model.embed(texts)]
    return [_hashed_embed(t, settings.embedding_dim) for t in texts]


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


def vec_to_blob(vec: Iterable[float]) -> bytes:
    """Pack a float vector to little-endian float32 bytes for sqlite-vec."""
    arr = list(vec)
    return struct.pack(f"<{len(arr)}f", *arr)


def _hashed_embed(text: str, dim: int) -> list[float]:
    """Hash-trick char-3gram embeddings. Deterministic, 0-cost, low quality."""
    text = (text or "").lower()
    if not text:
        return [0.0] * dim
    vec = [0.0] * dim
    padded = f"  {text}  "
    for i in range(len(padded) - 2):
        gram = padded[i : i + 3]
        h = hashlib.blake2b(gram.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        sign = 1.0 if h[4] & 1 else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]
