# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

- Frontend: Next.js App Router with TypeScript, Tailwind CSS, and `@xyflow/react` for the interactive memory graph.
- Backend and agent engine: Python with FastAPI.
- Relational and graph persistence: local SQLite or PostgreSQL running in local Docker; the final choice remains open. The chosen store must enforce the backward citation chain from L3 to L2 to L1.
- Vector search: a local embedded store such as `sqlite-vec`, Chroma, or embedded Qdrant; the final choice remains open.
- Model interface: provider-agnostic, supporting Google Gemini, OpenAI, Anthropic Claude, and local models through Ollama. Google Gemini is the default model for testing.
- Deployment: local-first, self-hosted containers through Docker Compose, with local development available through the frontend development server and Uvicorn.

## Users

TutorDesk is for one ambitious individual learner, self-directed researcher, or knowledge worker studying complex and diverse domains. It is a strictly single-user personal learning workspace. The user needs to turn heterogeneous study materials into deep, personalized mastery while retaining transparent control over how the system interprets their understanding and changes their learner state.

## Product Purpose

TutorDesk turns source materials into citation-grounded learning through one continuous agent-native workspace. It combines conversation, dynamic quizzing, deep research, visual explanations, multimodal source study, and learner-memory inspection in a shared session context. Success means the product adapts to the user's demonstrated comprehension over time, stays within the evidence supplied by the user's materials, and makes every important conclusion and memory change traceable and controllable.

## Positioning

TutorDesk is not a generic chat wrapper or a collection of disconnected study tools. Its distinguishing mechanism is a single day-to-day agent loop grounded in the user's source vault and calibrated by a transparent, inspectable three-tier learner-memory graph. A separate Agent Boardroom allows specialized agents to deliberate visibly, but their report remains advisory until the user explicitly approves any long-term memory update.

## Operating Context

- The primary experience is a desktop-first, information-dense web workstation in which the user can work across the active agent loop, source documents or media with citations, the three-tier Memory Graph, and the Agent Boardroom deliberation feed.
- The interface must operate seamlessly in English and Vietnamese, including UI copy, prompt behavior, and memory reasoning.
- The user ingests and studies text, images, tables, audio recordings, and video.
- All source files, interaction logs, and learner-memory data remain on the user's local filesystem and local database.
- Inference is hybrid and user-selectable: it can run locally through Ollama or use a supported cloud provider.
- When a cloud model is selected, TutorDesk sends only the minimum context chunks and system prompts required for the request over HTTPS. Raw, unindexed vault contents never leave the local environment.

## Capabilities and Constraints

- All routine chat, quizzing, research, and visual-explanation capabilities share one agent loop and unified session context.
- Factual claims require strict citations to supplied source material. The system must not silently extend beyond its evidence.
- Learner memory has three non-negotiable, inspectable layers:
  - **L1 — Raw Event Log:** an append-only log of every interaction.
  - **L2 — Contextual Facts:** curated facts, each citing the originating L1 event.
  - **L3 — Synthesized Profile:** cross-context learner insights, each citing the underlying L2 facts.
- Every memory insight must support backward provenance from L3 through L2 to L1.
- No learner-state mutation may happen silently. Long-term memory updates require transparent user control, and Agent Boardroom recommendations require explicit approval before being written.
- Multi-agent orchestration is reserved strictly for the user-triggered Agent Boardroom. Day-to-day interactions remain on the single-agent loop.
- The product must ingest and process text, images, tables, audio recordings, and video.
- TutorDesk is strictly single-user. It excludes multi-tenancy, classroom administration, enterprise overhead, code sandboxes, messaging-platform bots, community skill marketplaces, and external sub-agent OAuth integrations.
- User knowledge vaults have zero telemetry and no third-party cloud persistence.
- The specific relational store, vector store, and accessibility conformance target remain open decisions.

## Brand Commitments

- The product name is **TutorDesk**.
- Product behavior and language must communicate intellectual rigor, epistemic honesty, backward provenance, and human agency.
- Avoid generic, ungrounded, or performative AI output. Explanations should be precise, evidence-aware, and useful to a serious learner.
- Do not manufacture certainty: identify insufficient evidence and unresolved questions explicitly.

## Evidence on Hand

- The repository currently contains no application implementation, production content, datasets, testimonials, benchmarks, logos, or other proof assets.
- Future work must not invent testimonials, customers, measured learning outcomes, or unsupported product claims.

## Product Principles

1. **Ground every claim.** Learning guidance must remain tied to supplied evidence with usable citations.
2. **Make memory inspectable.** The learner can trace synthesized understanding backward through contextual facts to raw events.
3. **Keep the human in control.** Important learner-state changes are visible, reviewable, and never silently committed.
4. **Unify the learning loop.** Core study capabilities share context instead of fragmenting the learner across disconnected tools.
5. **Stay local by default.** Preserve the user's private knowledge vault locally and minimize any context sent for optional cloud inference.
