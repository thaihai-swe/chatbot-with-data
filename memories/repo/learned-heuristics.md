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
  - The migration chain has 4 versions across 16 tables. Always add a new migration version rather than editing past ones. Backward compatibility must be maintained.
- **Evidence**:
  - `backend/migrations/runner.py` runs migrations sequentially; `backend/migrations/versions/` contains 4 version directories. Brownfield-map records this as preserved behavior #3.
- **Confidence**: High
- **Last reviewed**: 2026-06-28
- **Promote to stronger rule?**: Yes — consider promoting to a core policy if schema changes become frequent.

### LH-004: API routers have no authentication — changes must handle all 7 routers consistently
- **Trigger**:
  - Adding authentication middleware or modifying router logic
  - Reviewing security posture of the API surface
- **Working heuristic**:
  - None of the 7 routers (`health`, `chat`, `documents`, `collections`, `ingestion`, `settings`, `duplicate_decisions`) have auth middleware. When adding auth, either apply it globally via middleware or handle all routers consistently.
- **Evidence**:
  - `brownfield-map.md` lists all 7 routers under security-sensitive paths with risk MEDIUM due to no auth middleware. `backend/routers/` contains 7 route modules.
- **Confidence**: High
- **Last reviewed**: 2026-06-28
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
