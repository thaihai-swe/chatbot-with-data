# Project Tech Stack

<!-- LLM-friendly reference of your project's dependencies, APIs, tools, and conventions. Designed for agent consumption — agents read this to understand what's available without searching the codebase. /spec-research, /spec-plan, and /spec-implement use this for context. -->

## Languages & Runtimes

| Language | Version | Purpose | Package Manager |
| - | - | - | - |
| Python | 3.13 | Backend Application Runtime | pip (via requirements.txt, .venv) |
| JavaScript (ESM) | Node.js (Vite) | Frontend UI Development | npm (via package.json) |

## Frameworks

| Framework | Version | Purpose | Docs |
| - | - | - | - |
| FastAPI | Latest | Backend HTTP REST API and SSE Streaming | https://fastapi.tiangolo.com/ |
| React | ^18.3.1 | Frontend Single Page Application | https://react.dev/ |
| Vite | ^7.1.12 | Frontend Bundler and Dev Server | https://vite.dev/ |

## Key Dependencies

| Package | Version | Purpose | Notes |
| - | - | - | - |
| weaviate-client | v4 (latest) | Client for vector database operations | Used for document search / hybrid search |
| openai | Latest | LLM text generations & text embeddings | Targets GPT-4o / standard models |
| flashrank | Latest | Post-retrieval document reranking | Improves search precision |
| PyPDF2 / pdfplumber | Latest | Extract text content from raw PDF uploads | Used in parser utilities |
| beautifulsoup4 | Latest | Crawl & extract text from web URLs | Used for web-source ingestion |
| react-router-dom | ^6.30.1 | Frontend screen navigation | Configures App routes |
| recharts | ^3.9.1 | Visualization library | Used for performance/ablation metrics |
| vitest | ^3.2.4 | Frontend Unit testing framework | Executed via npm run test |
| pytest | Latest | Python Backend unit and integration test runner | Executed via pytest |

## Internal Libraries & Utilities

| Module | Path | Purpose | Key Exports |
| - | - | - | - |
| App configuration | `backend/config.py` | Load env vars, configuration management | `Settings` |
| Database Manager | `backend/database.py` | SQLite connection pooling & context manager | `get_connection` |
| Streaming Engine | `backend/chat/streaming.py` | SSE Event generation & prompt-to-response pipeline | `StreamingOrchestrator` |
| Document Ingestion | `backend/ingestion/service.py` | Handles uploads, duplicate checks, and indexes | `IngestionService` |
| Weaviate Vector Store | `backend/indexing/weaviate_store.py` | Weaviate connection, hybrid search, and vectors | `WeaviateVectorStore` |

## External APIs

| API | Base URL | Auth | Rate Limit | SDK |
| - | - | - | - | - |
| OpenAI API | `https://api.openai.com/v1` | Bearer Token (`OPENAI_API_KEY`) | Tier-dependent | `openai` Python SDK |

## Databases & Storage

| Store | Type | Purpose | Access Pattern |
| - | - | - | - |
| SQLite | Relational SQL | Session, History turns, Citations, Ingestion meta | Context-managed read/write connections |
| Weaviate | Vector DB | High-dimensional text chunk embedding indexing | Hybrid Search (Keyword BM25 + Semantic Vector) |

## Infrastructure & Services

| Service | Provider | Purpose | Config Location |
| - | - | - | - |
| Weaviate Vector DB | Local Docker Container | Local Vector Indexing | `docker-compose.yml` (port 8080) |

## Development Tools

| Tool | Purpose | Config File | Key Commands |
| - | - | - | - |
| Code intelligence MCP | Optional code knowledge graph | provider-specific | See `code-intelligence.md` |
| Vite Dev Server | Local frontend development | `frontend/vite.config.js` | `npm run dev` |
| Uvicorn | Python ASGI web server | CLI run | `uvicorn app:app` |

## Environment Variables

| Variable | Purpose | Required | Default |
| - | - | - | - |
| `OPENAI_API_KEY` | Authentication for OpenAI API queries | Yes | None |
| `WEAVIATE_URL` | Endpoint of Weaviate Vector Store | No | `http://localhost:8080` |
| `WEAVIATE_API_KEY` | Optional API key for remote Weaviate | No | None |
| `VITE_API_BASE_URL` | Base endpoint of FastAPI backend API | No | `http://127.0.0.1:8000` |

## Version Pinning Policy

- Production deps: Pinned exactly or compatible ranges in `package.json` / `requirements.txt`
- Dev deps: Pinned in package.json / requirements.txt
- Upgrade cadence: Manual
- Security patches: As needed

