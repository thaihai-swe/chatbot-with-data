# API Flows & Endpoint Reference

**Status:** 🟢 Implemented  
**Last verified:** 2026-06-30  
**Source files:** `backend/routers/`, `backend/schemas/`, `backend/app.py`

---

## Overview

The RAG Knowledge Base Lab exposes a REST API via FastAPI. All endpoints return JSON. Async operations (ingestion, re-ingestion) return immediately with a job ID; use polling to check status.

**Base URL:** `http://localhost:8000`  
**Frontend proxy:** `http://localhost:5173/api` → `http://localhost:8000`

---

## 1. Health & Status

### GET /health
Check API availability.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

**Use case:** Verify backend is running before making other requests.

---

## 2. Ingestion & Document Management

### POST /ingestion/file-upload
Upload a document file (PDF, TXT, MD).

**Request:**
```bash
curl -X POST http://localhost:8000/ingestion/file-upload \
  -F "file=@document.pdf" \
  -F "collection_ids=my-collection,another-collection"
```

**Response (202 Accepted):**
```json
{
  "id": "attempt-uuid",
  "document_id": null,
  "source_type": "pdf",
  "status": "pending",
  "submitted_filename": "document.pdf",
  "mime_type": "application/pdf",
  "file_hash": "abc123...",
  "duplicate_status": null,
  "error_message": null,
  "collection_ids": ["my-collection", "another-collection"],
  "created_at": "2026-05-29T06:41:55Z",
  "updated_at": "2026-05-29T06:41:55Z",
  "completed_at": null
}
```

**Status codes:**
- `202 Accepted` — Ingestion queued (async)
- `400 Bad Request` — Invalid file type or size
- `413 Payload Too Large` — File exceeds max size (default 50 MB)

**Internal flow:**
1. Validate file type and size
2. Create `ingestion_attempt` record (status: pending)
3. Queue `process_ingestion_attempt()` in background
4. Return attempt ID immediately
5. Background: extract → duplicate check → chunk → embed → index

**Polling for completion:**
```bash
curl http://localhost:8000/ingestion/attempts/{attempt_id}
```

---

### POST /ingestion/url
Ingest a document from a URL.

**Request:**
```bash
curl -X POST http://localhost:8000/ingestion/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/document.pdf",
    "collection_ids": ["web-docs"]
  }'
```

**Response (202 Accepted):**
Same as file-upload.

**Status codes:**
- `202 Accepted` — Ingestion queued
- `400 Bad Request` — Invalid URL or timeout
- `422 Unprocessable Entity` — URL fetch failed

---

### GET /ingestion/attempts
List all ingestion attempts (optionally filtered by status).

**Request:**
```bash
curl "http://localhost:8000/ingestion/attempts?status=completed"
```

**Query parameters:**
- `status` (optional) — Filter by status: `pending`, `completed`, `error`, `duplicate_detected`

**Response (200 OK):**
```json
[
  {
    "id": "attempt-uuid",
    "document_id": "doc-uuid",
    "status": "completed",
    "duplicate_status": null,
    ...
  },
  ...
]
```

---

### GET /ingestion/attempts/{attempt_id}
Get details of a specific ingestion attempt.

**Request:**
```bash
curl http://localhost:8000/ingestion/attempts/attempt-uuid
```

**Response (200 OK):**
```json
{
  "id": "attempt-uuid",
  "document_id": "doc-uuid",
  "source_type": "pdf",
  "status": "completed",
  "duplicate_status": null,
  "error_message": null,
  "created_at": "2026-05-29T06:41:55Z",
  "completed_at": "2026-05-29T06:42:10Z"
}
```

**Status codes:**
- `200 OK` — Attempt found
- `404 Not Found` — Attempt does not exist

---

### POST /ingestion/attempts/{attempt_id}/duplicate-decision
Decide what to do with a duplicate document.

**Request:**
```bash
curl -X POST http://localhost:8000/ingestion/attempts/attempt-uuid/duplicate-decision \
  -H "Content-Type: application/json" \
  -d '{"action": "skip"}'
```

**Body:**
```json
{
  "action": "skip" | "replace" | "variant" | "merge"
}
```

**Response (200 OK):**
```json
{
  "id": "decision-uuid",
  "action": "skip",
  "final_status": "skipped",
  "created_at": "2026-05-29T06:42:15Z"
}
```

**Actions:**
- `skip` — Don't index this document
- `replace` — Replace the existing document with this one
- `variant` — Index as a variant (new document, linked to original)
- `merge` — Merge metadata with existing document

