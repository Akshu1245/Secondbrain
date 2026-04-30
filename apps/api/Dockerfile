# Second Brain API — Render-ready container
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential ca-certificates curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# uv for fast, deterministic installs
COPY --from=ghcr.io/astral-sh/uv:0.5.9 /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --no-install-project || uv sync --no-dev --no-install-project

COPY app ./app
RUN uv sync --frozen --no-dev || uv sync --no-dev


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DATA_DIR=/var/data

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -ms /bin/bash app

COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY --from=builder /app/app /app/app
COPY pyproject.toml /app/

RUN mkdir -p /var/data && chown -R app:app /var/data /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=3); sys.exit(0)" || exit 1

CMD ["sh", "-c", "python -m app.cli init-db && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
