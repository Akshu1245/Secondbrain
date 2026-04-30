"""MCP server — Claude Code, Cursor, Cline, ChatGPT-desktop and any other MCP
client get Second Brain as a first-class memory backend.

Two transports:

  * `POST /mcp/jsonrpc` — JSON-RPC 2.0 (Streamable HTTP-style transport).
    Implements the standard `initialize`, `tools/list`, and `tools/call`
    methods so off-the-shelf MCP clients work without modification.

  * REST sugar (`/mcp/tools`, `/mcp/discover`, `/mcp/budget`, `/mcp/call`)
    so humans (and curl) can poke at the same surface, and so the Tool
    Attention extras have a discoverable surface for non-MCP callers.

Tool Attention (Sadani & Kumar, 2026): `tools/list` honours an optional
`intent` argument. When provided we run ISO scoring + state-aware gating
and only emit full JSON schemas for the top-k tools — the rest stay as
one-line summaries. This keeps the per-turn token budget tiny even if we
later grow to dozens of memory primitives.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, Query, Request

from .. import db
from ..auth import require_token
from ..mcp.attention import GateContext, attend
from ..mcp.registry import all_tools, get, schema_for, summary_for
from ..mcp.tools import register_all, serialise_result

log = logging.getLogger(__name__)

# Build the registry exactly once at import time.
register_all()


router = APIRouter(prefix="/mcp", tags=["mcp"])


def _gate_context() -> GateContext:
    item_row = db.query_one("SELECT COUNT(*) c FROM items")
    fact_row = db.query_one("SELECT COUNT(*) c FROM facts")
    return GateContext(
        item_count=int(item_row["c"]) if item_row else 0,
        fact_count=int(fact_row["c"]) if fact_row else 0,
    )


# ── REST sugar ────────────────────────────────────────────────────────────

@router.get("/manifest")
def mcp_manifest() -> dict[str, Any]:
    """Static manifest so MCP clients can install Second Brain in two clicks."""
    return {
        "schema_version": "v1",
        "name": "second-brain",
        "version": "0.2.0",
        "description": "Personal AI memory: hybrid search, atomic facts, multi-modal capture.",
        "tools_endpoint": "/mcp/tools",
        "discover_endpoint": "/mcp/discover",
        "call_endpoint": "/mcp/call",
        "jsonrpc_endpoint": "/mcp/jsonrpc",
        "auth": "bearer",
        "tool_attention": {
            "iso_scoring": True,
            "state_gating": True,
            "lazy_schema_loading": True,
            "reference": "Sadani & Kumar 2026 — Tool Attention Is All You Need",
        },
    }


@router.get("/tools", dependencies=[Depends(require_token)])
def list_tools_rest(
    intent: str | None = Query(default=None,
        description="Agent intent. Triggers Tool Attention: only top-k schemas expand."),
    k: int = Query(default=4, ge=1, le=50),
) -> dict[str, Any]:
    ctx = _gate_context()
    if not intent:
        return {
            "tools": [schema_for(t) for t in all_tools()],
            "lazy": False,
            "context_size": {"item_count": ctx.item_count, "fact_count": ctx.fact_count},
        }
    decision = attend(intent, k=k, ctx=ctx)
    return {
        "tools": [schema_for(t) for t in decision.expanded],
        "summaries": [summary_for(t) for t in decision.summarised],
        "iso_scores": decision.iso_scores,
        "lazy": True,
        "k": k,
    }


@router.post("/discover", dependencies=[Depends(require_token)])
def discover(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Cheap pre-flight: agent posts {intent, k}, gets top-k tool names + schemas.

    The whole point of Tool Attention — agents call this *before* they decide
    which schemas to commit to context.
    """
    intent = payload.get("intent") or ""
    k = int(payload.get("k") or 4)
    ctx = _gate_context()
    decision = attend(intent, k=k, ctx=ctx)
    return {
        "expanded": [schema_for(t) for t in decision.expanded],
        "summarised": [summary_for(t) for t in decision.summarised],
        "iso_scores": decision.iso_scores,
    }


@router.post("/call", dependencies=[Depends(require_token)])
def call_tool(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    name = payload.get("name") or ""
    args = payload.get("arguments") or {}
    spec = get(name)
    if spec is None:
        return {"error": f"no such tool: {name}"}
    try:
        result = spec.handler(args)
    except Exception as e:  # noqa: BLE001
        log.exception("mcp tool %s failed", name)
        return {"error": str(e)}
    return {"result": result}


@router.get("/budget", dependencies=[Depends(require_token)])
def budget(intent: str = Query(default=""), k: int = Query(default=4, ge=1, le=50)) -> dict[str, Any]:
    """Estimate token cost for an MCP turn under different attention strategies.

    Lets you confirm we're under the 70% context-utilisation fracture point
    described in the Tool Attention paper.
    """
    ctx = _gate_context()
    full_schemas = [schema_for(t) for t in all_tools()]
    full_chars = sum(len(serialise_result(s)) for s in full_schemas)

    if intent:
        decision = attend(intent, k=k, ctx=ctx)
        lazy_chars = (
            sum(len(serialise_result(schema_for(t))) for t in decision.expanded)
            + sum(len(serialise_result(summary_for(t))) for t in decision.summarised)
        )
    else:
        decision = None
        lazy_chars = sum(len(serialise_result(summary_for(t))) for t in all_tools())

    # ~4 chars per token rule of thumb for English JSON
    return {
        "total_tools": len(full_schemas),
        "approx_tokens_eager": full_chars // 4,
        "approx_tokens_lazy": lazy_chars // 4,
        "savings_pct": round(100 * (full_chars - lazy_chars) / max(full_chars, 1), 1),
        "expanded": [t.name for t in (decision.expanded if decision else [])],
    }


# ── JSON-RPC 2.0 transport ────────────────────────────────────────────────

def _rpc_response(req_id: Any, result: Any | None = None, error: dict | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return payload


@router.post("/jsonrpc", dependencies=[Depends(require_token)])
async def jsonrpc(request: Request) -> dict[str, Any]:
    """JSON-RPC entrypoint compatible with the MCP Streamable HTTP transport."""
    payload = await request.json()
    method = payload.get("method")
    params = payload.get("params") or {}
    req_id = payload.get("id")

    if method == "initialize":
        return _rpc_response(req_id, {
            "protocolVersion": "2025-03-26",
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "second-brain", "version": "0.2.0"},
        })

    if method == "tools/list":
        intent = params.get("intent") or ""
        k = int(params.get("k") or 4)
        ctx = _gate_context()
        if intent:
            decision = attend(intent, k=k, ctx=ctx)
            return _rpc_response(req_id, {
                "tools": [schema_for(t) for t in decision.expanded],
                "_summarised": [summary_for(t) for t in decision.summarised],
                "_iso_scores": decision.iso_scores,
            })
        return _rpc_response(req_id, {"tools": [schema_for(t) for t in all_tools()]})

    if method == "tools/call":
        name = params.get("name") or ""
        args = params.get("arguments") or {}
        spec = get(name)
        if spec is None:
            return _rpc_response(req_id, error={"code": -32602, "message": f"unknown tool {name}"})
        try:
            result = spec.handler(args)
        except Exception as e:  # noqa: BLE001
            log.exception("mcp tool %s failed", name)
            return _rpc_response(req_id, error={"code": -32000, "message": str(e)})
        return _rpc_response(req_id, {
            "content": [{"type": "text", "text": serialise_result(result)}],
            "isError": False,
        })

    return _rpc_response(req_id, error={"code": -32601, "message": f"method not found: {method}"})
