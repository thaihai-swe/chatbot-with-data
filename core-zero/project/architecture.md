# Architecture

> Pre-filled from archaeology sweep evidence (2026-06-28).

## System Overview

Two-tier web application: FastAPI Python backend + React SPA frontend. Weaviate vector DB runs as a separate Docker container.

```
┌─────────────┐      HTTP/SSE      ┌──────────────┐      ┌──────────┐
│  React SPA  │ ──────────────────▶│  FastAPI      │─────▶│ SQLite   │
│  (Vite dev) │◀───────────────────│  Backend      │◀─────│ (16 tbls)│
└─────────────┘                   │  (:8000)      │      └──────────┘
                                   │               │      ┌──────────┐
                                   │               │─────▶│ Weaviate │
                                   │               │      │ (:8080)  │
                                   │               │      └──────────┘
                                   │               │      ┌──────────┐
                                   │               │─────▶│ OpenAI   │
                                   │               │      │ endpoint │
                                   └──────────────┘      └──────────┘
```

## Component Boundaries

### Backend (`backend/`)
- **`app.py`** — FastAPI app factory (CORS, middleware, routers, error handlers, migrations)
- **`routers/`** — 7 route modules (health, chat, documents, collections, ingestion, settings, duplicate_decisions)
- **`chat/`** — Core RAG pipeline (safety → query intelligence → retrieval → reranking → context assembly → generation → streaming → citations → grounding)
- **`chunking/`** — 5 strategies (fixed-size, heading-aware, page-aware, semantic, parent-child)
- **`extractors/`** — Document extraction (PDF, text, web)
- **`ingestion/`** — Document ingestion orchestration + URL ingestion
- **`indexing/`** — Vector DB integration (Weaviate store, indexing service)
- **`embeddings/`** — OpenAI embedding client
- **`providers/`** — LLM/embedding provider abstraction (base, OpenAI, factory)
- **`repositories/`** — Data access layer (SQLite, 6 repositories)
- **`models/`** — Data models (chat, embedding, enums, index_entry, index_generation)
- **`schemas/`** — Pydantic request/response schemas
- **`migrations/`** — Database migration runner (4 versions, 16 tables)
- **`config/`** — Runtime config (settings.json, injection patterns, injection corpus)
- **`duplicate_detection/`** — Dedup by file hash, text hash, similarity

- **6 screens**: Chat, Collections, DocumentLibrary, DuplicateDecision, Evaluation, SettingsScreen
- **11 reusable components**: XRayPanel, UploadForm, DocumentTable, etc.
- **4 API client modules**: client.js, chat.js, knowledgeApi.js, settings.js
- Single-page app using React Router v6 for client-side routing

## Data Flow

### Ingestion Pipeline
```
Upload → Extraction (PDF/TXT/Web) → Duplicate Detection 
  → Chunking (auto-select strategy) → Embedding (cached) 
  → Indexing (Weaviate + SQLite)
```

### Query Pipeline
```
Query → Safety Check (heuristic + fuzzy + LLM) 
  → Query Intelligence (classify, expand, decompose, HyDE, synonym, dynamic route) 
  → Multi-Strategy Retrieval (BM25 + semantic + HyDE in parallel) 
  → RRF Merge → Rerank → Context Assembly 
  → Grounded Generation with Streaming → Citation Extraction 
  → Persist to SQLite
```

## Integration Points

| Integration | Type | Details |
|-------------|------|---------|
| Weaviate | Vector DB | gRPC :50051, HTTP :8080 |
| OpenAI LLM | External API | Configurable base URL, API key from env |
| OpenAI Embedding | External API | Configurable base URL, API key from env |
| Web URLs | HTTP fetch | Document ingestion from URLs |
| SQLite | File DB | `data/knowledge_ingestion/app.db` |
