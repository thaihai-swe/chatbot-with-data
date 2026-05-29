# Database Schema & Data Architecture

**Status:** 🟢 Implemented  
**Last verified:** 2026-05-29  
**Source files:** `backend/migrations/runner.py`, `backend/models/`, `backend/repositories/`

---

## Overview

The system uses a **dual-database architecture**:

- **SQLite** — Relational metadata: documents, chunks, embeddings cache, chat history, citations, ingestion tracking, index versioning
- **Weaviate** — Vector index for hybrid search (BM25 + semantic)

SQLite is file-based (`data/knowledge_ingestion/app.db` by default) and auto-migrated on backend startup.

---

## Schema Diagram (ER)

```
┌─────────────────────────────────────────────────────────────────┐
│                      Collections                                │
│  id (PK) | name | description | routing_enabled | created_at   │
└────────────────────────┬──────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Documents      │ │ Ingestion        │ │ Chat Sessions    │
│ id (PK)          │ │ Attempts         │ │ id (PK)          │
│ title            │ │ id (PK)          │ │ collection_id    │
│ source_type      │ │ document_id (FK) │ │ metadata_json    │
│ file_hash        │ │ status           │ │ created_at       │
│ deleted_at       │ │ duplicate_status │ │                  │
└────────┬─────────┘ └──────────────────┘ └────────┬─────────┘
         │                                         │
         ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│     Chunks       │                    │   Chat Turns     │
│ id (PK)          │                    │ id (PK)          │
│ document_id (FK) │                    │ session_id (FK)  │
│ text             │                    │ query_text       │
│ page_number      │                    │ answer_text      │
│ parent_chunk_id  │                    │ groundedness_scr │
└────────┬─────────┘                    └────────┬─────────┘
         │                                       │
         ▼                                       ▼
┌──────────────────┐                    ┌──────────────────┐
│   Embeddings     │                    │   Citations      │
│ id (PK)          │                    │ id (PK)          │
│ chunk_id (FK)    │                    │ turn_id (FK)     │
│ embedding_vector │                    │ chunk_id (FK)    │
│ (BLOB)           │                    │ quote_text       │
└──────────────────┘                    └──────────────────┘

Index Versioning:
┌──────────────────┐
│ Index            │
│ Generations      │
│ id (PK)          │
│ document_id (FK) │
│ generation_num   │
│ status           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Index Entries   │
│ id (PK)          │
│ chunk_id (FK)    │
│ embedding_id (FK)│
│ generation_id(FK)│
│ vector_db_id     │
└──────────────────┘
```

---

## 16 Tables

