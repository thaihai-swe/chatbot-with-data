# Granular API Endpoint Flows

This document details the end-to-end flow for every API endpoint in the system, mapping frontend requests to backend service execution and data persistence.

---

## 1. Health & Status
| Method | Endpoint | Description | Internal Flow |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Check API availability | Router → returns `{"status": "ok"}` |

---

## 2. Ingestion & Duplicate Management
| Method | Endpoint | Description | Internal Flow |
| :--- | :--- | :--- | :--- |
| `POST` | `/ingestion/file-upload` | Upload a PDF/TXT/MD | Frontend (`FormData`) → Router → `IngestionService.submit_file_upload` → Save to Disk (UUID name) → Create SQLite Attempt → **Background Task** (`process_ingestion_attempt`) |
| `POST` | `/ingestion/url` | Submit a Web URL | Frontend (`JSON`) → Router → `IngestionService.submit_url` → Create SQLite Attempt → **Background Task** |
| `GET` | `/ingestion/attempts` | List all uploads | Frontend → Router → `Repository.list_ingestion_attempts` → SQLite Join (`attempts` + `collections`) |
| `GET` | `/ingestion/attempts/{id}` | Get status of an upload | Frontend → Router → `Repository.get_ingestion_attempt` → SQLite |
| `POST` | `/ingestion/attempts/{id}/duplicate-decision` | Resolve a collision | Frontend → Router → `IngestionService.apply_duplicate_decision` → Update SQLite Attempt → **Trigger Chunking/Indexing** (if Action != SKIP) |

---

## 3. Knowledge Base (Collections & Documents)
| Method | Endpoint | Description | Internal Flow |
| :--- | :--- | :--- | :--- |
| `GET` | `/collections` | List collections | Router → `Repository.list_collections` → SQLite (with `COUNT(document_id)`) |
| `POST` | `/collections` | Create collection | Router → `Repository.create_collection` → SQLite |
| `DELETE` | `/collections/{id}` | Delete collection | Router → `Repository.delete_collection` (Soft delete: `deleted_at`) → SQLite |
| `GET` | `/documents` | List docs | Router → `Repository.list_documents` → SQLite (Join with `ingestion_attempts` for status/duplicate signals) |
| `DELETE` | `/documents/{id}` | Delete document | Router → `Repository.delete_document` (Hard delete) → **Weaviate Cleanup** (`delete_by_document`) + **SQLite Cleanup** (Chunks, Embeddings, Index Entries) |
| `POST` | `/documents/{id}/move` | Re-scope document | Router → `Repository.assign_document_to_collections` → SQLite Update |
| `POST` | `/documents/{id}/reindex` | Refresh vectors | Router → `IngestionService._chunk_and_index_document` → SQLite (Chunks) → OpenAI (Embeddings) → Weaviate (Hybrid Index) |

---

## 4. Grounded Chat (RAG)
| Method | Endpoint | Description | Internal Flow |
| :--- | :--- | :--- | :--- |
| `POST` | `/chat/sessions` | Create session | Router → `ChatRepository.create_session` → SQLite |
| `GET` | `/chat/sessions` | History list | Router → `ChatRepository.list_sessions` → SQLite |
| `POST` | `/chat/sessions/{id}/turns/stream` | Streaming RAG | Router → `StreamingOrchestrator` → **SafetyService** (Query) → **AdvancedRetrievalService** (Multi-strategy) → **SafetyService** (Chunk Filter) → **GroundingService** (Evidence Check) → OpenAI (Stream Tokens) → **CitationService** (Validate) → SQLite Persistence |
| `POST` | `/chat/turns/{id}/cancel` | Stop generation | Router → `chat.cancellation` → Signal active stream to abort |

---

## 5. Storage Technical Detail

### SQLite (Metadata & Cache)
SQLite serves as the primary relational database and an embedding cache.
- **Documents/Chunks:** Stores the structural hierarchy and full text.
- **Embeddings Table:** Caches OpenAI responses. Before calling OpenAI, the system hashes the chunk text and checks this table to save cost/latency.
- **Citations Table:** Stores verified links between LLM claims and source chunks.

### Weaviate (Hybrid Search)
Weaviate is used for native hybrid search, combining vector similarity and keyword relevance.
- **Connectivity:** Port 8080 (REST) and 50051 (gRPC).
- **Hybrid Retrieval:** Supports an `alpha` parameter (0.0 to 1.0) to balance **BM25** (keyword) and **Semantic** (vector) scores.
- **Schema:** Managed as the `DocumentChunk` class, storing both the vector and the raw text properties.
