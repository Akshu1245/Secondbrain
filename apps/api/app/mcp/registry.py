"""MCP tool registry — single source of truth for tools we expose.

Each tool ships with:
  - a tiny `summary` (used for Intent–Schema Overlap scoring; *the* core
    primitive in the Tool Attention paper [Sadani & Kumar, 2026])
  - a full JSON Schema (only emitted in MCP responses when an agent's intent
    actually scores into the top-k or the agent explicitly asks for it)
  - state predicates so we can gate tools whose preconditions aren't met
    (e.g. `delete_item` is hidden when the corpus is empty).

Adding a tool is one entry here + one handler in `tools.py`. The router
wires both at startup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolSpec:
    name: str
    summary: str  # 1-line description, the *only* thing in context by default
    description: str  # longer text, only in full schema
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    state_predicates: tuple[str, ...] = ()  # e.g. ('requires_items',)


# Filled in lazily so we don't import handlers at module load.
_REGISTRY: dict[str, ToolSpec] = {}


def register(tool: ToolSpec) -> None:
    _REGISTRY[tool.name] = tool


def all_tools() -> list[ToolSpec]:
    return list(_REGISTRY.values())


def get(name: str) -> ToolSpec | None:
    return _REGISTRY.get(name)


def schema_for(spec: ToolSpec) -> dict[str, Any]:
    """Full MCP-compatible tool schema — only emitted when actually needed."""
    return {
        "name": spec.name,
        "description": spec.description,
        "inputSchema": spec.input_schema,
    }


def summary_for(spec: ToolSpec) -> dict[str, Any]:
    """Tiny tool descriptor used in the lazy-schema phase."""
    return {"name": spec.name, "summary": spec.summary}
