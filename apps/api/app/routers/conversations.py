"""Conversation import — pour ChatGPT / Claude / Cursor / Telegram exports
into Second Brain so every useful agent turn becomes permanent memory.

The import is intentionally model-agnostic: the request body just carries
``messages: [{role, content, ts?}]``. Each non-trivial turn becomes one
``items`` row with the v1 enrichment pipeline (atomic facts and all),
plus an ``episodes`` row recording the agent (``actor``) and channel
(``conversation_import``).

Why turns and not whole conversations? Mem0 / Letta have shown that
turn-level granularity gives much better recall than dumping the whole
log: the embedding for "We agreed to use SQLite, not Postgres" is
dramatically better than the embedding for a 200-turn rambling thread.
"""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, Field

from .. import db
from ..auth import require_token
from ..ingest.pipeline import create_pending_item, process_item

router = APIRouter(
    prefix="/api/conversations", tags=["conversations"], dependencies=[Depends(require_token)]
)


class Message(BaseModel):
    role: str = Field(..., description="user | assistant | system | tool")
    content: str
    ts: str | None = None


class ConversationImport(BaseModel):
    actor: str = Field(default="agent", description="claude-code | cursor | chatgpt | telegram | …")
    title: str | None = None
    messages: list[Message]


def _is_useful(text: str) -> bool:
    """Skip greetings / confirmations / pure tool-call shells."""
    s = (text or "").strip()
    if len(s) < 40:
        return False
    if s.lower() in {"ok", "okay", "thanks", "thank you", "got it"}:
        return False
    return True


@router.post("/import")
def import_conversation(payload: ConversationImport, background: BackgroundTasks) -> dict:
    title_prefix = payload.title or f"Conversation with {payload.actor}"
    created: list[int] = []

    # We pair each assistant message with the preceding user message so the
    # captured "turn" carries context, not just an answer floating in space.
    last_user: str | None = None
    for msg in payload.messages:
        if msg.role == "user":
            last_user = msg.content
            continue
        if msg.role != "assistant":
            continue
        if not _is_useful(msg.content):
            continue
        text = msg.content
        if last_user:
            text = f"User: {last_user.strip()}\n\nAssistant: {msg.content.strip()}"
            last_user = None

        title = (msg.content.strip().splitlines() or [""])[0][:120] or title_prefix
        item_id = create_pending_item(text=text, url=None, title=f"{title_prefix} — {title}")
        db.execute(
            "INSERT INTO episodes(item_id, actor, channel, note) VALUES(?, ?, 'conversation_import', ?)",
            (item_id, payload.actor, msg.ts),
        )
        background.add_task(process_item, item_id, text=text, url=None, title=f"{title_prefix} — {title}")
        created.append(item_id)

    return {"imported": len(created), "item_ids": created}
