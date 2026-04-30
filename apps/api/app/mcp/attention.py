"""Tool Attention router — implements the three primitives from
Sadani & Kumar (Infrrd.ai, April 2026), "Tool Attention Is All You Need":

  1. Intent–Schema Overlap (ISO) — cosine similarity between the embedded
     intent and each tool's embedded summary.
  2. State-aware gating — drop tools whose preconditions aren't met (cheap;
     applied before scoring).
  3. Two-phase lazy schema loading — return only the top-k full schemas;
     other tools stay as one-line summaries to keep the per-turn token
     budget far below the ~70% context fracture point.

For the small Second Brain MCP surface (≈8 tools) this is mostly belt-and-
braces, but the same router is intended to scale to dozens of tools as we
add more memory primitives without exploding agent context cost.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..embeddings import embed_one
from .registry import ToolSpec, all_tools


@dataclass
class GateContext:
    item_count: int = 0
    fact_count: int = 0


def _state_ok(spec: ToolSpec, ctx: GateContext) -> bool:
    for p in spec.state_predicates:
        if p == "requires_items" and ctx.item_count == 0:
            return False
        if p == "requires_facts" and ctx.fact_count == 0:
            return False
    return True


def _cos(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(n):
        x = a[i]
        y = b[i]
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / ((na**0.5) * (nb**0.5))


@dataclass
class AttentionDecision:
    expanded: list[ToolSpec]   # tools whose full schema goes in context
    summarised: list[ToolSpec]  # tools that stay as one-line summaries
    iso_scores: dict[str, float]


def attend(intent: str, *, k: int = 4, ctx: GateContext | None = None,
           candidates: Iterable[ToolSpec] | None = None) -> AttentionDecision:
    """Run the full Tool Attention pipeline on the registry."""
    ctx = ctx or GateContext()
    pool = list(candidates) if candidates is not None else all_tools()
    gated = [t for t in pool if _state_ok(t, ctx)]

    if not intent.strip() or not gated:
        return AttentionDecision(expanded=gated[:k], summarised=gated[k:], iso_scores={})

    try:
        intent_vec = embed_one(intent)
    except Exception:  # noqa: BLE001 — embedding model unavailable
        return AttentionDecision(expanded=gated[:k], summarised=gated[k:], iso_scores={})

    scored: list[tuple[float, ToolSpec]] = []
    for t in gated:
        try:
            v = embed_one(t.summary)
        except Exception:  # noqa: BLE001
            v = []
        scored.append((_cos(intent_vec, v), t))

    scored.sort(key=lambda kv: -kv[0])
    expanded = [t for _, t in scored[:k]]
    summarised = [t for _, t in scored[k:]]
    iso = {t.name: round(s, 4) for s, t in scored}
    return AttentionDecision(expanded=expanded, summarised=summarised, iso_scores=iso)
