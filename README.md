# Second Brain

An open-source, AI-powered personal knowledge base.

Capture Instagram Reels, YouTube / TikTok / Twitter videos, articles, voice
memos, and plain notes from any device. We transcribe, summarise, extract every
mentioned tool / app / book / person, embed everything for semantic search, and
build a knowledge graph you can browse — all on FOSS components, all
self-hostable.

> Status: v0 — backend + web app working end-to-end with the fallback
> "no-LLM" mode. Drop in an OpenRouter / OpenAI key (or run a local Ollama
> with Gemma 3 or Qwen 2.5) to unlock high-quality summaries and entity
> extraction.

---

## Stack at a glance

| Concern | Choice | Why |
|---|---|---|
| Frontend | **Next.js 16** + Tailwind v4 (Vercel) | App Router, PWA, Web Share Target |
| Backend | **FastAPI** + SSE (Render) | Single small Python service |
| Storage | **SQLite + sqlite-vec + FTS5** | One file. No Postgres / Pinecone. |
| Capture | `yt-dlp`, `trafilatura` | Reels / YT / TikTok / X / articles |
| Transcription | `faster-whisper` (opt-in) | CTranslate2, runs on CPU |
| Embeddings | `fastembed` (`bge-small-en-v1.5`) | ONNX, ~80 MB |
| LLM | OpenAI-compatible — Ollama / OpenRouter / OpenAI | Single code path, graceful fallback |
| Auth | Bearer token (per-device) | Boring & simple |
| Realtime | Server-Sent Events | Cross-device live updates |
| License | **AGPL-3.0** | Open source, copyleft |

---

## How "flawless on every device" works

| Device | Path in |
|---|---|
| Android (Chrome) | Install the PWA → it appears in the system share sheet via Web Share Target. |
| iOS (Safari) | Install the PWA *or* import the supplied iOS Shortcut to share into the API. |
| Desktop browser | Install the PWA from Chrome / Edge / Brave. |
| Anywhere with HTTP | `POST /api/ingest` with a bearer token (curl, Raycast, n8n, Tasker…). |
| Telegram | Optional bot scaffold, off until you supply a token. |

All clients hit one Render-hosted backend with one SQLite file → no sync logic,
no conflicts, instant cross-device updates over SSE.

---

## Repo layout

```
apps/
  api/        FastAPI service (deployed to Render)
  web/        Next.js 16 PWA (deployed to Vercel)
docs/         Architecture notes, screenshots, etc.
render.yaml   Render Blueprint — one-click backend deploy
```

---

## Local development

```bash
# 1. Backend — requires Python 3.11+
cd apps/api
uv sync
uv run python -m app.cli init-db
uv run uvicorn app.main:app --reload --port 8000

# 2. Frontend — requires Node 20+ and pnpm
cd apps/web
pnpm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 pnpm dev
```

Open <http://localhost:3000>. Visit `/settings` to point the UI at any other
backend (e.g. your Render deploy) and to save an API token.

### Running with a local Ollama

```bash
ollama pull gemma3:4b           # or: ollama pull qwen2.5:7b
LLM_PROVIDER=ollama LLM_MODEL=gemma3:4b uv run uvicorn app.main:app --reload
```

### Running with OpenRouter (free tier)

```bash
export OPENROUTER_API_KEY=sk-or-...
export LLM_MODEL='google/gemma-3-12b-it:free'   # or 'qwen/qwen-2.5-7b-instruct:free'
uv run uvicorn app.main:app --reload
```

### Running without any LLM key

The backend boots and works — the fallback provider extracts the first few
sentences as a summary and falls back to regex-driven entity extraction. Quality
is rough but the whole pipeline runs.

---

## Deployment

### Backend → Render

1. Click **New → Blueprint** in Render and pick this repo.
2. Render reads `render.yaml`, builds `apps/api/Dockerfile`, and provisions a
   1 GB persistent disk at `/var/data`.
3. In the service's *Environment* tab, set:
   - `CORS_ORIGINS` — your Vercel URL(s), comma-separated.
   - `API_TOKEN` — keep the one Render auto-generated, or replace it.
   - One of: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or leave both blank to use
     the fallback / a local Ollama.
   - `LLM_MODEL` — e.g. `google/gemma-3-12b-it:free`, `gemma3:4b`, `gpt-4o-mini`.
4. Watch the deploy log; the container runs `python -m app.cli init-db` on
   startup so the schema is always present.

> Free-tier note: Render's free plan has no persistent disk, so your SQLite is
> wiped on every restart. Fine for demos. The default Blueprint provisions the
> $7/month Starter plan + a $1/month 1 GB disk — change `plan` in `render.yaml`
> if you need otherwise.

### Frontend → Vercel

1. Import the repo into Vercel and pick the `apps/web` directory as the root.
2. Set `NEXT_PUBLIC_API_BASE_URL` to your Render URL (e.g.
   `https://second-brain-api.onrender.com`).
3. Deploy. Visit the Vercel URL on phone or desktop, hit "Install app" / "Add to
   Home Screen", and you have a PWA that:
   - Shows up in the Android share sheet (Web Share Target).
   - Receives shares, queues them, and lands you on the item page.
   - Streams live updates over SSE — items added on another device appear in
     real time.

