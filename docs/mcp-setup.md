# Use Second Brain as MCP memory in Claude Code / Cursor / Cline

Second Brain ships an MCP (Model Context Protocol) server so any MCP-aware
agent can natively `search_memory`, `add_note`, `recall_facts`, and
`get_item` against your personal knowledge base — turning every coding
session into one with permanent memory.

The server is built on the **Tool Attention** primitives from Sadani &
Kumar 2026 (Infrrd.ai), so the per-turn schema cost stays under ~1k tokens
even as we add more memory primitives later.

## Endpoints

| Endpoint | What it does |
|---|---|
| `GET /mcp/manifest` | Server capabilities, no auth required. |
| `POST /mcp/jsonrpc` | Standard MCP transport (`initialize`, `tools/list`, `tools/call`). |
| `GET /mcp/tools?intent=...&k=4` | Lazy schema loader — only the top-k tools have full JSON Schema. |
| `POST /mcp/discover` | Same, JSON body `{intent, k}`. |
| `POST /mcp/call` | REST sugar for one-shot tool calls. |
| `GET /mcp/budget?intent=...` | Reports the eager-vs-lazy token delta. |

All endpoints except `/manifest` require the same `Authorization: Bearer <token>`
the rest of the API uses.

## Installing in Claude Code

Add to your Claude Code MCP config (typically `~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "second-brain": {
      "transport": {
        "type": "http",
        "url": "https://<your-render-url>/mcp/jsonrpc",
        "headers": {
          "Authorization": "Bearer <YOUR_API_TOKEN>"
        }
      }
    }
  }
}
```

## Installing in Cursor / Cline

Same JSON shape under their MCP settings. Both clients call `tools/list`
on connect; pass `intent` if you want the lazy variant:

```bash
curl -s -X POST https://<host>/mcp/jsonrpc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"intent":"recall what I know about postgres","k":3}}'
```

## Tools exposed

| Tool | When to use |
|---|---|
| `search_memory` | "What did I save about X?" Returns TLDRs, not bodies. |
| `get_item` | Expand one promising hit's full body. |
| `add_note` | Save a new note / link / snippet. Runs the full enrichment pipeline. |
| `recall_facts` | Atomic Mem0-style facts (preferences, identity, how-tos). |
| `list_themes` | Top tags — orient on what the user has been thinking about. |
| `delete_item` | Destructive; only on explicit user request. |

## Tool Attention in one paragraph

The classic MCP failure mode is the "Tools Tax": every turn dumps the full
schema of every tool into the model's context (10–60k tokens in real
deployments). Past ~70% context utilisation reasoning quality cliffs. We
fix that with three primitives from the paper:

1. **ISO score** — cosine similarity between the agent's embedded *intent*
   and each tool's embedded *summary*.
2. **State-aware gating** — drop tools whose preconditions aren't met
   (`requires_items`, `requires_facts`, …) before scoring.
3. **Two-phase lazy loading** — keep one-line summaries of every tool in
   context; expand to full JSON schema only for the top-k.

The savings are observable via `/mcp/budget`. With our six tools and an
empty corpus we already see ~80% reduction; the curve gets steeper as the
tool count grows.
