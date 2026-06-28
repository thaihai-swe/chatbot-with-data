# Tech Stack

> Pre-filled from archaeology sweep evidence (2026-06-28).

## Languages & Runtimes

| Layer | Language | Runtime |
|-------|----------|---------|
| Backend | Python 3.10+ | CPython |
| Frontend | JavaScript (not TypeScript) | Node.js (Vite dev server) |

## Frameworks & Libraries

### Backend
- **FastAPI** — async web framework (auto-docs at `/docs`, `/redoc`)
- **Weaviate 1.27.0** — vector database (Docker, hybrid search BM25 + semantic)
- **SQLite** — metadata and cache storage (16 tables)
- **OpenAI SDK** — LLM and embedding API client
- **python-dotenv** — env file loading
- **pdfplumber + PyPDF2** — PDF text extraction
- **beautifulsoup4 + requests** — web page extraction
- **httpx** — async HTTP client
- **python-multipart** — file upload handling
- **pydantic** — schema validation (via FastAPI)
- **tenacity** — retry logic
- **pytest + pytest-mock** — test framework (no tests written yet)

### Frontend
- **React 18** — UI framework
- **Vite** — build tool and dev server
- **React Router v6** — client-side routing
- **Vitest + jsdom + @testing-library/react + @testing-library/jest-dom** — test framework (no tests written yet)

## Infrastructure & Deploy

- **Docker Compose** — Weaviate 1.27.0 only (no app containers)
- **No CI pipeline** — no `.github/`, `.gitlab-ci.yml`, or similar
- **No Makefile** — manual commands

## Development Tools

- **GitNexus** — code intelligence (MCP tools, indexed 2998 symbols)
- **opencode** — primary AI agent framework
- **VS Code** — `.vscode/launch.json` with debug config for FastAPI via debugpy
- **No linters/formatters** — no ruff, black, flake8, eslint, prettier, mypy, pyright
