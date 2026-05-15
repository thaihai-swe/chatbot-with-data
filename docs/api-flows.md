# Granular API Endpoint Flows

This document details the end-to-end flow for every API endpoint in the system.

---

## 1. Health & Status
| Method | Endpoint | Description | Flow |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Check API availability | Router → returns `{"status": "ok"}` |

---

## 2. Ingestion & Duplicate Management
| Method | Endpoint | Description | Flow |
| :--- | :--- | :--- | :--- |
| `POST` | `/ingestion/file-upload` | Upload a PDF/TXT | Frontend (`FormData`) → Router → `IngestionService.submit_file_upload` → Save to Disk → Create SQLite Attempt → **Trigger Background Task** (`process_ingestion_attempt`) |
| `POST` | `/ingestion/url` | Submit a Web URL | Frontend (`JSON`) → Router → `IngestionService.submit_url` → Create SQLite Attempt → **Trigger Background Task** |
| `GET` | `/ingestion/attempts` | List all uploads | Frontend → Router → `IngestionRepository.list_ingestion_attempts` → SQLite |
| `GET` | `/ingestion/attempts/{id}` | Get status of an upload | Frontend → Router → `IngestionRepository.get_ingestion_attempt` → SQLite |
| `POST` | `/ingestion/attempts/{id}/duplicate-decision` | Resolve a collision | Frontend → Router → `IngestionService.apply_duplicate_decision` → Update SQLite Attempt → **Trigger Chunking/Indexing if Approved** |

---

## 3. Knowledge Base (Collections & Documents)
| Method | Endpoint | Description | Flow |
| :--- | :--- | :--- | :--- |
| `GET` | `/collections` | List collections | Frontend → Router → `Repository.list_collections` → SQLite |
| `POST` | `/collections` | Create collection | Frontend → Router → `Repository.create_collection` → SQLite |
| `GET` | `/collections/{id}` | Get collection details | Frontend → Router → `Repository.get_collection` → SQLite |
| `PATCH` | `/collections/{id}` | Update collection | Frontend → Router → `Repository.update_collection` → SQLite |
| `DELETE` | `/collections/{id}` | Delete collection | Frontend → Router → `Repository.delete_collection` → SQLite |
| `GET` | `/documents` | List docs (optionally by collection) | Frontend → Router → `Repository.list_documents` → SQLite |
| `GET` | `/documents/{id}` | Get document metadata | Frontend → Router → `Repository.get_document` → SQLite |
| `DELETE` | `/documents/{id}` | Delete document | Frontend → Router → `Repository.delete_document` (cascading cleanup of Chunks/Vectors) → SQLite + ChromaDB |
| `POST` | `/documents/{id}/move` | Change document collections | Frontend → Router → `Repository.assign_document_to_collections` → SQLite |
| `POST` | `/documents/{id}/reindex` | Refresh chunks/vectors | Frontend → Router → `IngestionService._chunk_and_index_document` (Skips extraction) → SQLite + ChromaDB |
| `POST` | `/documents/{id}/reingest` | Full re-process | Frontend → Router → `Repository.create_reingest_attempt` → **Trigger Background Task** |

---

## 4. Grounded Chat
| Method | Endpoint | Description | Flow |
| :--- | :--- | :--- | :--- |
| `POST` | `/chat/sessions` | New chat session | Frontend → Router → `ChatRepository.create_session` → SQLite |
| `GET` | `/chat/sessions` | List history | Frontend → Router → `ChatRepository.list_sessions` → SQLite |
| `GET` | `/chat/sessions/{id}` | Get session details | Frontend → Router → `ChatRepository.get_session` → SQLite |
| `GET` | `/chat/sessions/{id}/history` | Get turns for session | Frontend → Router → `ChatRepository.list_turns_by_session` + `list_citations_by_turn` → SQLite |
| `POST` | `/chat/sessions/{id}/turns` | Non-streaming query | Frontend → Router → `ChatService.process_turn` → Retrieval → Grounding → Generation → Citations → Save to DB |
| `POST` | `/chat/sessions/{id}/turns/stream` | Streaming RAG query | Frontend → Router → `StreamingOrchestrator.stream_turn` → SSE Event Stream → Parallel Retrieval & Generation → Stream Citations |
| `POST` | `/chat/turns/{id}/cancel` | Stop generation | Frontend → Router → `chat.cancellation.cancel_turn` → Signal `StreamingOrchestrator` to stop LLM call |

---

## 5. Background Workflows (Internal)
These flows are triggered by API calls but run asynchronously.

### A. Ingestion Background Processing (`process_ingestion_attempt`)
1.  **Extract:** `ExtractorDispatcher` parses file/URL.
2.  **Deduplicate:** `DuplicateDetector` checks for existing content.
3.  **Halt for Decision:** If duplicate, status moves to `AWAITING_USER_ACTION`.
4.  **Finalize:** If unique or approved, create `Document` in SQLite.
5.  **Chunk & Index:**
    *   `ChunkingService` splits text based on strategy.
    *   `IndexingService` generates embeddings via OpenAI.
    *   `ChromaVectorWriter` saves vectors to ChromaDB.
6.  **Complete:** Status moves to `COMPLETED`.

### B. Streaming RAG Flow (`stream_turn`)
1.  **Retrieve:** `AdvancedRetrievalService` performs multi-step retrieval (HyDE, Expansion, RRF).
2.  **Validate:** `GroundingService` checks if evidence is sufficient.
3.  **Stream Tokens:** LLM tokens are pushed to SSE as they arrive.
4.  **Stream Citations:** Final citation mapping is pushed after token stream completes.
5.  **Finalize:** Save turn metadata and citation records to SQLite.
