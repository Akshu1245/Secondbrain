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
