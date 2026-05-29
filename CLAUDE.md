# CLAUDE.md


## Project Overview

RAG knowledge-base lab: FastAPI backend + React/Vite frontend + Weaviate (hybrid vector/BM25) + SQLite (relational metadata) + OpenAI (embeddings + chat). See `README.md` and `docs/system-architecture.md` for the long-form description, and **`AGENTS.md` for operating rules** (priority rules, planning loop, verification expectations) — they apply to Claude Code sessions too.

## Common commands

Backend (run from repo root unless noted):
```bash
# one-time
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# dev server — MUST run from backend/ because imports are root-relative
# (`from config import ...`, `from routers import ...`)
cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Weaviate (required for retrieval/ingestion)
docker compose up -d weaviate
```

Frontend:
```bash
cd frontend
npm install
npm run dev      # vite dev server (proxies /api/* → http://localhost:8000, /api stripped)
npm run build
npm run test     # vitest
```

Tests:
```bash
# backend — pytest is the configured runner; there is no top-level tests/ dir today,
# so target specific files/dirs. Run from backend/ for import resolution.
cd backend && pytest path/to/test_x.py -v
cd backend && pytest path/to/test_x.py::test_name -v

# frontend
cd frontend && npm run test
```

## Architecture

### Backend layout (`backend/`)
- **Entry**: `main.py` re-exports `app` from `app.py`. `create_app()` wires CORS, an `X-Request-ID` middleware, all routers, error handlers, and runs `migrations.apply_migrations()` on startup.
- **Routers** (`routers/`) each mount their own prefix — there is **no global `/api` prefix on the backend**; the frontend's vite proxy adds `/api` and strips it on the way through:
  - `/chat`, `/collections`, `/documents`, `/ingestion`, `/ingestion/attempts` (duplicate decisions), `/settings`, `/health`.
- **Config** (`config.py`) is two-layered:
  1. `Settings` — env-driven (loaded via `python-dotenv`), holds paths, CORS origins, OpenAI/Weaviate credentials. Created at import time.
  2. `GlobalSettings` (`schemas/settings.py`) — hierarchical runtime config persisted to `config/settings.json`, mutated through `SettingsManager.update()` (atomic write via `.tmp` + `shutil.move`). `save_run_snapshot()` writes per-run snapshots into `data/knowledge_ingestion/runs/`.
  3. Use `get_settings()` for the legacy/env layer, `get_config()` for hierarchical settings, `get_settings_manager()` when you need to mutate or snapshot.
- **Persistence**:
  - SQLite: schema is defined inline in `migrations/runner.py` (`SCHEMA_STATEMENTS`); applied idempotently at app startup. Repositories in `repositories/` (chat, chunk, embedding, index_entry, index_generation) own all DB access.
  - Weaviate: `indexing/weaviate_store.py` is the gateway for vector + BM25 hybrid search; `indexing/indexing_service.py` orchestrates upsert/delete.
  - Embedding cache lives in SQLite (avoid redundant OpenAI calls).
- **Ingestion pipeline** (`ingestion/` → `extractors/` → `chunking/` → `duplicate_detection/` → `indexing/`):
  - Extractors dispatch by content type (`pdf_extractor`, `text_extractor`, `web_extractor`) via `extractors/dispatcher.py`.
  - Chunkers are pluggable strategies (`fixed_size`, `heading_aware`, `page_aware`, `parent_child`, `semantic`) selected by `chunking/dispatcher.py`.
  - Duplicate detection (`duplicate_detection/detector.py` + `heuristics.py`) gates whether chunks proceed; user decisions resolve via the duplicate-decisions router.
- **Chat pipeline** (`chat/`) — orchestrated by `chat/service.py`. Each step is its own service injected through FastAPI `Depends`:
  - `safety` (prompt-injection / PII / moderation) → `collection_routing` → `retrieval` (SIMPLE / EXPAND / MULTIHOP / AUTO modes; uses `multi_hop` for follow-up hops) → `context` (window assembly) → `generation` (LLM call) → `grounding` (claim verification) → `citations` (stitching) → `streaming` (token streaming + cancellation via `cancellation.py`).
  - Prompts live in `chat/prompts.py`. Evaluation harness in `chat/evaluation.py`.
- **LLM/embeddings**:
  - `providers/` defines a provider abstraction (`base.py`, `factory.py`, `openai.py`).
  - `llm/client.py` is the chat-completion client; `embeddings/openai_client.py` is the embedding client. Both honor `OPENAI_API_KEY`/`OPENAI_API_BASE` (and `EMBEDDING_*` overrides) from env.

### Frontend layout (`frontend/src/`)
- React 18 + react-router-dom, Vite, Vitest. Source split into `screens/`, `components/`, `api/`, `constants/`, `styles.css`.
- Always call the backend through the `/api` prefix in code — the dev proxy in `vite.config.js` rewrites it to `http://localhost:8000`.

### Cross-cutting conventions
- Backend imports are **root-relative to `backend/`** (`from config import …`, `from routers.chat import …`). Don't add `backend.` prefixes; run tools/uvicorn from `backend/`.
- Errors flow through `error_handlers/` — register new exceptions there rather than catching ad-hoc in routers.
- New persistent state: add a CREATE TABLE statement to `migrations/runner.py::SCHEMA_STATEMENTS`; it is run idempotently at startup. There is no Alembic.
- New chat-pipeline behavior: prefer extending an existing service in `chat/` and exposing it via `Depends`-style getter, matching the pattern in `chat/service.py`.
- Settings changes that should be runtime-tunable belong in `schemas/settings.py` (`GlobalSettings`), not the env-only `Settings` dataclass.

## Docs index (use these before reading source for context)
- `docs/system-architecture.md` — components + mermaid diagrams
- `docs/api-flows.md` — endpoint-by-endpoint request/response shapes
- `docs/database-schema.md` — SQLite tables and access patterns
- `docs/RETRIEVAL_FLOW.md`, `docs/CHUNKING_STRATEGIES.md` — pipeline deep-dives
- `docs/PROMPT_INJECTION_DETECTION.md`, `docs/PII_DETECTION_TUNING.md` — safety subsystems

## Gotchas
- Running `uvicorn` from the repo root will fail on imports — must `cd backend` first.
- Weaviate must be reachable at `WEAVIATE_URL` (default `http://localhost:8080`) before chat or ingestion calls succeed; bring it up via `docker compose up -d weaviate`.
- The `.env` file is required in the repo root for OpenAI keys; `python-dotenv` is loaded at `config.py` import time, so processes started before `.env` exists won't see the keys.
- `config/settings.json` is the source of truth for runtime-tunable settings and is mutated by the `/settings` API — don't hand-edit while the server is running, or use `SettingsManager.update()` to keep the in-memory copy in sync.
- The README and onboarding doc reference a `backend/tests/` directory and `backend/data/rag_lab.db`; the actual checked-in DB is `backend/chatbot.db` and there is no top-level test suite yet — verify before relying on either.
