"""FastAPI entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import settings
from .db import init_db
from .llm import get_provider
from .routers import entities, graph, ingest, items, search, stream

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    log.info("schema ready at %s", settings.db_path)
    log.info("LLM provider: %s", get_provider().name)
    yield


app = FastAPI(
    title="Second Brain API",
    version=__version__,
    description="AI-powered personal knowledge base — multi-modal capture, hybrid search, knowledge graph.",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def root() -> JSONResponse:
    return JSONResponse(
        {
            "name": "Second Brain API",
            "version": __version__,
            "llm_provider": get_provider().name,
            "endpoints": {
                "health": "/api/health",
                "ingest": "POST /api/ingest",
                "share": "POST /api/share",
                "items": "GET /api/items",
                "search": "GET /api/search?q=...",
                "entities": "GET /api/entities",
                "tools": "GET /api/tools",
                "graph": "GET /api/graph",
                "events": "GET /api/events (SSE)",
                "docs": "/docs",
            },
        }
    )


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "version": __version__, "llm": get_provider().name}


app.include_router(ingest.router)
app.include_router(items.router)
app.include_router(search.router)
app.include_router(entities.router)
app.include_router(graph.router)
app.include_router(stream.router)

if settings.serve_frontend and settings.frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(settings.frontend_dir), html=True), name="frontend")