---

### GET /documents
List all documents.

**Request:**
```bash
curl http://localhost:8000/documents
```

**Query parameters:**
- `collection_id` (optional) — Filter by collection
- `source_type` (optional) — Filter by source type (pdf, txt, md, web)

**Response (200 OK):**
```json
[
  {
    "id": "doc-uuid",
    "title": "My Document",
    "source_type": "pdf",
    "source_uri": "file:///path/to/doc.pdf",
    "filename": "doc.pdf",
    "created_at": "2026-05-29T06:41:55Z",
    "updated_at": "2026-05-29T06:41:55Z",
    "collections": [
      {"id": "coll-uuid", "name": "my-collection"}
    ]
  },
  ...
]
```

---

### GET /documents/{document_id}
Get full details of a document.

**Request:**
```bash
curl http://localhost:8000/documents/doc-uuid
```

**Response (200 OK):**
```json
{
  "id": "doc-uuid",
  "title": "My Document",
  "source_type": "pdf",
  "extracted_text": "Full text of document...",
  "file_hash": "abc123...",
  "normalized_text_hash": "def456...",
  "collections": [...],
  "latest_attempt": {
    "id": "attempt-uuid",
    "status": "completed",
    ...
  }
}
```

---

### DELETE /documents/{document_id}
Delete a document and all associated chunks, embeddings, and citations.

**Request:**
```bash
curl -X DELETE http://localhost:8000/documents/doc-uuid
```

**Response (204 No Content):**
No body.

**Internal flow:**
1. Soft-delete document (set `deleted_at`)
2. Cascade delete chunks, embeddings, citations
3. Remove from Weaviate index

---

### POST /documents/{document_id}/move
Move a document to different collections.

**Request:**
```bash
curl -X POST http://localhost:8000/documents/doc-uuid/move \
  -H "Content-Type: application/json" \
  -d '{"collection_ids": ["new-collection", "another"]}'
```

**Response (200 OK):**
```json
{
  "id": "doc-uuid",
  "collections": [
    {"id": "coll-uuid", "name": "new-collection"},
    {"id": "coll-uuid2", "name": "another"}
  ]
}
```

---

### POST /documents/{document_id}/reindex
Reindex a document with current settings (e.g., after changing chunking strategy).

**Request:**
```bash
curl -X POST http://localhost:8000/documents/doc-uuid/reindex
```

**Response (200 OK):**
```json
{
  "document_id": "doc-uuid",
  "status": "completed",
  "message": "Document re-indexed successfully."
}
```

**Internal flow:**
1. Save existing chunks (atomic restore on failure)
2. Delete old chunks and Weaviate vectors
3. Re-run chunk-and-index pipeline with current strategy and settings (including adaptive tiering)
4. If failure: restore saved chunks from step 1
5. Return success

---

### POST /documents/{document_id}/reingest
Re-ingest a document (e.g., after updating source URL).

**Request:**
```bash
curl -X POST http://localhost:8000/documents/doc-uuid/reingest \
  -H "Content-Type: application/json" \
  -d '{"collection_ids": ["my-collection"]}'
```

**Response (202 Accepted):**
```json
{
  "id": "new-attempt-uuid",
  "status": "pending"
}
```

---

## 3. Collections

### GET /collections
List all collections.

**Request:**
```bash
curl http://localhost:8000/collections
```

**Response (200 OK):**
```json
[
  {
    "id": "coll-uuid",
    "name": "my-collection",
    "description": "Documents about X",
    "is_default": false,
    "routing_enabled": false,
    "document_count": 5,
    "created_at": "2026-05-29T06:41:55Z"
  },
  ...
]
```

---

### POST /collections
Create a new collection.

**Request:**
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-collection",
    "description": "Documents about X",
    "is_default": false,
    "routing_enabled": false
  }'
