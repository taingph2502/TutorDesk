# Local persistence and vector-index foundations for TutorDesk

**Date:** 2026-09-18
**Decision scope:** local-first persistence, L1/L2/L3 provenance, Memory Graph traversal, hybrid retrieval, migrations, backup/restore, and Windows-first Docker Compose operation.

## Decision

Use **PostgreSQL as TutorDesk's only authoritative database** and install **pgvector in that same database**. Store source versions, content segments, embeddings, L1 events, L2 facts, L3 conclusions, evidence edges, approvals, quiz attempts, and indexing jobs in PostgreSQL.

Implement hybrid retrieval with:

1. PostgreSQL full-text search for lexical candidates;
2. pgvector exact or HNSW search for semantic candidates; and
3. reciprocal-rank fusion (RRF) in SQL or the application query layer, followed by an optional reranker.

Do **not** use embedded Qdrant, Chroma, or a separate vector server as the system of record. If retrieval scale or quality later justifies Qdrant, add it behind a retrieval-port interface as a **rebuildable projection** fed by a transactional outbox. PostgreSQL remains the source of truth.

For the first complete release, run a pinned PostgreSQL + pgvector image in Docker Compose with a Docker named volume. This satisfies the accepted Windows-first Docker Compose boundary while keeping all user data local to the machine.

## Why this is the right default

TutorDesk's hardest invariant is not nearest-neighbor speed. It is exact, durable traceability:

```text
L3 conclusion -> exact L2 facts -> exact L1 events
answer claim  -> exact source version and segment
approval      -> exact proposal version and evidence packet
```

PostgreSQL can commit a domain object and every provenance edge atomically. A transaction hides intermediate states from other sessions, and PostgreSQL's MVCC provides consistent snapshots for concurrent readers ([PostgreSQL transaction blocks](https://www.postgresql.org/docs/current/sql-begin.html), [MVCC](https://www.postgresql.org/docs/current/mvcc-intro.html)). Foreign keys can enforce that every evidence edge names an existing immutable record ([PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)). Recursive common-table expressions are sufficient for the bounded ancestry and descendant queries needed by the Memory Graph ([recursive queries](https://www.postgresql.org/docs/current/queries-with.html)).

