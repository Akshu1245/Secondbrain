"""Pydantic models for the API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ItemKind = Literal["reel", "video", "article", "note", "voice"]
ItemStatus = Literal["pending", "processing", "ready", "failed"]
EntityType = Literal["tool", "app", "website", "book", "person", "place", "concept"]


class IngestRequest(BaseModel):
    text: str | None = Field(default=None, description="Free-form note or pasted URL")
    url: str | None = Field(default=None, description="Explicit URL")
    title: str | None = None
    tags: list[str] = []


class TagOut(BaseModel):
    id: int
    name: str


class EntityOut(BaseModel):
    id: int
    name: str
    entity_type: EntityType
    description: str | None = None
    canonical_url: str | None = None
    mention_count: int = 0


class ItemOut(BaseModel):
    id: int
    kind: ItemKind
    source_url: str | None = None
    source_platform: str | None = None
    title: str | None = None
    author: str | None = None
    summary: str | None = None
    tldr: str | None = None
    raw_text: str | None = None
    media_path: str | None = None
    duration_sec: float | None = None
    status: ItemStatus
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut] = []
    entities: list[EntityOut] = []


class ItemListOut(BaseModel):
    items: list[ItemOut]
    total: int


class SearchHit(BaseModel):
    item: ItemOut
    score: float
    snippet: str | None = None


class SearchResponse(BaseModel):
    query: str
    hits: list[SearchHit]


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # 'item' | 'entity' | 'tag'
    meta: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    kind: str  # 'mentions' | 'tagged'


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class JobEvent(BaseModel):
    stage: str
    status: str
    detail: str | None = None
    created_at: datetime
