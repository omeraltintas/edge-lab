# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Bagimliliklar once: kod degisince bu katman cache'te kalir
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Uygulama + migration dosyalari
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./
RUN uv sync --frozen --no-dev


FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --uid 10001 edge

WORKDIR /app
COPY --from=builder --chown=edge:edge /app /app

USER edge

EXPOSE 8000

# exec form: uvicorn PID 1 olur, SIGTERM'i dogrudan alir
CMD ["uvicorn", "edge_lab.main:app", "--host", "0.0.0.0", "--port", "8000"]