```

**Response (201 Created):**
```json
{
  "id": "coll-uuid",
  "name": "my-collection",
  "description": "Documents about X",
  "is_default": false,
  "routing_enabled": false,
  "document_count": 0,
  "created_at": "2026-05-29T06:41:55Z"
}
```

---

### GET /collections/{collection_id}
Get collection details.

**Request:**
```bash
curl http://localhost:8000/collections/coll-uuid
```

**Response (200 OK):**
Same as POST response.

---

### PATCH /collections/{collection_id}
Update collection metadata.

**Request:**
```bash
curl -X PATCH http://localhost:8000/collections/coll-uuid \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'
```

**Response (200 OK):**
Updated collection object.

---

### DELETE /collections/{collection_id}
Delete a collection (documents remain, but collection association is removed).

**Request:**
```bash
curl -X DELETE http://localhost:8000/collections/coll-uuid
```

**Response (204 No Content):**
No body.

---

## 4. Chat & Retrieval

### POST /chat/sessions
Create a new chat session.

**Request:**
```bash
curl -X POST http://localhost:8000/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "collection_ids": ["my-collection"],
    "metadata": {"user_id": "user123", "topic": "RAG"}
  }'
```

**Response (201 Created):**
```json
{
  "id": "session-uuid",
  "collection_ids": ["my-collection"],
  "metadata_json": "{\"user_id\": \"user123\", \"topic\": \"RAG\"}",
  "created_at": "2026-05-29T06:41:55Z",
  "updated_at": "2026-05-29T06:41:55Z"
}
```

---

### GET /chat/sessions
List all chat sessions.

**Request:**
```bash
curl http://localhost:8000/chat/sessions
```

**Response (200 OK):**
```json
[
  {
    "id": "session-uuid",
    "collection_ids": ["my-collection"],
    "created_at": "2026-05-29T06:41:55Z"
  },
  ...
]
```

---

### GET /chat/sessions/{session_id}
Get session details.

**Request:**
```bash
curl http://localhost:8000/chat/sessions/session-uuid
```

**Response (200 OK):**
Session object.

---

### DELETE /chat/sessions/{session_id}
Delete a session and all associated turns.

**Request:**
```bash
curl -X DELETE http://localhost:8000/chat/sessions/session-uuid
```

**Response (204 No Content):**
No body.

---

### GET /chat/sessions/{session_id}/history
Get chat history for a session.

**Request:**
```bash
curl http://localhost:8000/chat/sessions/session-uuid/history
```

**Response (200 OK):**
```json
[
  {
    "id": "turn-uuid",
    "session_id": "session-uuid",
    "query_text": "What is RAG?",
    "answer_text": "RAG is...",
    "status": "completed",
    "groundedness_score": 0.92,
    "created_at": "2026-05-29T06:41:55Z",
    "citations": [
      {
        "id": "citation-uuid",
        "chunk_id": "chunk-uuid",
        "document_id": "doc-uuid",
        "quote_text": "RAG is a technique..."
      }
    ]
  },
  ...
]
```

---

### POST /chat/sessions/{session_id}/turns
Create a chat turn (non-streaming).

**Request:**
```bash
curl -X POST http://localhost:8000/chat/sessions/session-uuid/turns \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is RAG?"}'
```

**Response (201 Created):**
```json
{
  "id": "turn-uuid",
  "session_id": "session-uuid",
  "query_text": "What is RAG?",
  "answer_text": "RAG is a technique that combines retrieval and generation...",
  "status": "completed",
  "safety_status": "pass",
  "safety_risk_score": 0.1,
  "groundedness_score": 0.92,
  "citations": [...],
  "retrieval_trace": {
    "original_query": "What is RAG?",
    "classification": "factual",
    "transformations": {...},
    "routing": {...},
    "execution_time_ms": {"retrieval": 250, "generation": 1200}
  },
  "safety_trace": {
    "injection_risk": "low",
    "matched_patterns": []
  },
  "created_at": "2026-05-29T06:41:55Z"
}
```

**Internal flow:**
1. Safety check (heuristic + fuzzy + LLM injection detection)
2. Query intelligence (classify, rewrite, expand, decompose, HyDE, etc.)
3. Multi-strategy retrieval (BM25 + semantic + HyDE in parallel)
4. RRF merge results
5. Rerank (currently dummy)
6. Assemble context (retrieved chunks + chat history)
7. Stream LLM response
8. Extract citations
9. Calculate groundedness score
10. Store turn, citations, metrics

---

### POST /chat/sessions/{session_id}/turns/stream
Create a chat turn with streaming response (Server-Sent Events).

**Request:**
```bash
curl -X POST http://localhost:8000/chat/sessions/session-uuid/turns/stream \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is RAG?"}' \
  --no-buffer
```

**Response (200 OK, streaming):**
```
event: start
data: {"turn_id": "turn-uuid", "query_text": "What is RAG?"}

event: token
data: {"token": "RAG"}

event: token
data: {"token": " is"}

event: token
data: {"token": " a"}

