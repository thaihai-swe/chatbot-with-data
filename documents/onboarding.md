# Onboarding Guide

**Status:** 🟢 Implemented  
**Last verified:** 2026-05-29  
**Source files:** `backend/app.py`, `backend/main.py`, `docker-compose.yml`, `requirements.txt`

---

## Welcome

This guide walks you from a fresh clone to a working RAG system. Reading time: ~10 minutes. Active setup time: ~15 minutes if dependencies install cleanly.

---

## 1. Prerequisites

| Requirement | Version | Why |
|-------------|---------|-----|
| Python | 3.10+ | Backend runtime |
| Node.js | 18+ | Frontend dev server |
| Docker | 20+ | Runs Weaviate locally |
| OpenAI API key | — | LLM and embedding generation |

Verify:
```bash
python3 --version   # 3.10+
node --version      # v18+
docker --version    # 20+
```

---

## 2. Clone & Install

```bash
git clone <this-repo>
cd chatbot-with-data
```

### Backend
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
cd ..
```

---

## 3. Configuration

### Required environment variables

Create a `.env` file in the project root:

```bash
# LLM and embedding API
OPENAI_API_KEY=sk-...

# Optional overrides (defaults shown)
APP_ENV=development
APP_NAME="Knowledge Ingestion API"
DATABASE_PATH=data/knowledge_ingestion/app.db
WEAVIATE_URL=http://localhost:8080
WEAVIATE_COLLECTION_NAME=DocumentChunk
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LOG_LEVEL=INFO
```

The full list of supported variables lives in `backend/config.py` (`Settings` class). Values you don't set use sensible defaults.

### Runtime settings

Beyond `.env`, a JSON config file at `config/settings.json` holds runtime-tunable settings (chunking strategy, retrieval mode, feature toggles). It is created on first run and editable via:
- The Settings screen in the UI
- The `PUT /settings` API endpoint

See [api-flows.md](./api-flows.md#6-settings--configuration) for the schema.

---

## 4. Start the System

You'll run three things in three terminals.

### Terminal 1 — Weaviate (vector database)
```bash
docker-compose up -d
```
This starts Weaviate on `localhost:8080` (HTTP) and `localhost:50051` (gRPC). Verify:
```bash
curl http://localhost:8080/v1/meta
```
Expected: JSON with version info.

### Terminal 2 — Backend
```bash
source .venv/bin/activate
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On startup, the backend:
1. Loads settings from `.env` and `config/settings.json`
2. Auto-applies database migrations (`apply_migrations()` in `app.py:65`) — no manual step needed
3. Registers routers and middleware
4. Listens on `:8000`

Verify:
```bash
curl http://localhost:8000/health
```
Expected:
```json
{"status": "ok", "app_name": "Knowledge Ingestion API", "environment": "development"}
```

### Terminal 3 — Frontend
```bash
cd frontend
npm run dev
```
Visit `http://localhost:5173`. The Vite dev server proxies `/api/*` to `http://localhost:8000` (see `frontend/vite.config.js`).

---

## 5. End-to-End Verification

Once all three services are up, run this sanity checklist:

### Step 1 — Create a collection
UI: `Collections` screen → `New Collection` → name it `test`.

Or via API:
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "description": "Smoke test"}'
```

### Step 2 — Upload a document
UI: `Document Library` → upload any small PDF or `.txt` file → assign to `test` collection.

Or via API:
```bash
curl -X POST http://localhost:8000/ingestion/file-upload \
  -F "file=@some_doc.pdf" \
  -F "collection_ids=<collection-id-from-step-1>"
```

The response includes an `attempt_id`. Poll:
```bash
curl http://localhost:8000/ingestion/attempts/<attempt_id>
```
Wait until `status` is `completed` (typically a few seconds for a small doc).

### Step 3 — Ask a question
UI: `Chat` screen → select the `test` collection → ask a question about your document.

Or via API:
```bash
# Create a session
curl -X POST http://localhost:8000/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"collection_ids": ["<collection-id>"]}'

# Ask a question (streaming)
curl -X POST http://localhost:8000/chat/sessions/<session-id>/turns/stream \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is this document about?"}' \
  --no-buffer