pgvector keeps embeddings beside the rows they describe and supports exact search plus HNSW and IVFFlat approximate indexes. Its primary documentation explicitly includes ACID semantics, joins, point-in-time recovery, filtered nearest-neighbor queries, and hybrid use with PostgreSQL full-text search ([pgvector](https://github.com/pgvector/pgvector)). PostgreSQL full-text search supplies normalized `tsvector` documents, query parsing, ranking, and index support; its ranking functions account for lexical frequency, proximity, and structure ([text-search controls](https://www.postgresql.org/docs/current/textsearch-controls.html)).

The consequence is an intentionally boring failure model: one transaction, one migration history, one backup boundary, and no distributed commit between learner memory and its vector index.

## Recommended storage model

The names below are illustrative, but the boundaries are architectural requirements.

| Area | Core records | Required invariant |
|---|---|---|
| Source vault | `source`, `source_version`, `content_segment`, `segment_asset` | A citation points to an immutable source version and stable location anchor. Re-ingestion creates a version; it does not rewrite cited content. |
| Retrieval | `segment_embedding`, lexical `tsvector`, embedding-model registry | Every embedding records model, dimensions, normalization policy, content hash, and source segment. It is reproducible and safe to delete/rebuild. |
| L1 | `memory_event`, optional separately encrypted/redactable payload | Event headers and order are append-only. Corrections and deletion requests append new events; an authorized erasure may destroy a selected sensitive payload while retaining a non-sensitive tombstone. |
| L2 | `l2_fact_version`, `l2_fact_l1_evidence` | Each fact version has one or more exact L1 references, extraction method, confidence, status, and review decision. Inferred facts remain non-influential until approved. |
| L3 | `l3_conclusion_version`, `l3_conclusion_l2_basis` | Each conclusion version references exact L2 fact versions. Approved projections only are exposed to personalization. |
| Practice | `quiz`, `quiz_item_version`, `attempt`, `attempt_response`, deterministic schedule projection | Attempts are objective evidence. Content, scoring rubric, response, and score versions remain reproducible. |
| Boardroom | `evidence_packet`, `agent_turn`, `recommendation_report`, `recommendation_item`, `approval_decision` | The packet is immutable; discussion is visible; recommendations affect memory only through an explicit approval transaction. |
| Async work | `outbox_job`, `embedding_job`, `ingestion_job` | The row needing derived work and its outbox record commit together. Jobs are idempotent and can be replayed. |

Model provenance as ordinary adjacency tables with indexed `from_id` and `to_id` columns. The first release does not need a graph database: Memory Graph traversals are shallow, typed, and bounded, which relational recursive queries handle directly. Keep graph queries behind a domain repository so a specialized graph read model can be added later without changing the authoritative schema.

### Append-only does not mean update-free tables

Use immutable version rows plus explicit lifecycle events. A correction inserts a new version that supersedes the old one. Approval inserts an approval decision and advances a small current-state projection in the same transaction. Never overwrite the text, evidence set, or confidence of a historical L2/L3 version.

For user-requested sensitive-data erasure, separate the immutable event envelope from its payload. Erase or crypto-shred the selected payload, insert a tombstone event, and retain only the minimum non-sensitive identifiers required to explain the missing edge. This preserves audit shape without pretending deleted content still exists.

## Retrieval design

### Initial implementation

- Store one or more embeddings per immutable `content_segment`, not per mutable document row.
- Start with exact pgvector search for correctness baselines. Add HNSW only after corpus benchmarks show it is needed; approximate indexes trade recall for speed ([pgvector index guidance](https://github.com/pgvector/pgvector#hnsw)).
- Filter every candidate by workspace, source-version status, language, modality, and access state before it can reach generation. pgvector supports ordinary SQL filters and documents the recall implications of filtering approximate indexes ([pgvector filtering](https://github.com/pgvector/pgvector#filtering)).
- Maintain lexical vectors separately for English and Vietnamese. PostgreSQL's `english` configuration can stem English; use `simple` tokenization for Vietnamese initially, plus accent-insensitive normalized text only as a secondary recall field. Evaluate Vietnamese tokenization on a fixed bilingual retrieval set before adopting an external tokenizer.
- Retrieve lexical and dense candidate pools independently, fuse them with RRF, and retain component ranks/scores. A citation is valid only when the final answer claim refers to a retrieved `content_segment` and its immutable source anchor; vector similarity alone is not citation evidence.
- Version embedding models. A model change creates new embedding rows or a new physical column/table generation. Backfill asynchronously, compare old/new retrieval offline, then switch an active-model pointer. Do not update embeddings in place without a generation marker.

### When to add Qdrant server

Add a separate Qdrant service only after measured evidence shows that PostgreSQL cannot meet a documented retrieval service-level objective, or when native dense+sparse multi-stage queries materially improve quality. Qdrant's Query API supports hybrid and multi-stage prefetch/fusion ([Qdrant hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/)). If introduced:

1. publish committed segment generations through the PostgreSQL outbox;
2. use stable PostgreSQL IDs as Qdrant point IDs;
3. make indexing idempotent and record the indexed generation;
4. tolerate stale or missing Qdrant data by falling back to PostgreSQL; and
5. rebuild Qdrant entirely from PostgreSQL rather than treating a Qdrant snapshot as the only copy.

This avoids distributed transactions. Search may be briefly stale, but learner-memory provenance cannot become partially committed.

## Option comparison

| Foundation | Local operation | Transactional provenance and graph | Hybrid/vector retrieval | Migrations and backup | Decision |
|---|---|---|---|---|---|
| **PostgreSQL + pgvector** | One local Compose service and named volume; more RAM/ops than SQLite | Strongest fit: one ACID boundary, foreign keys, constraints, recursive CTEs, MVCC | Exact + HNSW/IVFFlat; PostgreSQL FTS + vector fusion; rich filters and joins | Mature SQL migrations; `pg_dump`/`pg_restore`; optional WAL/PITR | **Adopt** |
| **SQLite + sqlite-vec** | Excellent embedded, single-file deployment; WAL permits concurrent readers but only one writer | ACID and recursive graph queries are adequate for a single process | FTS5 + application fusion is viable; sqlite-vec is compact but still pre-v1 and its advanced index work is evolving | Easiest file lifecycle and online backup, but extension/version compatibility becomes app responsibility | Keep as a future no-Docker edition or test adapter, not release foundation |
| **Chroma single-node** | Easy Python `PersistentClient`; JS/TS and Rust use a local server | Retrieval-oriented API does not expose TutorDesk's relational constraints or an app-controlled transaction spanning memory and evidence | Dense queries and metadata/document filtering are easy; newer schema supports sparse/hybrid capabilities | Internal migrations exist, but the persistent layout spans SQLite and per-collection HNSW files; a safe filesystem backup requires stopping the service | Reject as authoritative store; no benefit over pgvector large enough to justify a second state system |
| **Embedded Qdrant (`QdrantLocal`)** | No server, but Python-specific and intended for small-scale data, demos, and tests | Separate from the domain database; persistent local mode uses an exclusive folder lock, so concurrent process access is unsupported | Useful API parity and brute-force local search, but not the server's production index path | Local mode cannot create Qdrant snapshots | Reject for production; acceptable for isolated retrieval tests only |
| **Qdrant server** | Good self-hosted Docker option, but adds another service and backup boundary | Excellent payload filtering, not a replacement for relational provenance; cross-store atomicity requires an outbox | Strongest native dense+sparse hybrid and multi-stage search among evaluated dedicated stores | Collection/full snapshots exist but have version restore constraints; Windows bind mounts need care | Defer as a rebuildable search projection behind a measured scale/quality trigger |

## Evidence behind the rejected defaults

### SQLite and sqlite-vec

SQLite provides serializable ACID transactions even across crashes and power loss ([SQLite transactional guarantees](https://www.sqlite.org/transactional.html)). WAL mode lets readers and a writer proceed concurrently, but all processes must be on the same host and there is still only one writer at a time ([SQLite WAL](https://www.sqlite.org/wal.html)). Its recursive CTE implementation explicitly supports tree and graph walks ([SQLite `WITH`](https://www.sqlite.org/lang_with.html#recursivecte)). The online backup API produces a consistent snapshot without holding the source lock for the entire copy ([SQLite backup API](https://www.sqlite.org/backup.html)). Those properties make SQLite a strong future portable edition.

The blocker is the vector layer's maturity, not SQLite's durability. sqlite-vec describes itself as pre-v1 with expected breaking changes, although it runs on Windows and supports metadata, auxiliary, and partition columns ([sqlite-vec repository](https://github.com/asg017/sqlite-vec), [API warning](https://github.com/asg017/sqlite-vec/blob/main/site/api-reference.md)). Its maintainer also documents limitations around arbitrary joined pre-filtering of `vec0` virtual tables and recommends manual exact distance calculation for some schemas ([sqlite-vec filtering discussion](https://github.com/asg017/sqlite-vec/issues/196)). TutorDesk should not make its most important provenance subsystem depend on an unstable native extension in the first complete release.

If a later no-Docker edition uses SQLite WAL, pin a version containing the 2026 WAL-reset fix; SQLite documents the bug as fixed in 3.51.3 and selected backports ([SQLite WAL-reset notice](https://www.sqlite.org/wal.html#walreset)).

### Chroma

Chroma persists automatically through Python's `PersistentClient`; TypeScript and Rust connect to a local Chroma server ([Chroma clients](https://docs.trychroma.com/docs/run-chroma/clients)). Its standard query API combines dense nearest-neighbor search with metadata and document-content filters ([Chroma query API](https://docs.trychroma.com/docs/querying-collections/query-and-get)), and current product documentation advertises dense, sparse, hybrid, full-text, and multimodal retrieval ([Chroma overview](https://docs.trychroma.com/docs/overview/introduction)).

Those are convenient retrieval features, but they do not establish the referential and transactional invariants TutorDesk requires. This is an architectural inference from the public API: collections expose record operations and filters, not application-defined foreign keys or one transaction that atomically commits an L2 fact and its L1 evidence edges.

Operationally, Chroma single-node persistence contains a SQLite database plus separate per-collection HNSW files ([Chroma storage layout](https://cookbook.chromadb.dev/core/storage-layout/)). Its backup guide says API export may miss concurrent updates and filesystem backup requires stopping the container to avoid corruption ([Chroma backups](https://cookbook.chromadb.dev/strategies/backup/)). Chroma does track and apply internal schema migrations ([Chroma configuration](https://cookbook.chromadb.dev/core/configuration/)), but that migration system does not replace TutorDesk's domain-schema migrations.

### Embedded and server Qdrant

The Qdrant Python client's own `QdrantLocal` class says local mode is for small-scale data, demos, and tests; it warns above 20,000 points and uses an exclusive filesystem lock that directs concurrent users to the server ([QdrantLocal source](https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/local/qdrant_local.py)). Qdrant's snapshot tutorial states that snapshots cannot be created in Python SDK local mode ([Qdrant snapshots tutorial](https://qdrant.tech/documentation/database-tutorials/create-snapshot/)). This makes embedded Qdrant a poor durability boundary for a complete application.

Qdrant server is substantially stronger. It supports local Docker persistence, hybrid query fusion, and collection/full-storage snapshots ([local quickstart](https://qdrant.tech/documentation/quick-start/), [hybrid queries](https://qdrant.tech/documentation/search/hybrid-queries/), [snapshots](https://qdrant.tech/documentation/snapshots/)). But restoring a snapshot is constrained to the same minor version or the next minor version, and Qdrant warns that Docker/WSL mounts on Windows are known to have filesystem problems that can cause data loss ([installation guidance](https://qdrant.tech/documentation/installation/)). It is therefore a defensible later search service, not the initial system of record.

## Migrations and deployment contract

1. **Pin versions.** Pin PostgreSQL major/minor-compatible image and pgvector version (or, preferably, an image digest) rather than `latest`. The pgvector project publishes Docker images and documents extension installation ([pgvector installation](https://github.com/pgvector/pgvector#installation)).
2. **One forward migration history.** Keep numbered SQL migrations in the repository. The deploy flow takes a backup, checks the running schema version, applies migrations once, then starts application services. Destructive changes use expand/backfill/verify/contract across releases.
3. **Migration safety.** Migrations must preserve immutable IDs and evidence edges. Any source/chunk reprocessing writes a new generation. A migration that cannot be safely rolled back must declare its restore procedure and required free disk space.
4. **Compose readiness.** Give PostgreSQL a `pg_isready` healthcheck and gate migration/app services on `condition: service_healthy`; Docker documents that ordinary startup order only means “running,” not “ready” ([Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)).
5. **Windows storage.** Use a Docker named volume for PostgreSQL data, not a bind mount into `C:\` or another Windows filesystem path. Docker documents materially better Linux-container filesystem performance when data is in the WSL/Linux filesystem ([Docker Desktop WSL guidance](https://docs.docker.com/desktop/features/wsl/best-practices/)). Export backups to a user-selected host directory as files rather than exposing the live database directory.
6. **Separate large immutable binaries.** Store uploaded audio/video/original files in a versioned local object directory or S3-compatible local service; PostgreSQL stores hashes, media metadata, extraction status, and stable locations. Include that object directory in the backup manifest. Database and objects share content hashes, not a distributed write transaction; an ingestion state machine prevents incomplete objects from becoming queryable.

## Backup, restore, and disaster recovery

The minimum supported backup artifact is:

```text
tutordesk-backup-<timestamp>/
  manifest.json              # app/schema/model versions, checksums, object inventory
  database.dump              # pg_dump custom-format archive
  objects/                   # immutable uploaded originals and derived assets, or their archive
```

- Run scheduled `pg_dump --format=custom` against the live database. PostgreSQL documents that dump archives can be selectively restored and are portable across architectures; logical dumps can generally be loaded into newer PostgreSQL versions ([SQL dump](https://www.postgresql.org/docs/current/backup-dump.html), [`pg_restore`](https://www.postgresql.org/docs/current/app-pgrestore.html)).
- Encrypt backup archives when they leave the application data directory. Never put provider keys in the dump or manifest.
- Restore into an empty, pinned-version stack; run `pg_restore`; restore objects; verify checksums; run schema and provenance-integrity checks; then rebuild full-text/vector indexes if necessary.
- Treat successful backup creation as incomplete until an automated restore drill passes. Ship a documented one-command backup and one-command restore, and test restore in CI against representative bilingual/multimodal fixtures.
- Daily logical backup with rotation is sufficient for the first single-user release. Add base backups plus WAL archiving only if recovery-point objectives demand it; PostgreSQL supports point-in-time recovery by combining a base backup with archived WAL ([continuous archiving/PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)).

Because embeddings are stored in the authoritative dump, a basic restore is immediately usable. They are nevertheless treated as derived: the integrity checker can delete and regenerate an embedding generation from immutable segments when the model or index changes.

## Acceptance checks for implementation tickets

Before calling the persistence foundation complete, automate these checks:

1. A committed L2 fact cannot reference a missing L1 event; a committed L3 conclusion cannot reference a missing L2 fact version.
2. Inferred L2 and all L3 records in `pending` state are absent from the personalization projection.
3. A Boardroom recommendation cannot become active without a recorded user approval tied to the exact report version.
4. A claim citation resolves to the exact source version, segment, and location anchor used during generation.
5. A failed transaction leaves neither an orphan memory record nor a provenance edge.
6. Replaying an outbox or embedding job is idempotent.
7. Exact and approximate vector modes are compared on a fixed English/Vietnamese retrieval fixture; HNSW is enabled only with an explicit recall/latency threshold.
8. Backup while the app is active, restore into a clean Compose project, and compare row counts, evidence-chain hashes, source-object checksums, and representative retrieval results.
9. Upgrade one pinned database/pgvector version at a time on a restored backup before applying it to the live named volume.
10. Explicit payload erasure leaves a tombstone and no recoverable sensitive payload in active storage or newly created backups.

## Decision triggers to revisit

Re-open this decision only with measured evidence:

- **Add Qdrant server** when the corpus or retrieval evaluation misses a documented latency/quality target that tuned PostgreSQL + pgvector cannot meet.
- **Add a SQLite edition** when a no-Docker installation becomes a product requirement and sqlite-vec has a stable compatibility story for the chosen runtime, or when exact search is proven sufficient without it.
- **Add a graph read model** when profiled recursive provenance queries fail UI latency targets on realistic graph sizes.
- **Add PITR** when the accepted recovery-point objective becomes smaller than the logical-backup interval.

Until one of those triggers is observed, PostgreSQL + pgvector has the smallest architecture that satisfies all correctness requirements without creating a second source of truth.
