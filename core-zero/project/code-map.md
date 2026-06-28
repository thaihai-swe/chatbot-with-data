# Code Map

> Pre-filled from archaeology sweep (2026-06-28). Refresh via `/harness-maintain`.

## Directory Structure

```
/Users/thaihai-swe/Desktop/chatbot-with-data/
├── backend/                          # FastAPI Python backend
│   ├── main.py                       # Server entry point
│   ├── app.py                        # FastAPI app factory
│   ├── config.py                     # Settings & env loading
│   ├── database.py                   # SQLite connection
│   ├── chat/                         # Core RAG pipeline (9 modules)
│   ├── chunking/                     # 5 chunking strategies
│   ├── extractors/                   # PDF/Text/Web extraction
│   ├── ingestion/                    # Doc ingestion service
│   ├── indexing/                     # Weaviate integration
│   ├── embeddings/                   # OpenAI embedding client
│   ├── providers/                    # LLM abstraction layer
│   ├── repositories/                 # SQLite data access (6 repos)
│   ├── models/                       # Data models
│   ├── schemas/                      # Pydantic schemas
│   ├── routers/                      # 7 API route modules
│   ├── migrations/                   # DB migration runner
│   ├── duplicate_detection/          # Dedup logic
│   ├── storage/                      # Local file storage
│   ├── config/                       # Runtime config files
│   └── data/                         # Runtime data (gitignored)
├── frontend/                         # React + Vite SPA
│   ├── src/
│   │   ├── screens/                  # 7 screen components
│   │   ├── components/               # 13 reusable components
│   │   ├── api/                      # 4 API client modules
│   │   └── constants/                # Status enums
│   └── vite.config.js                # Dev proxy + vitest config
├── documents/                        # Design docs (16 files)
├── scripts/                          # Utility scripts
├── core-zero/                        # Harness policy files
└── docs/                             # Generated docs
```

## Key Entry Points

| File | Purpose |
|------|---------|
| `backend/main.py` | Uvicorn entry: `uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| `backend/app.py` | `create_app()` factory: registers routers, middleware, error handlers, migrations |
| `frontend/src/main.jsx` | React DOM mount + BrowserRouter |
| `frontend/src/App.jsx` | Route definitions (7 routes) |
| `frontend/index.html` | HTML shell, loads `/src/main.jsx` via Vite |