### 1. schema_migrations
Tracks applied database migrations.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `version` | TEXT | PRIMARY KEY | Migration version identifier |
| `applied_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When migration was applied |

**Indexes:** None (PK is sufficient)

---

### 2. collections
Document collections/categories for organizing knowledge.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique collection ID |
| `name` | TEXT | NOT NULL, UNIQUE | Human-readable name |
| `description` | TEXT | | Optional description |
| `is_default` | INTEGER | NOT NULL, DEFAULT 0 | Whether this is the default collection |
| `routing_enabled` | INTEGER | NOT NULL, DEFAULT 0 | Whether automatic collection routing is enabled |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `deleted_at` | TEXT | | Soft delete timestamp (NULL = active) |

**Indexes:** None (name is UNIQUE)

**Use case:** Organize documents by domain, project, or access level.

---

### 3. documents
Ingested documents (PDFs, text files, web pages).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique document ID |
| `title` | TEXT | NOT NULL | Document title |
| `source_type` | TEXT | NOT NULL | Source type: pdf, txt, md, web |
| `source_uri` | TEXT | | Original source (file path or URL) |
| `canonical_source_uri` | TEXT | | Normalized source URI (for dedup) |
| `filename` | TEXT | | Original filename (if uploaded) |
| `mime_type` | TEXT | | MIME type (e.g., application/pdf) |
| `file_hash` | TEXT | | SHA256 hash of file (for dedup) |
| `normalized_text_hash` | TEXT | | Hash of normalized text (for dedup) |
| `extracted_text` | TEXT | | Full extracted text |
| `metadata_json` | TEXT | NOT NULL, DEFAULT '{}' | Custom metadata (JSON) |
| `version_of_document_id` | TEXT | FOREIGN KEY → documents(id) | If this is a version of another doc |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |
| `deleted_at` | TEXT | | Soft delete timestamp (NULL = active) |

**Indexes:** None (PK is sufficient)

**Use case:** Track all ingested documents with dedup hashes and versioning.

---

### 4. document_collections
M:M relationship between documents and collections.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `document_id` | TEXT | NOT NULL, FK → documents(id) ON DELETE CASCADE | Document reference |
| `collection_id` | TEXT | NOT NULL, FK → collections(id) ON DELETE CASCADE | Collection reference |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When association was created |

**Primary Key:** (document_id, collection_id)

**Use case:** A document can belong to multiple collections.

---

### 5. ingestion_attempts
Track document ingestion jobs (async operations).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique attempt ID |
| `document_id` | TEXT | FK → documents(id) ON DELETE SET NULL | Associated document (NULL until completed) |
| `source_type` | TEXT | NOT NULL | Source type: pdf, txt, md, web |
| `status` | TEXT | NOT NULL | Status: pending, completed, error, duplicate_detected |
| `submitted_filename` | TEXT | | Filename as submitted |
| `source_uri` | TEXT | | Source URI (file path or URL) |
| `canonical_source_uri` | TEXT | | Normalized source URI |
| `mime_type` | TEXT | | MIME type |
| `artifact_path` | TEXT | | Path to uploaded file (temporary) |
| `snapshot_path` | TEXT | | Path to snapshot (for debugging) |
| `title` | TEXT | | Extracted or inferred title |
| `extracted_text` | TEXT | | Full extracted text |
| `metadata_json` | TEXT | NOT NULL, DEFAULT '{}' | Metadata (JSON) |
| `file_hash` | TEXT | | File hash (for dedup) |
| `normalized_text_hash` | TEXT | | Normalized text hash (for dedup) |
| `duplicate_status` | TEXT | | Duplicate classification: unique, exact_duplicate, near_duplicate, same_url, etc. |
| `duplicate_match_document_id` | TEXT | FK → documents(id) ON DELETE SET NULL | If duplicate, which document it matches |
| `duplicate_evidence_json` | TEXT | | Evidence for duplicate classification (JSON) |
| `error_message` | TEXT | | Error message if status = error |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When attempt was created |
| `updated_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update |
| `completed_at` | TEXT | | When attempt completed (NULL if pending) |

**Indexes:** None (PK is sufficient)

**Use case:** Track async ingestion jobs; support polling for completion and duplicate detection workflow.

---

### 6. ingestion_attempt_collections
M:M relationship between ingestion attempts and collections.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `ingestion_attempt_id` | TEXT | NOT NULL, FK → ingestion_attempts(id) ON DELETE CASCADE | Attempt reference |
| `collection_id` | TEXT | NOT NULL, FK → collections(id) ON DELETE CASCADE | Collection reference |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When association was created |

**Primary Key:** (ingestion_attempt_id, collection_id)

**Use case:** An ingestion attempt can target multiple collections.

---

### 7. lifecycle_events
Audit trail for document state changes.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique event ID |
| `document_id` | TEXT | FK → documents(id) ON DELETE CASCADE | Document reference |
| `ingestion_attempt_id` | TEXT | FK → ingestion_attempts(id) ON DELETE CASCADE | Attempt reference (if applicable) |
| `event_type` | TEXT | NOT NULL | Event type: ingested, reindexed, deleted, moved, etc. |
| `from_status` | TEXT | | Previous status (if applicable) |
| `to_status` | TEXT | | New status (if applicable) |
| `details_json` | TEXT | NOT NULL, DEFAULT '{}' | Event details (JSON) |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When event occurred |

**Indexes:** None (PK is sufficient)

**Use case:** Audit trail for compliance and debugging.

---

### 8. duplicate_decisions
User decisions on duplicate documents.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique decision ID |
| `ingestion_attempt_id` | TEXT | NOT NULL, FK → ingestion_attempts(id) ON DELETE CASCADE | Attempt that triggered duplicate |
| `document_id` | TEXT | FK → documents(id) ON DELETE SET NULL | New document (if applicable) |
| `matched_document_id` | TEXT | FK → documents(id) ON DELETE SET NULL | Existing document that matched |
| `classification` | TEXT | NOT NULL | Duplicate classification (from detector) |
| `detection_method` | TEXT | NOT NULL | How duplicate was detected: file_hash, text_hash, similarity, etc. |
| `evidence_json` | TEXT | NOT NULL, DEFAULT '{}' | Evidence for classification (JSON) |
| `action` | TEXT | NOT NULL | User decision: skip, replace, variant, merge |
| `final_status` | TEXT | NOT NULL | Result: skipped, replaced, created_variant, merged |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When decision was made |

