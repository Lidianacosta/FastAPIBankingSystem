FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN useradd -m -u 1000 appuser && \
    chown appuser:appuser /app

COPY --from=builder --chown=appuser:appuser --chmod=555 /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appuser --chmod=555 src/ ./src/
COPY --chown=appuser:appuser --chmod=555 migrations/ ./migrations/
COPY --chown=appuser:appuser --chmod=555 alembic.ini pyproject.toml uv.lock ./
COPY --chown=appuser:appuser --chmod=555 scripts/ ./scripts/

USER appuser

EXPOSE 8000

ENTRYPOINT ["./scripts/entrypoint.sh"]
