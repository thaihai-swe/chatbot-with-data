# Project Knowledge Base

## Purpose

This file stores durable repository memory for `chatbot-with-data`: stable facts, reusable implementation patterns, important boundaries, and brownfield watchouts that future agents should know before planning or changing code.

It complements `memories/repo/constitution.md`. The constitution says what contributors must do; this file records what is stably true about the repo.

## How Agents Should Use This File

- Read this file before writing or revising non-trivial feature artifacts.
- Use it to orient quickly to stable codebase structure and source-of-truth docs.
- Promote only durable findings here; keep feature-specific analysis in `artifacts/features/<slug>/`.

## Source Of Truth Map

- Domain or concern:
  Repository workflow and contributor guardrails
  Source of truth: `CLAUDE.md`, `memories/repo/constitution.md`
  Why it matters: these files define working rules, planning expectations, and editing constraints.

- Domain or concern:
  Product and feature intent
  Source of truth: `prd-requirement.md`, `PRODUCT_ROADMAP.md`, `artifacts/features/`
  Why it matters: roadmap and feature-artifact history explain what the system is trying to do and how changes are sequenced.

- Domain or concern:
  System architecture and operational setup
  Source of truth: `README.md`, `docs/onboarding.md`, `docs/system-architecture.md`, `docs/database-schema.md`, `docs/api-flows.md`
  Why it matters: these docs capture the intended backend/frontend/data-flow structure and setup model.

- Domain or concern:
  Frontend design expectations
  Source of truth: `design.md`, `frontend/src/`
  Why it matters: the repo treats `design.md` as the durable design guide for UI work.

## Stable Invariants

- Invariant:
  The repo is split into a FastAPI backend in `backend/` and a Vite + React frontend in `frontend/`.
  Why it matters: most changes should stay within one side of the boundary or cross it deliberately through documented API surfaces.
  Confidence: High
  Provenance: Observed in repo

- Invariant:
  The application uses SQLite for relational app data and Weaviate for vector and hybrid retrieval infrastructure.
  Why it matters: backend changes involving ingestion, retrieval, or document lifecycle usually need to account for both stores.
  Confidence: High
  Provenance: Observed in repo

- Invariant:
  The repository already follows a spec-driven feature workflow under `artifacts/features/<slug>/`, with `spec.md`, `plan.md`, and `tasks.md` used across multiple features.
  Why it matters: non-trivial work should plug into that workflow instead of inventing one-off planning artifacts.
  Confidence: High
  Provenance: Observed in repo

- Invariant:
  Frontend HTTP calls are organized under `frontend/src/api/`, while screens and components consume those modules.
  Why it matters: new UI behavior should usually extend an API helper first rather than embedding fetch logic directly in view components.
  Confidence: High
  Provenance: Observed in repo

## Decision Heuristics

- Heuristic:
  Prefer the nearest established module pattern over introducing a new abstraction style.
  Use when: editing existing backend packages or frontend screens/components.
  Avoid when: the task explicitly asks for a larger architectural change.
  Why it helps: this repo has several evolving subsystems, and local consistency lowers review and regression cost.

- Heuristic:
  Treat docs as orientation, then verify behavior in code when implementation details matter.
  Use when: requirements, API shape, or architecture claims affect a code change.
  Avoid when: the task is purely documentation maintenance.
  Why it helps: the repo has rich docs, but active feature work means code remains the final behavioral authority.

- Heuristic:
  Promote reusable findings only after they appear durable across more than one feature or subsystem.
  Use when: deciding whether something belongs in repo memory or should stay feature-local.
  Avoid when: the note is a one-off debugging result or temporary workaround.
  Why it helps: keeps repo memory concise and high signal.

## Known Good Patterns

- Pattern:
  Add or evolve user-facing backend behavior through dedicated backend modules plus router entry points.
  Use when: implementing ingestion, retrieval, chat, settings, or lifecycle features.
  Reference: `backend/routers/`, `backend/repositories/`, `backend/providers/`, `backend/schemas/`
  Notes: backend code is organized by concern; preserve those boundaries when extending behavior.

- Pattern:
  Keep frontend UI composition in screens/components and shared request logic in `frontend/src/api/`.
  Use when: adding new frontend actions or data fetches.
  Reference: `frontend/src/api/`, `frontend/src/screens/`, `frontend/src/components/`
  Notes: this reduces duplication and keeps UI modules thinner.

- Pattern:
  Document substantial feature work in `artifacts/features/<slug>/tasks.md` with explicit completion criteria.
  Use when: implementing or verifying non-trivial changes.
  Reference: `artifacts/features/3.grounded-chat-and-citations/`, `artifacts/features/14.provider-abstraction-layer/`
  Notes: existing features use this structure consistently enough to treat it as the house style.

