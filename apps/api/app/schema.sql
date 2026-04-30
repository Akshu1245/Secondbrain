-- Second Brain SQLite schema
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    kind            TEXT NOT NULL,                -- 'reel' | 'video' | 'article' | 'note' | 'voice'
    source_url      TEXT,
    source_platform TEXT,                         -- 'instagram' | 'youtube' | 'tiktok' | 'twitter' | 'web' | 'manual'
    title           TEXT,
    author          TEXT,
    raw_text        TEXT,                         -- transcript / article body / note body
    summary         TEXT,                         -- LLM-generated 3-bullet summary
    tldr            TEXT,                         -- one-line TL;DR
    media_path      TEXT,                         -- relative path under media_dir
    duration_sec    REAL,
    status          TEXT NOT NULL DEFAULT 'pending', -- pending | processing | ready | failed
    error           TEXT,
    metadata_json   TEXT,                         -- raw yt-dlp / readability metadata
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_items_status   ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_kind     ON items(kind);
CREATE INDEX IF NOT EXISTS idx_items_platform ON items(source_platform);

-- Tags (auto + manual)
CREATE TABLE IF NOT EXISTS tags (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT UNIQUE NOT NULL COLLATE NOCASE
);
CREATE TABLE IF NOT EXISTS item_tags (
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    tag_id  INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    source  TEXT NOT NULL DEFAULT 'auto',  -- 'auto' | 'manual'
    PRIMARY KEY (item_id, tag_id)
);

-- Extracted entities — the "Tool Memory" lives here when entity_type='tool'
CREATE TABLE IF NOT EXISTS entities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL COLLATE NOCASE,
    entity_type TEXT NOT NULL,                    -- tool | app | website | book | person | place | concept
    canonical_url TEXT,
    description TEXT,
    metadata_json TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, entity_type)
);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

CREATE TABLE IF NOT EXISTS item_entities (
    item_id   INTEGER NOT NULL REFERENCES items(id)    ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    confidence REAL NOT NULL DEFAULT 1.0,
    context   TEXT,                               -- short snippet around the mention
    PRIMARY KEY (item_id, entity_id)
);

-- Hybrid search: lexical FTS5 over title + raw_text + summary
CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    title, raw_text, summary,
    content='items', content_rowid='id',
    tokenize='porter unicode61'
);

CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
    INSERT INTO items_fts(rowid, title, raw_text, summary)
    VALUES (new.id, new.title, new.raw_text, new.summary);
END;
CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
    INSERT INTO items_fts(items_fts, rowid, title, raw_text, summary)
    VALUES ('delete', old.id, old.title, old.raw_text, old.summary);
END;
CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
    INSERT INTO items_fts(items_fts, rowid, title, raw_text, summary)
    VALUES ('delete', old.id, old.title, old.raw_text, old.summary);
    INSERT INTO items_fts(rowid, title, raw_text, summary)
    VALUES (new.id, new.title, new.raw_text, new.summary);
END;

-- Vector store (sqlite-vec)
CREATE VIRTUAL TABLE IF NOT EXISTS item_vectors USING vec0(
    item_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);

-- Background job log (visibility into pipeline progress per item)
CREATE TABLE IF NOT EXISTS job_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id    INTEGER REFERENCES items(id) ON DELETE CASCADE,
    stage      TEXT NOT NULL,        -- capture | transcribe | enrich | embed
    status     TEXT NOT NULL,        -- start | ok | error | skip
    detail     TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_job_events_item ON job_events(item_id);

-- ── v1: Agent Memory Edition ──────────────────────────────────────────────

-- Atomic facts (Mem0-style): one item -> N facts. Agents query facts directly,
-- which is far cheaper than re-reading whole items.
CREATE TABLE IF NOT EXISTS facts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id     INTEGER REFERENCES items(id) ON DELETE CASCADE,
    text        TEXT NOT NULL,                  -- one self-contained sentence
    fact_type   TEXT NOT NULL DEFAULT 'general',-- preference | identity | task | general | how_to
    confidence  REAL NOT NULL DEFAULT 1.0,
    last_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_facts_item ON facts(item_id);
CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(fact_type);

CREATE VIRTUAL TABLE IF NOT EXISTS facts_vec USING vec0(
    fact_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);

-- Episodic provenance: which agent / device / source dropped each item.
CREATE TABLE IF NOT EXISTS episodes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id    INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    actor      TEXT,            -- 'user' | 'claude-code' | 'cursor' | 'cline' | ...
    device     TEXT,            -- free-form: 'phone' | 'macbook' | 'render' | ...
    channel    TEXT,            -- 'web' | 'mcp' | 'share-target' | 'telegram'
    note       TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_episodes_item ON episodes(item_id);

