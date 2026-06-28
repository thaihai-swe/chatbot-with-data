# Project Constraints

> Pre-filled from archaeology sweep evidence (2026-06-28). Sections marked `[USER REVIEW NEEDED]` need adopter input.

## Runtime Constraints

- **Python 3.10+** required (no version pin in `requirements.txt`)
- **Weaviate 1.27.0** required via Docker Compose
- **SQLite** file-based at `data/knowledge_ingestion/app.db`
- **OpenAI-compatible LLM endpoint** required (default: `http://localhost:20128/v1`)
- **OpenAI-compatible embedding endpoint** required (default: `http://localhost:20128/v1`)

## Compliance & Security

- **Hardcoded API keys in `.env` files** — committed to repo (CRITICAL, must address)
- **No authentication/authorization** on any API endpoint — open access
- **No output moderation** on generated content
- **No PII redaction** (roadmap item, not implemented)
- **No SSRF protection** on URL ingestion (`backend/extractors/web_extractor.py`)
- **Prompt injection defense** implemented (3-layer: heuristic + fuzzy + LLM)
- [USER REVIEW NEEDED] — Compliance requirements (SOC2, GDPR, etc.)
- [USER REVIEW NEEDED] — Data retention policies

## Resource Limits

[USER REVIEW NEEDED] — No evidence of resource limits in code or config.

## Deployment Constraints

- **No Dockerfiles for app containers** — only Weaviate in Docker
- **No CI/CD pipeline**
- [USER REVIEW NEEDED] — Deployment environment (cloud, self-hosted, etc.)
- [USER REVIEW NEEDED] — Expected scale (users, QPS, document volume)
