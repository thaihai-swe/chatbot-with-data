# Domain — Boundaries

> Ownership: Collaborative — skill-updated + user-maintained.
> Updated by: `/context-memory` post-ship sync when a feature changes domain ownership, an integration contract evolves, or an invariant is added/removed.
> Read by: `/spec-requirements`, `/spec-plan`, `/spec-implement`, `/harness-verify` to prevent boundary violations and regression.

Defines what the RAG Chat domain owns, does not own, how it integrates with adjacent domains, and the invariants that must never be violated.

## Owns

- SSE Event Stream serialization & formatting logic
- Pre-generation safety checks and grounding gating validation
- Smart text chunking mechanisms (adaptive, heading-aware, parent-child, semantic)
- Document ingestion processing (duplicate detection, uniqueness validation, indexing registry)
- Retrieval service (executing hybrid keyword/vector search targeting Weaviate)

## Does Not Own

- SQLite storage engine internals (handled via sqlite3 stdlib)
- Weaviate vector DB server instances (run in Docker context)
- OpenAI API inference infrastructure (hosted externally by OpenAI)
- HTTP/CORS transport routers (FastAPI app configuration)

## Integration Contracts

| Produces | Consumed By | Contract |
|-|-|-|
| SSE Event Stream | React Frontend Client | Event: `status`, `token`, `citations`, `error`, `done` |
| DB connection | Backend Repositories | Thread-safe `@contextmanager get_connection()` |
| Vector Queries | Weaviate DB | `weaviate.connect_to_local(...)` |

## Invariants

Rules that must never be violated when working in this domain. The agent must check these before implementing any change that touches this domain.

| ID | Invariant | Rationale |
|-|-|-|
| INV-001 | Streaming responses must use Server-Sent Events (SSE) format | Frontend parser expects exact event-name/data-payload structure |
| INV-002 | Pre-generation Safety check must occur before querying OpenAI API | Prevents unsafe prompts from ever reaching downstream LLMs |
| INV-003 | If grounding check fails, refusal must stream token-by-token and end turn | Ensures the LLM is not queried when grounding evidence is insufficient |
| INV-004 | Ingestion unique constraint checks must halt on non-unique duplicates | Prevents duplicate document indexing in Weaviate / SQLite |

*Add INV-005, INV-006, … as invariants are discovered. Never renumber or remove an ID — mark retired ones `Retired in <feature-slug> on <date>`.*

## Change Rules

- Domain interfaces are stable contracts. Changes require an ADR.
- Domain events are append-only. New fields may be added; existing fields must not be removed.
- Cross-domain calls go through declared integration contracts only — never direct imports.
- Any change to `## Invariants` must be reflected in the `## Change Log` below.

## Change Log

*Append one row per merged feature that modifies this file. Most recent first.*

| Date | Feature Slug | Change Summary |
|-|-|-|
| 2026-07-11 | starter-init | Initial RAG boundaries definition |
