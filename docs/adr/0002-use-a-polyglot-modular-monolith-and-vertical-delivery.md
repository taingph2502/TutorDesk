---
status: accepted
---

# Use a polyglot modular monolith with vertical delivery

TutorDesk uses one polyglot monorepo containing a Next.js presentation adapter and one Python distribution with separate FastAPI, scheduler, processing-supervisor, source-worker, migration, and maintenance entrypoints. Authoritative state belongs to deep domain modules behind typed interfaces in one PostgreSQL database; Capabilities orchestrate those interfaces but own no durable state, and deferred work uses a transactional outbox plus PostgreSQL-backed jobs rather than independently deployed domain services or an external message broker. Delivery proceeds through runnable vertical milestones so every increment exercises its UI, domain behavior, persistence, recovery, and applicable release invariants.