---

## API surface

| Method | Path | Use |
|---|---|---|
| `GET` | `/api/health` | Liveness + which LLM provider is active |
| `POST` | `/api/ingest` | `{ "url": "..." }` or `{ "text": "..." }` |
| `POST` | `/api/share` | Same, but accepts `application/x-www-form-urlencoded` (Web Share Target / iOS Shortcuts) |
| `GET` | `/api/items` | Paginated item list |
| `GET` | `/api/items/{id}` | Full item with summary, entities, tags |
| `DELETE` | `/api/items/{id}` | Remove an item |
| `GET` | `/api/search?q=...&mode=hybrid` | FTS5 + vector hybrid search |
| `GET` | `/api/tools` | "Tool Memory" — every tool / app / website ever mentioned |
| `GET` | `/api/entities?entity_type=book` | Filtered entities |
| `GET` | `/api/graph` | Knowledge graph as `{nodes, edges}` |
| `GET` | `/api/events` | Server-Sent Events stream of changes |
| `GET` | `/api/facts` | Atomic facts (Mem0-style); each carries `confidence`, `recall_count`, `last_seen_at` |
| `GET` | `/api/skills` | Procedural memory (verbatim how-tos the agent quotes back) |
| `POST` | `/api/skills` | Upsert a skill |
| `GET` | `/api/episodes?actor=claude-code&days=7` | Episodic queries by actor/channel/time |
| `GET` | `/api/communities` | GraphRAG-style theme rollups written by the nightly job |
| `GET` | `/api/reflections` | Meta-facts the brain wrote about itself (weekly) |
| `POST` | `/api/conversations/import` | Drop a ChatGPT/Claude/Cursor/Telegram transcript → memory items |
| `POST` | `/api/jobs/run` | Manually trigger memory-upkeep jobs (`?name=consolidate` etc.) |
| `GET` | `/api/jobs` | Recent job runs + their status |
| `POST` | `/mcp/jsonrpc` | Model Context Protocol entry point — agents use this |

All routes accept `Authorization: Bearer <API_TOKEN>` (and `?token=...` query
arg, used by SSE since `EventSource` can't set headers).

## Memory mechanics (v1 + v2)

Second Brain isn't just a notes app — it's an *agent-grade memory store*:

- **MCP server** — Claude Code, Cursor, Cline, ChatGPT-desktop add Second Brain
  as a tool source. `search_memory`, `recall_facts` (multi-hop, HippoRAG-style),
  `recall_skill`, `recall_episodes`, `list_communities`, `list_reflections`,
  `add_note`, `get_item`, `delete_item`, `list_themes`.
- **Tool Attention** ([Sadani & Kumar, 2026](https://arxiv.org/abs/...)) —
  `/mcp/discover` ISO-scores tools against your intent and only expands the
  top-k schemas, keeping per-turn cost <2k tokens.
- **Atomic facts (Mem0-style)** — every item is decomposed into self-contained
  sentences, each with its own embedding, `fact_type`, `confidence`,
  `recall_count`, `last_seen_at`.
- **Memory consolidation** — near-duplicate items (cosine ≥ 0.95) are *merged*
  not warned: tags / facts / episodes are unioned, the older item kept as
  canonical, the duplicate's vec rows cleaned up. Replaces the v1 dedupe-warn.
- **Forgetting curve** — facts decay over time unless recalled. Recalling via
  the MCP `recall_facts` tool bumps `last_seen_at` + `recall_count`, sparing
  the fact from the nightly decay pass.
- **Active distillation** — nightly LLM rewrites stale (>30 day, >12-word)
  TLDRs tighter so token cost stays flat as the corpus grows for years.
- **Reflective memory** — nightly job reads the last 7 days of items + facts
  and writes 1–5 *meta-facts* into `reflections` ("user spent the week on
  FastAPI + agents — likely shipping a Second Brain").
- **GraphRAG community rollups** — items cluster by entity co-occurrence
  (cheap union-find, no graph DB needed), each cluster gets an LLM-written
  paragraph summary stored in `communities`.
- **Multi-hop recall (HippoRAG-style)** — `recall_facts` walks
  *fact → item → entity → linked items* in 2 hops by default, not 1.
- **Episodic provenance** — every memory carries `actor` (which agent),
  `device`, `channel` (mcp / share-target / web / conversation_import). Query
  via `recall_episodes`.
- **Conversation import** — paste a ChatGPT / Claude / Cursor / Telegram
  export and every useful turn becomes a memory item with full provenance.
- **Procedural memory** — `kind=skill` rows are quoted verbatim by agents and
  exempt from distillation.
- **Correction loop (DSPy-style)** — every user edit on title / summary /
  TLDR / tags becomes an exemplar pair; future enrichments pull the K most
  similar in-context.

The nightly upkeep cron is shipped as a Render cron service in `render.yaml`.
Run it manually any time with:

```bash
cd apps/api && uv run python -m app.cli run-jobs            # all jobs
cd apps/api && uv run python -m app.cli run-jobs --name decay  # just one
```

Or via REST: `POST /api/jobs/run` (with bearer auth).

---

## License

AGPL-3.0. See `LICENSE`.