```

You should see token-by-token streaming, then citations and metrics. If the question can be answered from the document, the system returns an answer with citations linking back to specific chunks.

### Step 4 — Inspect the pipeline
UI: Click the X-Ray panel on a turn to see retrieved chunks, query transformations, and grounding scores.

---

## 6. Running Tests

```bash
source .venv/bin/activate
cd backend
pytest
```

`pytest` and `pytest-mock` are in `requirements.txt`. Test files live alongside source under each subpackage. Use `pytest -k <pattern>` to run a subset.

---

## 7. Common Issues

### Weaviate connection refused
- Confirm `docker-compose ps` shows the container running.
- Check `WEAVIATE_URL` in `.env` matches the exposed port (default `8080`).
- On macOS Docker Desktop, port forwarding can take a few seconds after `up -d`.

### `OPENAI_API_KEY` missing
- The backend will start, but ingestion (embedding generation) and chat (LLM) will fail.
- Errors surface in the backend logs and as 500 responses.

### Port already in use
- Backend `:8000`: `lsof -i :8000` then kill the offending process.
- Frontend `:5173`: change in `frontend/vite.config.js` or kill the process.
- Weaviate `:8080`: stop other services or edit `docker-compose.yml`.

### Migrations not applied / DB schema errors
- The DB lives at `DATABASE_PATH` (default `data/knowledge_ingestion/app.db`).
- Migrations run on backend startup. If the DB looks corrupt, stop the backend, delete the file, restart — migrations recreate the schema.
- For schema details, see [database-schema.md](./database-schema.md).

### Frontend shows "Network Error" on every request
- Confirm backend is up: `curl http://localhost:8000/health`.
- Confirm Vite proxy is hitting the right port (`vite.config.js` → `target: "http://localhost:8000"`).
- Confirm CORS allows `http://localhost:5173` (default config does).

### Chat returns "I don't know" for questions that should be answered
- Check ingestion completed: `GET /ingestion/attempts/<id>` shows `status=completed`.
- Check chunks were created: query SQLite at `DATABASE_PATH` for `chunks WHERE document_id = ?`.
- Check Weaviate has the data: `curl http://localhost:8080/v1/objects?class=DocumentChunk&limit=5`.
- Try lowering retrieval thresholds or enabling query expansion via the Settings screen.

---

## 8. Where to Go Next

Once the smoke test passes:

| Goal | Doc |
|------|-----|
| Understand the architecture | [system-architecture.md](./system-architecture.md) |
| Browse all API endpoints | [api-flows.md](./api-flows.md) |
| Read the data model | [database-schema.md](./database-schema.md) |
| Learn how retrieval works | [RETRIEVAL_FLOW.md](./RETRIEVAL_FLOW.md) |
| Tune chunking | [CHUNKING_STRATEGIES.md](./CHUNKING_STRATEGIES.md) |
| Understand safety | [PROMPT_INJECTION_DETECTION.md](./PROMPT_INJECTION_DETECTION.md) |
| Understand RAG concepts | [ai-learning.md](./ai-learning.md) |
| See the roadmap | [enhancement-recommendations.md](./enhancement-recommendations.md) |

---

## 9. Project Layout (Cheat Sheet)

```
backend/
  app.py                # FastAPI factory, middleware, startup
  main.py               # uvicorn entry: app = create_app()
  config.py             # Settings + SettingsManager
  database.py           # SQLite connection
  routers/              # FastAPI endpoints
  chat/                 # Retrieval, generation, safety, streaming
  chunking/             # Five chunking strategies + dispatcher
  ingestion/            # Upload, URL fetch, ingestion orchestration
  indexing/             # Weaviate integration
  duplicate_detection/  # File/text/similarity duplicate checks
  embeddings/           # OpenAI embedding client
  llm/                  # LLM client
  providers/            # Provider abstraction
  repositories/         # Data access layer (SQLite)
  schemas/              # Pydantic request/response models
  models/               # Domain dataclasses
  migrations/           # Schema migrations (auto-run on startup)
  extractors/           # PDF/text/web extraction
  error_handlers/       # Global exception handlers
  storage/              # Local file storage helpers

frontend/
  src/
    screens/            # Chat, Evaluation, DocumentLibrary, Collections, Settings, ...
    components/         # XRayPanel, CitationModal, ...
    App.jsx, main.jsx
  vite.config.js        # Dev server + /api proxy
  package.json

docs/                   # You are here
config/                 # Runtime settings.json (created on first run)
data/                   # SQLite + uploads + snapshots (created on first run)
docker-compose.yml      # Weaviate
requirements.txt
README.md
```
