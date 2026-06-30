# Learned Heuristics

## Purpose

This file captures repeated, evidence-backed heuristics that improve maintenance of the project.

## Heuristics

### LH-001: Safety check must run before any query pipeline processing
- **Trigger**:
  - Adding a new query endpoint or bypassing the existing `/chat/send` router
  - Modifying `backend/chat/safety.py` or the query pipeline entry point
- **Working heuristic**:
  - Always ensure the 3-layer safety check (heuristic → fuzzy → LLM) runs before any user query reaches retrieval or generation. Never allow a code path that sends user input directly to the LLM or vector DB without passing through `safety.py`.
- **Evidence**:
  - `backend/routers/chat.py` calls `safety_service.check_query()` before any retrieval; bypassing this would expose the system to prompt injection (`brownfield-map.md` lists this as preserved behavior #1).
- **Confidence**: High
- **Last reviewed**: 2026-06-28
- **Promote to stronger rule?**: Consider — this is already a preserved behavior baseline entry.

### LH-002: Default retrieval must be hybrid search via RRF fusion
- **Trigger**:
  - Modifying `backend/chat/retrieval.py` or adding a new retrieval strategy
  - Changing the `CandidateMerger` or RRF scoring logic
- **Working heuristic**:
  - Hybrid search (BM25 + semantic vector) is the core differentiator. Single-strategy retrieval changes or removal of RRF fusion should require explicit justification in the task spec.
- **Evidence**:
  - `backend/chat/retrieval.py` uses `CandidateMerger` with RRF fusion; brownfield-map.md records this as preserved behavior #2.
- **Confidence**: High
- **Last reviewed**: 2026-06-28
- **Promote to stronger rule?**: No — descriptive heuristic, not a policy.

### LH-003: SQLite migrations are append-only — never modify past versions
- **Trigger**:
  - Adding new database tables or columns
  - Modifying `backend/migrations/` or `backend/database.py`
- **Working heuristic**:
  - The migration chain has 5 versions across 17 tables. Always add a new migration version rather than editing past ones. Backward compatibility must be maintained.
- **Evidence**:
  - `backend/migrations/runner.py` runs migrations sequentially; versions `0001` through `0005_user_annotations` exist. Brownfield-map records this as preserved behavior #3. Feature `3.0-ux-upgrade` confirmed the pattern by adding `0005_user_annotations` with idempotent `INSERT OR IGNORE` semantics following the established pattern.
- **Confidence**: High
- **Last reviewed**: 2026-06-29
- **Promote to stronger rule?**: Yes — consider promoting to a core policy if schema changes become frequent.

### LH-004: API routers have no authentication — changes must handle all 8 routers consistently
- **Trigger**:
  - Adding authentication middleware or modifying router logic
  - Reviewing security posture of the API surface
- **Working heuristic**:
  - None of the 8 routers (`health`, `chat`, `documents`, `collections`, `ingestion`, `settings`, `duplicate_decisions`, `notes`) have auth middleware. When adding auth, either apply it globally via middleware or handle all routers consistently.
- **Evidence**:
  - `brownfield-map.md` lists all 7 original routers under security-sensitive paths with risk MEDIUM due to no auth middleware. Feature `3.0-ux-upgrade` added the 8th router (`notes.py`) following the same pattern. `backend/routers/` contains 8 route modules.
- **Confidence**: High
- **Last reviewed**: 2026-06-29
- **Promote to stronger rule?**: No — once auth is added, this heuristic becomes obsolete.

### LH-005: Chunking strategy auto-selection handles most document types
- **Trigger**:
  - Adding a new document format or modifying the chunking pipeline
  - Debugging poor retrieval quality for specific document types
- **Working heuristic**:
  - The ingestion pipeline auto-selects chunking strategy by document type (PDF → page-aware, markdown → heading-aware, text → fixed-size, etc.). Manual override is available but the auto-selection handles most cases. First debug step for poor results is to check if the auto-selected strategy was appropriate.
- **Evidence**:
  - `backend/chunking/` contains 5 strategies tagged by document type; `backend/ingestion/` selects strategy automatically based on file extension and MIME type.
- **Confidence**: Medium
- **Last reviewed**: 2026-06-28
- **Promote to stronger rule?**: No

### LH-006: Harness config file required for verification scripts
- **Status**: Active  <!-- Active | Fading | Archived -->
- **Trigger**:
  - Running `scripts/harness/gate-runner.sh` or `scripts/harness/phase-gate.sh`
  - Re-initializing the project harness or starting feature verification
- **Working heuristic**:
  - The verification harness scripts expect `core-zero/project/harness-config.yaml` to exist. If it is missing (due to incomplete or partial initialization), the harness fails with `ConfigError`. Always ensure this file is created and properly defines the phases and test runner commands before running harness verifications.
- **Evidence**:
  - Running `phase-gate.sh` in feature `1.0-citation-ingest-richer` failed with `ConfigError: Config not found: core-zero/project/harness-config.yaml` until the file was manually created.
- **Recurrence count**: 1
- **Semantic links**: [harness-config.yaml](core-zero/project/harness-config.yaml)
- **Confidence**: High
- **Last reviewed**: 2026-06-28
- **Promote to stronger rule?**: No

### LH-007: SQLite migration queries on deprecated tables must check for table existence
- **Trigger**:
  - Writing database schema migrations that execute data-copy operations from legacy/deprecated tables
  - Editing migration runner logic or schema setup statements
- **Working heuristic**:
  - Always check `sqlite_master` for table existence before running data-migrations on deprecated/dropped tables. Fresh database builds that skip creating deprecated tables (since they are removed from schema definition statements) will crash during legacy migration step executions if the query is not conditional.
- **Evidence**:
  - Resolving the `no such table: chat_session_collections` crash in `reset_all_data.py` required making migration `0004` and `0006` checks conditional in [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py#L352-L380).
- **Confidence**: High
- **Last reviewed**: 2026-06-29
- **Promote to stronger rule?**: No

### LH-008: FastAPI / Uvicorn dependency caching requires backend restart
- **Trigger**:
  - Modifying backend configuration files (e.g., `settings.json`) that are used inside `@lru_cache()` dependencies (like factory providers).
  - Testing newly configured providers via the UI or API.
- **Working heuristic**:
  - FastAPI dependencies using `@lru_cache` will indefinitely cache the fallback or old configuration if the backend is already running when the configuration file is updated. Always restart the backend server explicitly to bust the cache when testing provider switches (e.g., `DummyRerankingProvider` to `FlashRankProvider`).
- **Evidence**:
  - In feature `7.0-cross-encoder-reranking`, the frontend received `0` documents because `DummyRerankingProvider` remained cached despite `settings.json` being updated to `flashrank`, requiring a manual restart to activate the cross-encoder.
- **Confidence**: High
- **Last reviewed**: 2026-06-30
- **Promote to stronger rule?**: No