**Indexes:** None (PK is sufficient)

**Use case:** Track duplicate detection and user decisions.

---

### 9. chunks
Document chunks (pieces of text indexed in vector DB).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique chunk ID |
| `document_id` | TEXT | NOT NULL, FK → documents(id) ON DELETE CASCADE | Parent document |
| `collection_id` | TEXT | NOT NULL, FK → collections(id) ON DELETE CASCADE | Collection (denormalized for query efficiency) |
| `chunk_order` | INTEGER | NOT NULL | Sequential order within document |
| `strategy` | TEXT | NOT NULL | Chunking strategy used: fixed_size, heading_aware, page_aware, semantic, parent_child |
| `source_type` | TEXT | NOT NULL | Source type of parent document |
| `title` | TEXT | | Chunk title (if applicable) |
| `section_title` | TEXT | | Section heading (if applicable) |
| `page_number` | INTEGER | | Page number (for PDFs) |
| `source_url` | TEXT | | Source URL (for web content) |
| `text` | TEXT | NOT NULL | Chunk text |
| `text_length` | INTEGER | NOT NULL | Length of text in characters |
| `parent_chunk_id` | TEXT | FK → chunks(id) ON DELETE CASCADE | Parent chunk (for parent-child strategy) |
| `fallback_applied` | INTEGER | NOT NULL, DEFAULT 0 | Whether fallback chunking was used |
| `semantic_score` | REAL | | Semantic continuity score (for semantic chunking) |
| `metadata_json` | TEXT | NOT NULL, DEFAULT '{}' | Custom metadata (JSON) |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_chunks_document_id` on `document_id`
- `idx_chunks_collection_id` on `collection_id`
- `idx_chunks_parent_id` on `parent_chunk_id`

**Use case:** Store all chunks for retrieval and citation.

---

### 10. embeddings
Cached embeddings for chunks.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique embedding ID |
| `chunk_id` | TEXT | NOT NULL, FK → chunks(id) ON DELETE CASCADE | Chunk reference |
| `embedding_model` | TEXT | NOT NULL | Model used: text-embedding-3-small, text-embedding-3-large, etc. |
| `embedding_model_version` | TEXT | | Model version (for tracking changes) |
| `embedding_vector` | BLOB | NOT NULL | Embedding vector (serialized, e.g., pickle or msgpack) |
| `input_text_hash` | TEXT | NOT NULL | Hash of input text (for cache validation) |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When embedding was generated |

**Indexes:**
- `idx_embeddings_chunk_id` on `chunk_id`

**Unique constraint:** (chunk_id, embedding_model) — one embedding per chunk per model

**Use case:** Cache embeddings to avoid recomputation; support multiple embedding models.

---

### 11. index_generations
Track index versions (for re-embedding, schema changes, etc.).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique generation ID |
| `document_id` | TEXT | NOT NULL, FK → documents(id) ON DELETE CASCADE | Document reference |
| `generation_number` | INTEGER | NOT NULL | Sequential generation number |
| `status` | TEXT | NOT NULL | Status: pending, completed, failed |
| `strategy` | TEXT | NOT NULL | Chunking strategy used |
| `settings_hash` | TEXT | | Hash of settings used (for detecting changes) |
| `embedding_model` | TEXT | | Embedding model used |
| `chunk_count` | INTEGER | | Number of chunks generated |
| `is_active` | INTEGER | NOT NULL, DEFAULT 1 | Whether this is the active generation |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When generation started |
| `completed_at` | TEXT | | When generation completed |

**Indexes:**
- `idx_index_generations_document_id` on `document_id`

**Unique constraint:** (document_id, generation_number)

**Use case:** Support index versioning, re-embedding, and blue/green index swaps.

---

### 12. index_entries
Links chunks to embeddings to generations (for index lifecycle management).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique entry ID |
| `chunk_id` | TEXT | NOT NULL, FK → chunks(id) ON DELETE CASCADE | Chunk reference |
| `embedding_id` | TEXT | NOT NULL, FK → embeddings(id) ON DELETE CASCADE | Embedding reference |
| `document_id` | TEXT | NOT NULL, FK → documents(id) ON DELETE CASCADE | Document reference (denormalized) |
| `collection_id` | TEXT | NOT NULL, FK → collections(id) ON DELETE CASCADE | Collection reference (denormalized) |
| `generation_id` | TEXT | NOT NULL, FK → index_generations(id) ON DELETE CASCADE | Generation reference |
| `vector_db_id` | TEXT | | ID in Weaviate (for tracking) |
| `is_active` | INTEGER | NOT NULL, DEFAULT 1 | Whether this entry is active |
| `chunk_order` | INTEGER | NOT NULL | Chunk order (denormalized) |
| `parent_chunk_id` | TEXT | | Parent chunk ID (denormalized) |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_index_entries_chunk_id` on `chunk_id`
- `idx_index_entries_generation_id` on `generation_id`