...

event: citations
data: {"citations": [{"chunk_id": "...", "document_id": "...", "quote_text": "..."}]}

event: metrics
data: {"groundedness_score": 0.92, "safety_status": "pass"}

event: end
data: {"turn_id": "turn-uuid", "status": "completed"}
```

**Events:**
- `start` — Turn created, streaming begins
- `token` — LLM token (streamed)
- `citations` — Final citations
- `metrics` — Quality metrics
- `end` — Streaming complete

**Cancellation:**
Send `POST /chat/turns/{turn_id}/cancel` to stop streaming.

---

### POST /chat/turns/{turn_id}/cancel
Cancel a streaming turn.

**Request:**
```bash
curl -X POST http://localhost:8000/chat/turns/turn-uuid/cancel
```

**Response (200 OK):**
```json
{
  "turn_id": "turn-uuid",
  "status": "cancelled"
}
```

---

## 5. Evaluation

### POST /chat/evaluate/sanity-check
Run evaluation on the golden test dataset.

**Request:**
```bash
curl -X POST http://localhost:8000/chat/evaluate/sanity-check
```

**Response (200 OK):**
```json
{
  "timestamp": "2026-05-29T06:41:55Z",
  "total_cases": 20,
  "passed_cases": 18,
  "overall_recall": 0.89,
  "overall_groundedness": 0.91,
  "results": [
    {
      "case_id": "case-1",
      "question": "What is RAG?",
      "expected_document_id": "doc-uuid",
      "actual_answer": "RAG is...",
      "recall_status": true,
      "groundedness_score": 0.95,
      "latency_ms": 1450,
      "passed": true
    },
    ...
  ]
}
```

**Metrics:**
- `recall_status` — Did retrieval find the expected document?
- `groundedness_score` — Is the answer grounded in retrieved context?
- `passed` — Both recall and groundedness passed?

---

## 6. Settings & Configuration

### GET /settings
Get all system settings.

**Request:**
```bash
curl http://localhost:8000/settings
```

**Response (200 OK):**
```json
{
  "ingestion": {
    "allowed_file_types": ["pdf", "txt", "md"],
    "max_file_size_mb": 50,
    "chunking_strategy": "fixed_size",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "embedding_model": "text-embedding-3-small",
    "adaptive_tiering_enabled": true,
    "adaptive_tiering_threshold": null,
    "adaptive_tiering_ratio": 0.3
  },
  "retrieval": {
    "retrieval_mode": "hybrid",
    "top_k": 5,
    "hybrid_weight": 0.5,
    "query_expansion_enabled": true,
    "query_decomposition_enabled": false,
    "hyde_enabled": false,
    "reranker_enabled": false
  },
  "llm": {
    "model": "gpt-4o",
    "temperature": 0.0,
    "max_tokens": 1000,
    "streaming_enabled": true
  },
  "safety": {
    "prompt_injection_detection_enabled": true,
    "safety_mode": "moderate",
    "injection_risk_threshold": 0.7
  }
}
```

---

### PUT /settings
Update system settings.

**Request:**
```bash
curl -X PUT http://localhost:8000/settings \
  -H "Content-Type: application/json" \
  -d '{
    "retrieval": {
      "query_expansion_enabled": true,
      "top_k": 10
    }
  }'
```

**Response (200 OK):**
Updated settings object.

**Note:** Settings are persisted to `config/settings.json` and applied immediately.

---

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `202` | Accepted (async operation queued) |
| `204` | No Content (success, no body) |
| `400` | Bad Request (invalid input) |
| `404` | Not Found |
| `413` | Payload Too Large |
| `422` | Unprocessable Entity (validation error) |
| `500` | Internal Server Error |

**Error response format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Request ID Tracking

Every request receives a unique `X-Request-ID` header for tracing:

**Request:**
```bash
curl -H "X-Request-ID: my-trace-id" http://localhost:8000/health
```

**Response:**
```
X-Request-ID: my-trace-id
```

If not provided, a UUID is generated automatically.

---

## CORS

Frontend at `http://localhost:5173` is allowed to make requests. Configure via `CORS_ORIGINS` env var.

---

## Cross-References

- **System Architecture:** [`docs/system-architecture.md`](./system-architecture.md)
- **Database Schema:** [`docs/database-schema.md`](./database-schema.md)
- **Retrieval Deep Dive:** [`docs/RETRIEVAL_FLOW.md`](./RETRIEVAL_FLOW.md)
