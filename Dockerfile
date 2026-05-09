FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN useradd -m -u 1000 appuser && \
    chown appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser migrations/ ./migrations/
COPY --chown=appuser:appuser alembic.ini pyproject.toml uv.lock ./
COPY --chown=appuser:appuser scripts/ ./scripts/

USER appuser

EXPOSE 8000

ENTRYPOINT ["./scripts/entrypoint.sh"]
