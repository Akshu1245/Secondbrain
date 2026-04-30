"""Deterministic, dependency-light fallback enrichment.

Used when no LLM provider is reachable. Quality is obviously lower than a real
LLM, but keeps the app usable end-to-end with zero credentials.
"""

from __future__ import annotations

import re
from collections import Counter
from urllib.parse import urlparse

from .base import EnrichResult, ExtractedEntity, LLMProvider

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "while", "of", "at", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "s", "t", "can", "will", "just", "don", "should", "now", "i", "you",
    "your", "yours", "yourself", "yourselves", "we", "they", "them", "this", "that",
    "these", "those", "is", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "it", "its", "as", "also", "like", "really",
    "going", "make", "made", "use", "used", "using", "get", "got", "want", "wants",
    "need", "needs", "thing", "things",
}

_KNOWN_TOOLS = {
    "notion", "obsidian", "anki", "logseq", "raycast", "linear", "figma", "framer",
    "slack", "discord", "telegram", "whatsapp", "gmail", "google docs", "google drive",
    "dropbox", "github", "gitlab", "vscode", "vs code", "cursor", "windsurf", "claude",
    "chatgpt", "gpt-4", "gpt-4o", "gemini", "perplexity", "midjourney", "stable diffusion",
    "dalle", "dall-e", "runway", "elevenlabs", "descript", "canva", "photoshop",
    "premiere pro", "after effects", "davinci resolve", "capcut", "ableton",
    "fl studio", "logic pro", "blender", "unity", "unreal engine", "godot", "roblox",
    "next.js", "nextjs", "react", "vue", "svelte", "tailwind", "shadcn", "vercel",
    "netlify", "fly.io", "supabase", "firebase", "postgres", "postgresql", "mongodb",
    "redis", "sqlite", "qdrant", "pinecone", "weaviate", "milvus", "chroma",
    "langchain", "llamaindex", "haystack", "ollama", "huggingface", "hugging face",
    "openai", "anthropic", "openrouter", "replicate", "modal", "fastapi", "flask",
    "django", "express", "node.js", "deno", "bun", "rust", "python", "typescript",
    "kubernetes", "docker", "terraform", "aws", "gcp", "azure", "cloudflare",
    "youtube", "instagram", "tiktok", "twitter", "x.com", "reddit", "linkedin",
    "spotify", "apple music", "audible", "kindle", "goodreads",
}

_URL_RE = re.compile(r"https?://[^\s)>\]]+")
_HASHTAG_RE = re.compile(r"#([A-Za-z][\w-]{1,40})")
_PROPER_RE = re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){0,3})\b")


class FallbackProvider(LLMProvider):
    name = "fallback"

    def available(self) -> bool:
        return True

    def enrich(self, *, title: str, body: str, source_url: str | None = None) -> EnrichResult:
        text = (title + ". " + body).strip()
        sentences = _split_sentences(body or title)
        bullets = _top_sentences(sentences, n=3) or ([title] if title else ["(no content)"])
        summary = "- " + "\n- ".join(b.strip() for b in bullets)
        tldr = (sentences[0][:160] if sentences else (title or "")[:160]).strip() or "(no tldr)"
        tags = _auto_tags(text)
        entities = _extract_entities(text, source_url)
        return EnrichResult(
            summary=summary, tldr=tldr, tags=tags, entities=entities, provider="fallback"
        )


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return [p.strip() for p in parts if len(p.strip()) > 0]


def _top_sentences(sentences: list[str], n: int = 3) -> list[str]:
    if not sentences:
        return []
    # Score by word frequency (TextRank-lite).
    words: list[str] = []
    for s in sentences:
        for w in re.findall(r"[a-zA-Z][a-zA-Z'-]+", s.lower()):
            if w not in _STOPWORDS and len(w) > 2:
                words.append(w)
    freq = Counter(words)
    scored = []
    for idx, s in enumerate(sentences):
        toks = re.findall(r"[a-zA-Z][a-zA-Z'-]+", s.lower())
        score = sum(freq.get(t, 0) for t in toks if t not in _STOPWORDS) / max(len(toks), 1)
        # Prefer earlier sentences slightly.
        score *= 1.0 / (1.0 + idx * 0.05)
        scored.append((score, idx, s))
    scored.sort(key=lambda x: (-x[0], x[1]))
    chosen = sorted(scored[:n], key=lambda x: x[1])
    return [s for _, _, s in chosen]


def _auto_tags(text: str) -> list[str]:
    tags: list[str] = []
    for tag in _HASHTAG_RE.findall(text):
        tags.append(tag.lower())
    if len(tags) < 5:
        words = [w.lower() for w in re.findall(r"[a-zA-Z][a-zA-Z'-]{3,}", text)]
        words = [w for w in words if w not in _STOPWORDS]
        for w, _ in Counter(words).most_common(7 - len(tags)):
            tags.append(w)
    seen, dedup = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t)
            dedup.append(t)
    return dedup[:7]


def _extract_entities(text: str, source_url: str | None) -> list[ExtractedEntity]:
    out: dict[tuple[str, str], ExtractedEntity] = {}
    lower = text.lower()

    # Known tools / apps
    for tool in _KNOWN_TOOLS:
        if re.search(rf"(?<![\w.]){re.escape(tool)}(?![\w.])", lower):
            key = (tool, "tool")
            out[key] = ExtractedEntity(name=tool.title(), entity_type="tool")

    # URLs => websites
    for url in _URL_RE.findall(text):
        host = urlparse(url).netloc.lower().removeprefix("www.")
        if not host:
            continue
        key = (host, "website")
        out[key] = ExtractedEntity(name=host, entity_type="website", canonical_url=url)

    # Proper-noun chunks => candidate concepts/people. Cap to avoid noise.
    for m in _PROPER_RE.findall(text):
        if m.lower() in _STOPWORDS:
            continue
        if len(m) < 4 or len(m) > 50:
            continue
        key = (m, "concept")
        out.setdefault(key, ExtractedEntity(name=m, entity_type="concept"))
        if len(out) > 25:
            break

    return list(out.values())[:25]
