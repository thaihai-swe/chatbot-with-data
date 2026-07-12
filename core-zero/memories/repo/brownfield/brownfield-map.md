# Brownfield Archaeology Map

## Overview
This document maps out the existing components, risk tiers, and baseline behaviors for the `chatbot-with-data` repository, conducted during the initial archaeology sweep.

## Codebase Entrypoints
- **Backend Entry**: [backend/main.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/main.py) which runs the FastAPI app exported by [backend/app.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/app.py).
- **Frontend Entry**: [frontend/index.html](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/index.html) which mounts [frontend/src/main.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/main.jsx) and renders [frontend/src/App.jsx](file:///Users/thaihai-swe/Desktop/chatbot-with-data/frontend/src/App.jsx).

## Baseline Commands
- **Backend Verification/Tests**: `PYTHONPATH=backend ./.venv/bin/pytest`
- **Frontend Build**: `npm run build` (inside `/frontend` directory)
- **Frontend Dev Server**: `npm run dev` (inside `/frontend` directory)

## High-Risk & Sensitive Paths
The following paths handle sensitive operations, external network integrations, or state persistency:

| Path | Risk Rating | Description / Sensitive Asset |
| - | - | - |
| `backend/.env` | Critical | Contains secret keys (`OPENAI_API_KEY`, etc.) |
| `backend/chat/streaming.py` | High | SSE generation, LLM connection, safety & grounding validation |
| `backend/chat/grounding.py` | High | Gating logic for hallucination & fact verification |
| `backend/ingestion/service.py` | High | Document deduplication, ingestion flow, and parsing |
| `backend/indexing/weaviate_store.py` | Medium | Weaviate Vector Store client indexing & hybrid search queries |
| `backend/database.py` | Medium | Relational SQLite database connection pooling |

## Preserved Behavior Baseline
The following behaviors must not be modified or broken by any feature delivery work:
1. **SSE Event Stream Formatting**: Streaming orchestrator (`streaming.py`) must emit structured messages matching the SSE format (`event: {event_name}\ndata: {json_payload}\n\n`).
2. **Pre-generation Safety and Grounding Gating**: Queries must be safety-checked and evidence-grounded. If validation fails, refusal reason must stream without querying the LLM.
3. **Turn Cancellation Pipeline**: Check `is_cancelled(turn_id)` at key checkpoints, closing stream and updating SQLite status to `cancelled` immediately on match.
4. **Duplicate Detection Ingestion Status**: Unique documents proceed to indexing; duplicate/modified files halt ingestion and update status to `AWAITING_USER_ACTION`.

## Profile Rules
Any feature touching a path rated `high` or `critical` MUST be promoted to `Complex` in its `status.md` file to ensure appropriate planning and safety checks are executed.
