# Document Ingestion — Boundaries

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Owns

- Document upload handling (file storage, validation)
- Document extraction (PDF, text, web URLs)
- Duplicate detection (file hash, text hash, similarity)
- Chunking strategy selection and execution (5 strategies)
- Embedding computation (via shared embedding client)
- Vector DB indexing (Weaviate)
- SQLite schema and migrations (16 tables, 4 versions)
- Provider abstraction for LLM/embedding APIs

## Does Not Own

- Query processing and retrieval — owned by RAG Pipeline domain
- Chat history persistence — owned by RAG Pipeline domain
- Frontend upload UI and document library — owned by Frontend domain

## Integration Contracts

| Produces | Consumed By | Contract |
|----------|-------------|----------|
| Indexed documents in Weaviate | RAG Pipeline retrieval | Weaviate schema with `document_id`, `content`, `metadata`, embedding vector |
| Document metadata in SQLite | RAG Pipeline context assembly | SQLite tables: `documents`, `sources`, `collections` |
| Document list | Frontend DocumentLibrary screen | REST GET `/documents`, `/collections` |
| Ingestion status | Frontend UI | REST GET `/ingestion/status`, SSE events |

## Invariants

| ID | Invariant | Rationale |
|----|-----------|-----------|
| INV-001 | Past migration versions are immutable | Editing applied migrations breaks the database state |
| INV-002 | Chunking strategy auto-selection by document type is the default | Manual override is available but the default should handle most cases |
| INV-003 | Duplicate detection runs before chunking and embedding | Skipping dedup wastes API calls and degrades search quality |

## Change Rules

- New chunking strategies must implement the shared interface.
- Schema changes require a new migration version, not edits to past versions.
- Embedding provider changes go through `providers/` abstraction layer, not direct imports.

## Change Log

| Date | Feature Slug | Change Summary |
|------|--------------|----------------|
| 2026-06-28 | starter-init | Initial scaffold from archaeology sweep |