**Use case:** Track which chunks are indexed in which generation; support index lifecycle operations.

---

### 13. chat_sessions
Chat sessions (conversations).

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique session ID |
| `collection_id` | TEXT | FK → collections(id) ON DELETE SET NULL | Collection scope (NULL = all collections) |
| `metadata_json` | TEXT | NOT NULL, DEFAULT '{}' | Session metadata: user_id, topic, etc. (JSON) |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:** None (PK is sufficient)

**Note:** Schema inconsistency — `collection_id` is singular, but `ChatSession` model uses `collection_ids: List[str]` and `chat_session_collections` join table exists. Should be resolved in future migration.

**Use case:** Store chat sessions with optional collection scoping.

---

### 14. chat_turns
Query/answer pairs within a session.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique turn ID |
| `session_id` | TEXT | NOT NULL, FK → chat_sessions(id) ON DELETE CASCADE | Session reference |
| `query_text` | TEXT | NOT NULL | User query |
| `answer_text` | TEXT | | Generated answer |
| `retrieved_chunks_json` | TEXT | NOT NULL, DEFAULT '[]' | Retrieved chunk IDs/metadata (JSON) |
| `context_used_json` | TEXT | NOT NULL, DEFAULT '{}' | Context assembled for LLM: prompts, retrieval results (JSON) |
| `status` | TEXT | NOT NULL, DEFAULT 'pending' | Status: pending, generating, completed, error, cancelled |
| `safety_status` | TEXT | | Safety check result: pass, fail, warning |
| `safety_risk_score` | REAL | | Injection risk score (0.0-1.0) |
| `safety_reason` | TEXT | | Reason for safety status |
| `groundedness_score` | REAL | | Groundedness score (0.0-1.0) |
| `error_message` | TEXT | | Error message if status = error |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| `updated_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_chat_turns_session_id` on `session_id`

**Use case:** Store all query/answer pairs with metrics and traces.

---

### 15. citations
Citations linking answers to source chunks.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | TEXT | PRIMARY KEY | Unique citation ID |
| `turn_id` | TEXT | NOT NULL, FK → chat_turns(id) ON DELETE CASCADE | Turn reference |
| `chunk_id` | TEXT | NOT NULL, FK → chunks(id) ON DELETE CASCADE | Chunk reference |
| `document_id` | TEXT | NOT NULL, FK → documents(id) ON DELETE CASCADE | Document reference (denormalized) |
| `quote_text` | TEXT | | Quoted text from chunk |
| `metadata_json` | TEXT | NOT NULL, DEFAULT '{}' | Citation metadata (JSON) |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

**Indexes:**
- `idx_citations_turn_id` on `turn_id`

**Use case:** Link answer claims to source chunks for grounding and transparency.

---

### 16. chat_session_collections
M:M relationship between chat sessions and collections.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `session_id` | TEXT | NOT NULL, FK → chat_sessions(id) ON DELETE CASCADE | Session reference |
| `collection_id` | TEXT | NOT NULL, FK → collections(id) ON DELETE CASCADE | Collection reference |
| `created_at` | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When association was created |

**Primary Key:** (session_id, collection_id)

**Use case:** A session can be scoped to multiple collections (resolves schema inconsistency in chat_sessions).

---

## Known Issues

### Schema Inconsistency
`chat_sessions.collection_id` is singular (TEXT), but the model and join table suggest multi-collection support. This should be resolved in a future migration:
- Option 1: Drop `chat_sessions.collection_id`, rely on `chat_session_collections` join table
- Option 2: Rename `chat_sessions.collection_id` to `default_collection_id` for clarity

---

## Migrations

Migrations are versioned and tracked in `schema_migrations` table. New migrations are applied automatically on backend startup via `backend/migrations/runner.py`.

To add a new migration:
1. Add SQL statements to `MIGRATIONS` list in `runner.py`
2. Restart backend (migrations run on startup)
3. Verify in `schema_migrations` table

---

## Cross-References

- **System Architecture:** [`docs/system-architecture.md`](./system-architecture.md)
- **API Flows:** [`docs/api-flows.md`](./api-flows.md)
- **Migrations:** `backend/migrations/runner.py`
