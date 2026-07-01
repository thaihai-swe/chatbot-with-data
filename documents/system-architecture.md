# System Architecture

**Status:** 🟢 Implemented  
**Last verified:** 2026-06-30  
**Source files:** `backend/app.py`, `backend/routers/`, `backend/chat/`, `backend/chunking/`, `backend/ingestion/`, `backend/indexing/`, `backend/migrations/runner.py`

---

## 1. System Overview

The RAG Knowledge Base Lab is a FastAPI backend + React frontend system that ingests documents, retrieves relevant chunks using hybrid search, and generates grounded answers with citations.

**Core data flow:**
```
Document Upload → Extraction → Duplicate Detection → Chunking → Embedding → Indexing
                                                                              ↓
Query → Safety Check → Query Intelligence → Retrieval → Reranking → Generation → Citations
```

---

## 2. Architecture Layers

### Backend Stack
- **Framework:** FastAPI (Python 3.10+)
- **Metadata DB:** SQLite (file-based, 16 tables)
- **Vector DB:** Weaviate (Docker, hybrid BM25 + semantic search)
- **Embedding Model:** OpenAI `text-embedding-3-small` (cached in SQLite)
- **LLM:** OpenAI GPT-4o (configurable via provider abstraction)
- **Async Runtime:** Python asyncio

### Frontend Stack
- **Framework:** React + Vite (JavaScript, not TypeScript)
- **Port:** 5173 (proxies `/api` to backend `:8000`)
- **Key screens:** Chat, Evaluation, DocumentLibrary, Collections, DuplicateDecision, Settings

---

## 3. Component Map

| Component | Location | Responsibility |
|-----------|----------|-----------------|
| **API Router** | `backend/routers/` | HTTP endpoints (health, ingestion, documents, collections, chat, settings, duplicate decisions) |
| **Chat Service** | `backend/chat/service.py` | Orchestrates retrieval, generation, streaming, citations |
| **Query Intelligence** | `backend/chat/retrieval.py::QueryIntelligenceService` | Query classification, expansion, decomposition, HyDE, synonym expansion, dynamic routing |
| **Retrieval Service** | `backend/chat/retrieval.py::RetrievalService` | Hybrid search (BM25 + semantic), multi-strategy retrieval |
| **RRF Merger** | `backend/chat/retrieval.py::CandidateMerger` | Reciprocal Rank Fusion for combining multi-strategy results |
| **Reranking** | `backend/chat/retrieval.py::RerankingService` | Post-retrieval ranking (currently dummy; sorts by similarity score) |
| **Generation** | `backend/chat/generation.py` | LLM answer generation with streaming |
| **Citations** | `backend/chat/citations.py` | Extract and link citations to source chunks |
| **Grounding** | `backend/chat/grounding.py` | Evaluate evidence and calculate groundedness score |
| **Safety** | `backend/chat/safety.py` | Three-layer prompt injection detection (heuristic, fuzzy, LLM) |
| **Streaming** | `backend/chat/streaming.py::StreamingOrchestrator` | Coordinate streaming responses via SSE |
| **Context Assembly** | `backend/chat/context.py` | Build LLM prompt from retrieved chunks + chat history |
| **Multi-Hop** | `backend/chat/multi_hop.py` | Sequential retrieval for multi-part questions |
| **Collection Routing** | `backend/chat/collection_routing.py` | Infer relevant collections from query |
| **Ingestion** | `backend/ingestion/service.py` | File upload, URL ingestion, duplicate detection, chunking, indexing |
| **Extractors** | `backend/extractors/` | PDF, text, web extraction (dispatcher auto-selects) |
| **Chunking** | `backend/chunking/` | Adaptive tiering + 5 strategies: fixed-size, heading-aware, page-aware, semantic, parent-child |
| **Duplicate Detection** | `backend/duplicate_detection/detector.py` | File hash, text hash, URL canonicalization, similarity-based detection |
| **Embeddings** | `backend/embeddings/openai_client.py` | Generate and cache embeddings |
| **Indexing** | `backend/indexing/weaviate_store.py` | Weaviate integration (hybrid search, SOLID abstraction) |
| **LLM Provider** | `backend/llm/client.py` | OpenAI client (configurable via provider abstraction) |
| **Repositories** | `backend/repositories/` | Data access layer (chat, chunk, embedding, index_entry, index_generation) |
| **Database** | `backend/database.py` | SQLite connection management |
| **Migrations** | `backend/migrations/runner.py` | Schema versioning and auto-migration on startup |
| **Config** | `backend/config.py` | Settings management (env vars, .env file, runtime updates) |
| **Error Handlers** | `backend/error_handlers/handlers.py` | Global error handling and recovery |

