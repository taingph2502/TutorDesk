---
status: accepted
---

# Use PostgreSQL with managed objects and rebuildable retrieval

TutorDesk uses PostgreSQL with pgvector as its sole authoritative database because learner-memory revisions, approvals, citations, and their exact provenance must commit and restore coherently. Large immutable originals live in an application-managed content-addressed directory, while PostgreSQL owns their identities, hashes, lifecycle state, and manifests. Core provenance uses constrained relation-specific tables; graph visualization and retrieval structures are derived read models behind deep domain-module interfaces.

Recovery Backups contain the database, authoritative objects, active expensive Evidence Representations, and active Retrieval Generation in a checksummed encrypted envelope. Portable Archives use a separate documented logical format for staged, dependency-complete transfer. Rebuildable Artifacts may be quota-evicted and regenerated, but authoritative evidence, learner state, provenance, decisions, Tombstones, and audit records may not. Database migrations and restored installations are verified before atomic activation; older restores must apply the latest available Erasure Ledger before exposing data.

SQLite remains a possible future no-Docker edition, and Qdrant or a graph read store may be added only as rebuildable projections when measurements demonstrate that PostgreSQL cannot meet an accepted quality or latency target. The complete rationale and operational contract are recorded in [Choose the persistence and indexing architecture](https://github.com/taingph2502/TutorDesk/issues/11).