-- Correction loop / few-shot exemplars. Every time a user edits a summary,
-- tldr, or tags, we record the (input -> expected output) pair. Future
-- enrichments can pull the K most-similar exemplars in-context.
CREATE TABLE IF NOT EXISTS exemplars (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    field       TEXT NOT NULL,         -- 'summary' | 'tldr' | 'tags' | 'entities'
    input_text  TEXT NOT NULL,         -- the title + body that was being enriched
    expected    TEXT NOT NULL,         -- the user's corrected value
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_exemplars_field ON exemplars(field);

CREATE VIRTUAL TABLE IF NOT EXISTS exemplars_vec USING vec0(
    exemplar_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);

-- MCP tool registry for Tool Attention (ISO scoring + lazy schema loading).
-- Schemas are stored as JSON; agents fetch tiny summaries by default and
-- only pay the schema-token cost for top-k tools matched to their intent.
CREATE TABLE IF NOT EXISTS mcp_tools (
    name        TEXT PRIMARY KEY,
    summary     TEXT NOT NULL,        -- one-line description used for ISO scoring
    schema_json TEXT NOT NULL,        -- full JSON schema (returned only on demand)
    state_predicates TEXT,            -- comma-separated: 'requires_items' etc.
    enabled     INTEGER NOT NULL DEFAULT 1,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS mcp_tools_vec USING vec0(
    rowid INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);
CREATE TABLE IF NOT EXISTS mcp_tool_index (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT UNIQUE NOT NULL REFERENCES mcp_tools(name) ON DELETE CASCADE
);

-- ── v2: Stronger Memory ───────────────────────────────────────────────────

-- Active fact decay / recall counter. ALTER-style additions are wrapped in a
-- conditional so re-running the schema on a v1 db is idempotent.
-- (The columns are NOT NULL with defaults; SQLite handles it on ALTER.)
-- We use a separate "fact_stats" view-style table only when extending; here
-- we just rely on `last_seen_at` (already in v1) plus new columns:
--   recall_count, decayed_at
-- Added directly to facts in v2 via add_column migrations done in cli.py.

-- Skills / procedural memory: short, high-confidence "how I do X" notes.
-- Skills are quoted verbatim by agents; treated separately from items so
-- they don't get distilled away.
CREATE TABLE IF NOT EXISTS skills (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    summary     TEXT NOT NULL,
    body        TEXT NOT NULL,            -- the verbatim "how to" content
    tags_json   TEXT,
    use_count   INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE VIRTUAL TABLE IF NOT EXISTS skills_vec USING vec0(
    skill_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);

-- Multi-hop links between memory primitives. Lets recall walk
-- fact ↔ item ↔ entity ↔ fact in 2 hops (HippoRAG-ish).
CREATE TABLE IF NOT EXISTS memory_links (
    src_kind   TEXT NOT NULL,    -- 'item' | 'fact' | 'entity' | 'skill'
    src_id     INTEGER NOT NULL,
    dst_kind   TEXT NOT NULL,
    dst_id     INTEGER NOT NULL,
    relation   TEXT NOT NULL,    -- 'mentions' | 'derived_from' | 'similar_to' | 'merged_into'
    weight     REAL NOT NULL DEFAULT 1.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (src_kind, src_id, dst_kind, dst_id, relation)
);
CREATE INDEX IF NOT EXISTS idx_links_src ON memory_links(src_kind, src_id);
CREATE INDEX IF NOT EXISTS idx_links_dst ON memory_links(dst_kind, dst_id);

-- GraphRAG-style community summaries written by the nightly rollup job.
CREATE TABLE IF NOT EXISTS communities (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    label        TEXT NOT NULL,
    summary      TEXT NOT NULL,         -- LLM-written paragraph
    member_ids   TEXT NOT NULL,         -- JSON array of item ids
    period_start TIMESTAMP,
    period_end   TIMESTAMP,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Reflections: meta-facts the nightly job writes about itself
-- ("user spent the week on FastAPI + agents → likely shipping a Second Brain").
-- Stored separately so they don't pollute the user's atomic facts.
CREATE TABLE IF NOT EXISTS reflections (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    text         TEXT NOT NULL,
    period_start TIMESTAMP,
    period_end   TIMESTAMP,
    confidence   REAL NOT NULL DEFAULT 0.6,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Job runs: every nightly cron run leaves a row so we can track health.
CREATE TABLE IF NOT EXISTS job_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name    TEXT NOT NULL,           -- 'consolidate' | 'distill' | 'reflect' | 'rollup' | 'decay'
    status      TEXT NOT NULL,           -- 'ok' | 'error'
    detail      TEXT,
    started_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_job_runs_name ON job_runs(job_name);

