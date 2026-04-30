"""OpenAI-compatible chat completion client.

Works with OpenAI, OpenRouter, Together, Ollama (`/v1`), vLLM, etc.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from .base import EnrichResult, ExtractedEntity, LLMProvider

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an information-extraction engine for a personal knowledge base.

Given a piece of saved content (a video transcript, article, or note), produce STRICT JSON with:

  - tldr:    one sentence, <= 160 chars
  - summary: 3 short bullet points joined by "\\n- " (start the first bullet with "- ")
  - tags:    3-7 lowercase, hyphenated topical tags
  - entities: every concrete tool / app / website / book / person / place / concept
              mentioned. Each is {name, entity_type, description}. entity_type ∈
              {tool, app, website, book, person, place, concept}.

Output JSON only, no preamble."""


class OpenAICompatProvider(LLMProvider):
    def __init__(self, *, name: str, base_url: str, api_key: str, model: str) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._available: bool | None = None

    def available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            r = httpx.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=3.0,
            )
            self._available = r.status_code < 500
        except Exception as e:  # noqa: BLE001
            log.debug("provider %s unavailable: %s", self.name, e)
            self._available = False
        return self._available

    def enrich(self, *, title: str, body: str, source_url: str | None = None) -> EnrichResult:
        # Truncate to ~12k chars to stay well under context windows of small models.
        body_trunc = body[:12_000]
        user_msg = f"TITLE: {title}\nSOURCE: {source_url or '-'}\n\nCONTENT:\n{body_trunc}"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        try:
            r = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=60.0,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            data = _safe_json(content)
        except Exception as e:  # noqa: BLE001
            log.warning("LLM call failed (%s): %s — falling back", self.name, e)
            from .fallback import FallbackProvider

            return FallbackProvider().enrich(title=title, body=body, source_url=source_url)

        entities = [
            ExtractedEntity(
                name=str(e.get("name", "")).strip(),
                entity_type=str(e.get("entity_type", "concept")).strip().lower(),
                description=(e.get("description") or None),
                canonical_url=(e.get("canonical_url") or None),
            )
            for e in (data.get("entities") or [])
            if e.get("name")
        ]
        return EnrichResult(
            summary=str(data.get("summary", "")).strip() or "(no summary)",
            tldr=str(data.get("tldr", "")).strip() or "(no tldr)",
            tags=[str(t).strip().lower() for t in (data.get("tags") or []) if t],
            entities=entities,
            provider=self.name,
        )


def _safe_json(text: str) -> dict[str, Any]:
    text = text.strip()
    # Some providers wrap JSON in ```json ... ```
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find the first {...} block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {}
