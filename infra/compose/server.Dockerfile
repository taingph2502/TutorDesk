FROM ghcr.io/astral-sh/uv:0.11.21 AS uv

FROM python:3.12.13-slim-bookworm

COPY --from=uv /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY apps/server ./apps/server

RUN uv sync --frozen --no-dev --package tutordesk \
    && useradd --create-home --uid 10001 tutordesk

USER tutordesk

CMD ["tutordesk-api"]