---

## 4. Database Schema (16 Tables)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `schema_migrations` | Track applied migrations | `version`, `applied_at` |
| `collections` | Document collections/categories | `id`, `name`, `description`, `routing_enabled` |
| `documents` | Ingested documents | `id`, `title`, `source_type`, `file_hash`, `normalized_text_hash`, `version_of_document_id`, `deleted_at` |
| `document_collections` | M:M relationship (doc ↔ collection) | `document_id`, `collection_id` |
| `ingestion_attempts` | Track ingestion jobs | `id`, `document_id`, `status`, `duplicate_status`, `duplicate_match_document_id`, `error_message` |
| `ingestion_attempt_collections` | M:M relationship (attempt ↔ collection) | `ingestion_attempt_id`, `collection_id` |
| `lifecycle_events` | Audit trail for documents | `id`, `document_id`, `event_type`, `from_status`, `to_status` |
| `duplicate_decisions` | User decisions on duplicates | `id`, `ingestion_attempt_id`, `classification`, `action`, `final_status` |
| `chunks` | Document chunks | `id`, `document_id`, `collection_id`, `text`, `strategy`, `page_number`, `parent_chunk_id`, `semantic_score` |
| `embeddings` | Cached embeddings | `id`, `chunk_id`, `embedding_model`, `embedding_vector` (BLOB), `input_text_hash` |
| `index_generations` | Index versioning | `id`, `document_id`, `generation_number`, `status`, `embedding_model`, `chunk_count` |
| `index_entries` | Index entries (chunk ↔ embedding ↔ generation) | `id`, `chunk_id`, `embedding_id`, `generation_id`, `vector_db_id` |
| `chat_sessions` | Chat sessions | `id`, `collection_id`, `metadata_json`, `created_at` |
| `chat_turns` | Query/answer pairs | `id`, `session_id`, `query_text`, `answer_text`, `status`, `safety_status`, `groundedness_score` |
| `citations` | Answer citations | `id`, `turn_id`, `chunk_id`, `document_id`, `quote_text` |
| `chat_session_collections` | M:M relationship (session ↔ collection) | `session_id`, `collection_id` |

**Note:** Schema inconsistency flagged: `chat_sessions.collection_id` is singular (TEXT), but `ChatSession` model uses `collection_ids: List[str]` and `chat_session_collections` join table exists. This should be resolved in a future migration.

---