## Anti-Patterns And Forbidden Moves

- Anti-pattern:
  Leaving durable repo conventions only in chat or transient review notes.
  Why it is harmful: future work has to rediscover the same constraints and patterns.
  Safer alternative: promote stable rules to the constitution and stable facts to this file.

- Anti-pattern:
  Mixing new request logic directly into frontend view files when `frontend/src/api/` is the established integration layer.
  Why it is harmful: it scatters backend contracts across the UI and makes later maintenance harder.
  Safer alternative: add or extend an API module and keep screens/components focused on state and presentation.

- Anti-pattern:
  Treating repository docs as automatically correct when changing behavior.
  Why it is harmful: docs can lag behind implementation during active feature development.
  Safer alternative: use docs for orientation, then verify the actual code path you are modifying.

## Boundaries And Ownership

- Boundary:
  Backend API surface vs. frontend consumption
  Owned by / primary area: `backend/routers/` and `frontend/src/api/`
  Why it matters: cross-stack changes should update both the server contract and the frontend integration layer coherently.
  Integration note: avoid bypassing these seams with ad hoc request handling.

- Boundary:
  Relational metadata vs. retrieval index
  Owned by / primary area: SQLite-backed backend modules and Weaviate-backed indexing/retrieval modules
  Why it matters: document ingestion, deletion, and reindexing often span both data systems.
  Integration note: lifecycle fixes should consider consistency between database records and vector-index state.

- Boundary:
  Repo-wide memory vs. feature-local artifacts
  Owned by / primary area: `memories/repo/` and `artifacts/features/`
  Why it matters: mixing them creates either bloated memory or missing historical context.
  Integration note: promote only durable cross-feature knowledge into repo memory.

## Shared Dependencies And Infrastructure

- Dependency or platform:
  FastAPI + Uvicorn
  Why it matters: this is the backend runtime and request-handling layer.
  Watchout: API changes usually ripple into schemas, routers, and frontend API consumers.

- Dependency or platform:
  React + Vite + Vitest
  Why it matters: this is the frontend app and its local test/build toolchain.
  Watchout: UI changes should respect the existing screen/component/API split and design guidance in `design.md`.

- Dependency or platform:
  OpenAI, SQLite, and Weaviate
  Why it matters: core RAG behavior depends on embeddings/generation, relational persistence, and vector retrieval together.
  Watchout: changes to ingestion, retrieval, safety, or provider selection can affect multiple integrations at once.

## Project Dictionary / Shared Language

- **Term:** Feature artifacts
  - **Definition:** The per-feature planning and execution files stored under `artifacts/features/<slug>/`.
  - **Context/Usage:** Used for `spec.md`, `plan.md`, and `tasks.md` in non-trivial work.
  - **Aliases:** feature docs, feature package

- **Term:** Repo memory
  - **Definition:** Durable agent-oriented repository knowledge stored under `memories/repo/`.
  - **Context/Usage:** Holds the constitution and project knowledge base.
  - **Aliases:** durable memory

- **Term:** Grounded chat
  - **Definition:** Chat answers generated from retrieved repository or uploaded-document context, with citations.
  - **Context/Usage:** Appears in README, docs, and feature artifacts around chat and citation behavior.
  - **Aliases:** cited chat, RAG chat

- **Term:** Hybrid retrieval
  - **Definition:** Retrieval that combines semantic/vector search with keyword-style search.
  - **Context/Usage:** Central to the system's RAG behavior and called out in README and architecture docs.
  - **Aliases:** hybrid search

## Stable Invariants

- Last major refresh date:
  2026-05-21
- What kinds of changes should trigger a refresh:
  repo structure changes, new durable workflows, architectural boundary shifts, or repeated lessons that span multiple features
- What does not belong here:
  one-off implementation notes, temporary fixes, feature-specific reasoning, or speculative future design

## Promotion Rules

- What belongs here:
  stable repository facts, cross-feature patterns, durable decision heuristics, and brownfield watchouts
- What should stay in feature artifacts under `artifacts/features/<slug>/`:
  feature-specific requirements, implementation sequencing, temporary analysis, and task tracking
- What should instead go to `memories/repo/constitution.md`:
  repo-wide rules, quality gates, and normative guardrails
- When a finding is durable enough to promote:
  when it is evidence-based, likely to remain true beyond one feature, and useful for future contributors
- How to record confidence or provenance when evidence is partial:
  state the confidence level and whether the fact comes from observed code, docs, or an explicit team convention
