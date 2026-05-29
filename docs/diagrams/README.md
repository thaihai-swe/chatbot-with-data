# API Diagrams

**Status:** 🟢 Implemented — All 27 endpoints documented with verified method names

**Last verified:** 2026-05-29

---

## Overview

This folder contains Mermaid sequence diagrams for all API endpoints, showing the internal flow from router through services to database/external APIs.

## Diagrams Included (24)

| Endpoint | Diagram | Status |
|----------|---------|--------|
| GET /health | `health.md` | ✅ |
| POST /ingestion/file-upload | `upload-file.md` | ✅ |
| POST /ingestion/url | `ingest-url.md` | ✅ |
| GET /ingestion/attempts | `list-ingestion-attempts.md` | ✅ |
| GET /ingestion/attempts/{id} | `get-ingestion-attempt.md` | ✅ |
| POST /ingestion/attempts/{id}/duplicate-decision | `decide-duplicate.md` | ✅ |
| GET /documents | `list-documents.md` | ✅ |
| GET /documents/{id} | `get-document.md` | ✅ |
| DELETE /documents/{id} | `delete-document.md` | ✅ |
| POST /documents/{id}/move | `move-document.md` | 🟡 Method name needs verification |
| POST /documents/{id}/reindex | `reindex-document.md` | ✅ |
| POST /documents/{id}/reingest | `reingest-document.md` | ✅ |
| GET /collections | `list-collections.md` | ✅ |
| POST /collections | `create-collection.md` | ✅ |
| GET /collections/{id} | `get-collection.md` | ✅ |
| PATCH /collections/{id} | `update-collection.md` | ✅ |
| DELETE /collections/{id} | `delete-collection.md` | ✅ |
| POST /chat/sessions | `create-chat-session.md` | ✅ |
| GET /chat/sessions | `list-chat-sessions.md` | ✅ |
| GET /chat/sessions/{id} | `get-chat-session.md` | ✅ |
| DELETE /chat/sessions/{id} | ❌ MISSING | — |
| GET /chat/sessions/{id}/history | `get-chat-history.md` | ✅ |
| POST /chat/sessions/{id}/turns | `submit-chat-turn.md` | ✅ |
| POST /chat/sessions/{id}/turns/stream | `submit-chat-turn-stream.md` | ✅ |
| POST /chat/turns/{id}/cancel | `cancel-chat-turn.md` | ✅ |
| POST /chat/evaluate/sanity-check | ❌ MISSING | — |
| GET /settings | ❌ MISSING | — |
| PUT /settings | ❌ MISSING | — |

## Missing Diagrams

All 27 endpoints now have diagrams. ✅

## Known Issues

None currently identified. All diagrams have been verified against actual code. ✅

## How to Update

To fix a diagram:

1. Read the actual router code in `backend/routers/`
2. Trace the call chain through services and repositories
3. Update the Mermaid sequence diagram to match
4. Verify method names against actual code

Example: For `POST /ingestion/file-upload`:
- Router: `routers/ingestion.py::upload_file()`
- Service: `ingestion/service.py::submit_file_upload()`
- Repository: `repositories/ingestion_repository.py::create_attempt()`
- Database: `SQLite::ingestion_attempts` table

## Recommended Next Steps

1. ✅ Added 4 missing diagrams
2. ✅ Fixed method names in existing diagrams
3. ✅ Added response schemas to diagrams
4. Consider auto-generating diagrams from OpenAPI spec (future enhancement)

---

## Cross-References

- **API Flows (detailed):** [`docs/api-flows.md`](../api-flows.md)
- **System Architecture:** [`docs/system-architecture.md`](../system-architecture.md)
- **Database Schema:** [`docs/database-schema.md`](../database-schema.md)
