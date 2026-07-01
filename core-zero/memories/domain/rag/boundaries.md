# RAG Pipeline — Boundaries

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Owns

- Query processing pipeline orchestration (safety → intelligence → retrieval → generation)
- Retrieval strategy selection and RRF fusion (CandidateMerger)
- Prompt injection defense (3-layer safety check)
- Context assembly and token budget management
- Grounded generation with citation extraction
- SSE streaming for real-time output
- Response persistence to SQLite

## Does Not Own

- Document ingestion and chunking — owned by Ingestion domain
- Vector DB indexing — owned by Ingestion domain
- Frontend display (chat UI, X-Ray Panel) — owned by Frontend domain
- Embedding generation — shared utility (owned by Ingestion)
- Provider abstraction (LLM/embedding API calls) — shared utility

## Integration Contracts

| Produces | Consumed By | Contract |
|----------|-------------|----------|
| Query results (with citations) | Frontend Chat screen | JSON via SSE + REST POST `/chat/send`, `/chat/history` |
| Chat history entries | SQLite via repositories | `ChatMessage` model → `chat_repository` |
| Safety check results | Query pipeline | Boolean + reason fields |
| Retrieved chunks | X-Ray Panel | `RetrievalResult[]` with scores and content |

## Invariants

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | The 3-layer safety check must run before any retrieval or generation | Without this, prompt injection attacks reach the LLM directly |
| INV-002 | Default retrieval must be hybrid (BM25 + vector) | Single-strategy retrieval is a degraded mode requiring explicit justification |
| INV-003 | SSE streams are append-only — never modify a stream mid-delivery | The frontend renders incrementally; mid-stream mutations break display |

## Change Rules

- Changes to the pipeline stage order require explanation in the task spec.
- New retrieval strategies should be added as parallel options, not replacements.
- Any change to safety logic must be regression-tested against all 3 layers.
- Cross-domain calls go through declared integration contracts only.

## Change Log

| Date | Feature Slug | Change Summary |
|------|--------------|----------------|
| 2026-06-28 | starter-init | Initial scaffold from archaeology sweep |
