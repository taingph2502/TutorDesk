FROM node:24.18.0-bookworm-slim AS base

ENV NEXT_TELEMETRY_DISABLED=1 \
    PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@12.4.1 --activate

FROM base AS builder

WORKDIR /workspace

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/generated-client/package.json ./packages/generated-client/package.json

RUN pnpm install --frozen-lockfile --filter @tutordesk/web...

COPY apps/web ./apps/web
COPY packages/generated-client ./packages/generated-client

ARG TUTORDESK_API_ORIGIN=http://api:8000
ENV TUTORDESK_API_ORIGIN=$TUTORDESK_API_ORIGIN

RUN pnpm --filter @tutordesk/web build

FROM node:24.18.0-bookworm-slim AS runner

ENV HOSTNAME="0.0.0.0" \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV="production" \
    PORT=3000

WORKDIR /app

COPY --from=builder --chown=node:node /workspace/apps/web/.next/standalone ./
COPY --from=builder --chown=node:node /workspace/apps/web/.next/static ./apps/web/.next/static

USER node
WORKDIR /app/apps/web

CMD ["node", "server.js"]