## 5. API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Health check |
| `POST` | `/ingestion/file-upload` | Upload document (async, returns attempt ID) |
| `POST` | `/ingestion/url` | Ingest URL (async) |
| `GET` | `/ingestion/attempts` | List ingestion attempts |
| `GET` | `/ingestion/attempts/{attempt_id}` | Get attempt details |
| `POST` | `/ingestion/attempts/{attempt_id}/duplicate-decision` | Decide on duplicate |
| `GET` | `/documents` | List documents |
| `GET` | `/documents/{document_id}` | Get document details |
| `DELETE` | `/documents/{document_id}` | Delete document |
| `POST` | `/documents/{document_id}/move` | Move document to collection |
| `POST` | `/documents/{document_id}/reindex` | Reindex document |
| `POST` | `/documents/{document_id}/reingest` | Re-ingest document |
| `GET` | `/collections` | List collections |
| `POST` | `/collections` | Create collection |
| `GET` | `/collections/{collection_id}` | Get collection |
| `PATCH` | `/collections/{collection_id}` | Update collection |
| `DELETE` | `/collections/{collection_id}` | Delete collection |
| `POST` | `/chat/sessions` | Create chat session |
| `GET` | `/chat/sessions` | List sessions |
| `GET` | `/chat/sessions/{session_id}` | Get session |
| `DELETE` | `/chat/sessions/{session_id}` | Delete session |
| `GET` | `/chat/sessions/{session_id}/history` | Get chat history |
| `POST` | `/chat/sessions/{session_id}/turns` | Create turn (non-streaming) |
| `POST` | `/chat/sessions/{session_id}/turns/stream` | Create turn (streaming SSE) |
| `POST` | `/chat/turns/{turn_id}/cancel` | Cancel streaming turn |
| `POST` | `/chat/evaluate/sanity-check` | Run evaluation on golden dataset |
| `GET` | `/settings` | Get all settings |
| `PUT` | `/settings` | Update settings |

---

## 6. Data Flow: Ingestion

```
1. User uploads file/URL via frontend
   ↓
2. POST /ingestion/file-upload or /ingestion/url
   ↓
3. Backend creates ingestion_attempt (status: pending)
   ↓
4. BackgroundTasks queues process_ingestion_attempt()
   ↓
5. Extract text (PDF/TXT/Web)
   ↓
6. Detect duplicates (file hash, text hash, similarity)
   ↓
7. If duplicate detected:
   - Create duplicate_decision record
   - Wait for user decision (skip/replace/variant/merge)
   ↓
8. Chunk document (auto-select strategy: page-aware for PDF, heading-aware for MD, fixed-size for TXT)
   ↓
9. Generate embeddings (OpenAI text-embedding-3-small, cached in SQLite)
   ↓
10. Index chunks in Weaviate (hybrid search: BM25 + semantic)
    ↓
11. Create document, chunks, embeddings, index_entries records
    ↓
12. Update ingestion_attempt (status: completed)
```

---

## 7. Data Flow: Query & Retrieval

```
1. User sends query via chat UI
   ↓
2. POST /chat/sessions/{session_id}/turns/stream
   ↓
3. Safety check (heuristic + fuzzy + LLM injection detection)
   ↓
4. Query intelligence:
   - Classify query type (factual/comparative/how-to/troubleshooting/exploratory)
   - Dynamic routing selects strategy (baseline/expansion/decomposition/hyde/synonym)
   - Rewrite, expand, decompose, or generate HyDE as needed
   ↓
5. Multi-strategy retrieval (parallel):
   - BM25 (keyword search)
   - Semantic (vector search)
   - HyDE (if enabled)
   ↓
6. Merge results via RRF (Reciprocal Rank Fusion)
   ↓
7. Rerank results (currently dummy; sorts by similarity score)
   ↓
8. Select top-k chunks within context window
   ↓
9. Assemble context:
   - Format retrieved chunks
   - Include chat history (sliding window of 10 turns)
   - Build system + user prompts
   ↓
10. Stream LLM response token-by-token via SSE
    ↓
11. Extract citations (link claims to source chunks)
    ↓
12. Calculate groundedness score
    ↓
13. Store turn, citations, and metrics in SQLite
```

---

## 8. Key Features

### Query Intelligence (Pre-Retrieval)
- **Classification:** Detects query type (factual, comparative, how-to, troubleshooting, exploratory)
- **Expansion:** Generates 3–5 alternative phrasings
- **Decomposition:** Breaks multi-part questions into sub-queries
- **HyDE:** Generates hypothetical relevant documents
- **Synonym Expansion:** Domain-specific vocabulary mapping
- **Dynamic Routing:** Selects optimal strategy based on query type

