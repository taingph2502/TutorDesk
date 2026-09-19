# Repository layout

TutorDesk is a polyglot modular monolith. Deployment entrypoints are separated for least privilege,
but authoritative behavior stays behind typed module interfaces in one Python distribution.

| Path | Responsibility |
| --- | --- |
| `apps/web` | Next.js presentation adapter; owns no domain behavior or durable state |
| `apps/server` | Python distribution containing domain modules, FastAPI, and process entrypoints |
| `workers/source-processing` | Source-worker image and deployment boundary, not a separate service |
| `packages/generated-client` | Generated TypeScript client output owned by the OpenAPI toolchain |
| `infra/compose` | Local loopback deployment substrate |
| `evals` | Versioned, learner-data-free evaluation fixtures and harness |
| `tests` | Tests that cross package boundaries through public interfaces |

## Workspace rules

- pnpm owns TypeScript dependency resolution through `pnpm-lock.yaml`.
- uv owns Python dependency resolution through `uv.lock`.
- A caller uses another module's public interface and never reads its tables or storage paths.
- Unit tests stay with their owning package. Cross-package integration tests live under `tests`.
- Generated source is regenerated from its contract and is never hand-edited.

## Shared quality entrypoints

| Command | Contract |
| --- | --- |
| `pnpm lint` | ESLint and Ruff |
| `pnpm typecheck` | TypeScript and Pyright strict checks |
| `pnpm test:unit` | Vitest and pytest unit suites |
| `pnpm test:integration` | FastAPI boundary tests and Playwright learner workflows |
| `pnpm eval` | English/Vietnamese evaluation-catalog validation |
| `pnpm inventory` | JavaScript/Python dependency and declared-license inventory |
| `pnpm check` | Full local and CI quality gate, including production builds |
