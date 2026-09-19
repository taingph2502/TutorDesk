# Docker Compose substrate

The Compose substrate starts the Next.js presentation adapter, FastAPI, and PostgreSQL with pgvector.
Only Next.js is published to the host, at `http://127.0.0.1:3000`; FastAPI and PostgreSQL remain on
private container networks. The public `/api/v1/health` route checks both the API and PostgreSQL.

## Start

From the repository root:

```powershell
Copy-Item infra/compose/.env.example infra/compose/.env
# Replace the placeholder in infra/compose/.env with a long random local password.
pnpm compose:up
```

`compose:up` builds the application images and waits for the integrated health check. Open
`http://127.0.0.1:3000` after it succeeds. The database password is supplied as a Docker secret and
is not stored in a container environment variable.

Stop the application without deleting its database:

```powershell
pnpm compose:down
```

Compose applies bounded local log rotation, restart-on-process-exit recovery, deterministic health
checks, a read-only web filesystem, non-root application processes, and graceful shutdown windows.
Raw Compose remains an advanced recovery path behind the future Windows launcher rather than
becoming a second application interface.

## Recovery

An exited process restarts automatically unless the learner explicitly stopped it. Docker Compose
does not automatically restart a process that is still running but unhealthy. If a health check
remains unhealthy, restart the affected service and wait for the integrated health surface:

```powershell
docker compose -f infra/compose/compose.yaml restart api web
docker compose -f infra/compose/compose.yaml up --wait
```

Database interruption is reported as a sanitized `503`; after PostgreSQL recovers, the API and web
health checks recover without replacing the database volume. Cancellation uses the configured
graceful shutdown windows. Repeating `compose:up` is safe and waits for the existing services.

## Verify

With the stack running, exercise the public deployment contract:

```powershell
$env:TUTORDESK_COMPOSE_SMOKE = "1"
uv run pytest tests/integration/test_compose_substrate.py -q
```

The test verifies the normalized Compose model and calls both the Workspace and integrated health
surface through the single loopback origin. Health failures return only component availability; raw
database errors and connection material are never included in the response.
