# Frontend UI — Boundaries

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Owns

- All UI rendering (React components, screens, routing)
- UI state management (React state, effects)
- API client module organization
- Dev tooling (Vite dev server, vitest config)
- SSE stream consumption and display
- X-Ray Panel for retrieval debugging

## Does Not Own

- Backend business logic (RAG pipeline, ingestion) — owned by RAG/Ingestion domains
- Data persistence — backend-owned via REST API
- Authentication/authorization — not implemented yet

## Integration Contracts

| Produces | Consumed By | Contract |
|----------|-------------|----------|
| HTTP requests | Backend REST API | 7 router endpoints (health, chat, documents, collections, ingestion, settings, duplicate_decisions) |
| SSE event stream | Chat screen | Token events from `/chat/send` SSE endpoint |

## Invariants

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | API calls are made at the screen level, not in reusable components | Components must remain screen-agnostic for reusability |
| INV-002 | SSE streaming is consumed via an abstraction layer | Direct SSE-to-state coupling breaks when streaming format changes |

## Change Rules

- New screens go in `frontend/src/screens/` following existing patterns.
- New reusable components go in `frontend/src/components/`.
- New API endpoints require an API module update and optionally a client.js update.
- CSS changes should be scoped; no global style overrides without justification.

## Change Log

| Date | Feature Slug | Change Summary |
|------|--------------|----------------|
| 2026-06-28 | starter-init | Initial scaffold from archaeology sweep |
