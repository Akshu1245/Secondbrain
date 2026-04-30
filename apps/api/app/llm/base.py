"""LLM provider abstraction + auto-selection."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import lru_cache

from ..config import settings

log = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    name: str
    entity_type: str  # tool | app | website | book | person | place | concept
    description: str | None = None
    canonical_url: str | None = None


@dataclass
class AtomicFact:
    """Mem0-style standalone sentence: 'User prefers FastAPI for hobby projects.'"""
    text: str
    fact_type: str = "general"  # preference | identity | task | how_to | general
    confidence: float = 1.0


@dataclass
class EnrichResult:
    summary: str
    tldr: str
    tags: list[str] = field(default_factory=list)
    entities: list[ExtractedEntity] = field(default_factory=list)
    facts: list[AtomicFact] = field(default_factory=list)
    provider: str = "fallback"


class LLMProvider:
    name: str = "base"

    def available(self) -> bool:  # pragma: no cover - interface
        return False

    def enrich(self, *, title: str, body: str, source_url: str | None = None) -> EnrichResult:
        raise NotImplementedError


@lru_cache(maxsize=1)
def get_provider() -> LLMProvider:
    """Pick the best available LLM provider once per process."""
    from .fallback import FallbackProvider
    from .openai_compat import OpenAICompatProvider

    requested = (settings.llm_provider or "auto").lower()

    candidates: list[LLMProvider] = []
    if requested in ("auto", "openai") and settings.openai_api_key:
        candidates.append(
            OpenAICompatProvider(
                name="openai",
                base_url=settings.openai_base_url,
                api_key=settings.openai_api_key,
                model=settings.llm_model or "gpt-4o-mini",
            )
        )
    if requested in ("auto", "openrouter") and settings.openrouter_api_key:
        candidates.append(
            OpenAICompatProvider(
                name="openrouter",
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.openrouter_api_key,
                model=settings.llm_model or "google/gemma-3-12b-it:free",
            )
        )
    if requested in ("auto", "ollama"):
        candidates.append(
            OpenAICompatProvider(
                name="ollama",
                base_url=f"{settings.ollama_base_url.rstrip('/')}/v1",
                api_key="ollama",
                model=settings.llm_model or "gemma3:4b",
            )
        )

    for c in candidates:
        if c.available():
            log.info("LLM provider selected: %s (%s)", c.name, c.model)
            return c

    log.info("No LLM provider available — using extractive fallback")
    return FallbackProvider()