### Retrieval
- **Hybrid Search:** BM25 (keyword) + semantic (vector) via Weaviate
- **Multi-Strategy:** Parallel retrieval with RRF merging
- **Reranking:** Post-retrieval ranking (placeholder; real cross-encoder pending)
- **Collection Filtering:** Query within specific collections
- **Parent-Child Retrieval:** Hierarchical indexing for precision + context

### Chunking
- **Adaptive Tiering:** Full-doc injection for small docs (Notebook LM style); configurable threshold
- **Fixed-Size:** Plain text with configurable overlap
- **Heading-Aware:** Heading paths prepended to chunk text via recursive extraction; preserves full section lineage
- **Page-Aware:** PDFs; respects page boundaries
- **Semantic:** Embedding-based cosine similarity for boundary detection; Jaccard fallback on >5s timeout
- **Parent-Child:** Boundary-aware grouping (aligns parents with heading boundaries)

### Safety
- **Heuristic Scanner:** 49 regex patterns across 8 attack categories
- **Fuzzy Scanner:** Cosine similarity to known injection corpus (70% threshold)
- **LLM Scanner:** LLM judges adversarial intent
- **Configurable Modes:** Strict (0.5), Moderate (0.7), Lenient (0.9) thresholds

### Grounding & Citations
- **Grounding:** LLM generates answers only from retrieved context
- **Citations:** Every claim linked to source chunks with page numbers
- **Streaming:** Token-by-token response streaming

### Conversation Memory
- **Session History:** Multi-turn context with sliding window (10 turns)
- **Reference Resolution:** Resolves pronouns to prior turns
- **Metadata Tracking:** Topic, quality metrics per session

---

## 9. Configuration

Settings are managed via:
1. **Environment variables** (`.env` file or system env)
2. **`config/settings.json`** (persistent config)
3. **Runtime updates** via `PUT /settings`

Key settings:
- `OPENAI_API_KEY` — LLM and embedding API key
- `WEAVIATE_URL` — Vector DB endpoint (default: `http://localhost:8080`)
- `DATABASE_PATH` — SQLite file path
- `CHUNKING_STRATEGY` — Default chunking strategy
- `RETRIEVAL_MODE` — Hybrid/semantic/keyword
- `SAFETY_MODE` — Strict/moderate/lenient
- Feature toggles: `query_expansion_enabled`, `query_decomposition_enabled`, `hyde_enabled`, `reranking_enabled`, etc.

---

## 10. Deployment

### Local Development
```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up -d  # Starts Weaviate on port 8080
```

Migrations run automatically on backend startup via `app.py:65` (`apply_migrations()`).

---

## 11. Known Limitations & Roadmap

### Current Limitations
- **Reranker:** Dummy implementation (sorts by similarity score). Real cross-encoder (`BAAI/bge-reranker-base`) pending.
- **Ingestion:** Uses in-process `BackgroundTasks` (not durable). Celery/RQ job queue pending.
- **PII Detection:** Not implemented (roadmap item).
- **RAGAS Metrics:** Evaluation harness exists; full RAGAS metrics pending.
- **Conversation Memory:** Sliding window only; no context compression or advanced coreference.

### Roadmap
See [`docs/enhancement-recommendations.md`](./enhancement-recommendations.md) and [`rag-prd-requirement.md`](../rag-prd-requirement.md) for planned features.

---

## 12. Cross-References

- **Onboarding:** [`docs/onboarding.md`](./onboarding.md)
- **API Flows:** [`docs/api-flows.md`](./api-flows.md)
- **Database Schema:** [`docs/database-schema.md`](./database-schema.md)
- **Retrieval Deep Dive:** [`docs/RETRIEVAL_FLOW.md`](./RETRIEVAL_FLOW.md)
- **Chunking Strategies:** [`docs/CHUNKING_STRATEGIES.md`](./CHUNKING_STRATEGIES.md)
- **Safety & Injection Detection:** [`docs/PROMPT_INJECTION_DETECTION.md`](./PROMPT_INJECTION_DETECTION.md)
