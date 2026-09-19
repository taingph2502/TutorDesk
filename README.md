# TutorDesk

TutorDesk is a local-first learning workspace that turns learner-approved evidence into
citation-grounded study experiences and an inspectable learner model.

## Prerequisites

- Node.js 24.18 and pnpm 12
- Python 3.12 and uv 0.11
- Chromium installed for Playwright (`pnpm --filter @tutordesk/web exec playwright install chromium`)

## Setup

```sh
pnpm install --frozen-lockfile
uv sync --all-packages --frozen
```

Run the complete quality gate with `pnpm check`. Focused entrypoints are `pnpm lint`,
`pnpm typecheck`, `pnpm test:unit`, `pnpm test:integration`, `pnpm eval`, and `pnpm inventory`.

Start the web adapter with `pnpm dev`. Start the FastAPI adapter with `uv run tutordesk-api`.

See [the repository layout](docs/architecture/repository-layout.md) for ownership boundaries and
where new work belongs.

## License

TutorDesk is licensed under the Apache License 2.0.
