# Learned Heuristics

## Purpose
This file captures repeated, evidence-backed heuristics that improve maintenance of the project.

## Heuristics

### LH-001: Safety check must run before any query pipeline processing
- **Trigger**: New query endpoints or modifications to `backend/chat/safety.py`.
- **Working heuristic**: Always pass user input through the 3-layer check in `safety.py` before retrieval or generation.
- **Evidence**: `backend/routers/chat.py` routes through safety checks; direct LLM/DB queries are blocked.
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-002: Default retrieval must be hybrid search via RRF fusion
- **Trigger**: Modifying `backend/chat/retrieval.py` or retrieval strategy.
- **Working heuristic**: Hybrid search (BM25 + semantic vector) using CandidateMerger with RRF fusion is the core retrieval pattern.
- **Evidence**: `backend/chat/retrieval.py` uses CandidateMerger with RRF.
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-003: SQLite migrations are append-only — never modify past versions
- **Trigger**: Modifying database schemas or runner scripts in `backend/migrations/`.
- **Working heuristic**: Always append new migrations sequentially rather than editing past migrations to maintain backward compatibility.
- **Evidence**: Migration runners execute `0001` through `0005_user_annotations` sequentially.
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-004: API routers have no authentication — changes must handle all 8 routers consistently
- **Trigger**: Modifying routing middleware or security structures in `backend/routers/`.
- **Working heuristic**: All 8 route modules have no auth. When applying security controls, handle all routers consistently.
- **Evidence**: `backend/routers/` contains 8 route modules without authentication.
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-005: Chunking strategy auto-selection handles most document types
- **Trigger**: Document ingestion pipelines or poor retrieval quality.
- **Working heuristic**: Ingestion automatically maps file types to strategies (PDF → page-aware, MD → heading-aware, TXT → fixed-size). Check auto-strategy selection before debugging retrieval.
- **Evidence**: `backend/chunking/` maps 5 strategies; `backend/ingestion/` executes auto-strategy mapping.
- **Confidence**: Medium
- **Last reviewed**: 2026-07-01

### LH-006: Harness config file required for verification scripts
- **Status**: Active
- **Trigger**: Running `scripts/harness/gate-runner.sh` or `scripts/harness/phase-gate.sh`.
- **Working heuristic**: Verification scripts require `core-zero/project/harness-config.yaml` to run. Ensure this file is initialized.
- **Evidence**: Harness verifications crash with `ConfigError` if the config file is absent.
- **Recurrence count**: 1
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-007: SQLite migration queries on deprecated tables must check for table existence
- **Trigger**: Schema migrations copying data from deprecated tables.
- **Working heuristic**: Check `sqlite_master` for table existence before migrating data from dropped tables to avoid crash on fresh builds.
- **Evidence**: Handled conditional execution in `runner.py` for deprecated tables to avoid crash.
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-008: FastAPI / Uvicorn dependency caching requires backend restart
- **Trigger**: Modifying backend settings used inside `@lru_cache()` dependencies.
- **Working heuristic**: FastAPI caches factory functions. Explicitly restart the server when testing settings or provider swaps.
- **Evidence**: Settings changes in `7.0-cross-encoder-reranking` remained cached until manual server restart.
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-009: RAG Citation Verification requires Disabling Adaptive Tiering
- **Status**: Active
- **Trigger**: Testing citation parsing, rendering, or highlights with small mock files.
- **Working heuristic**: Ingestion Adaptive Tiering keeps files < 38,400 tokens as 1 chunk. Disable `adaptive_tiering_enabled` to verify multi-chunking.
- **Evidence**: Re-uploading `q3_earnings.txt` in `9.0-citation-upgrade` yielded 1 chunk until disabled.
- **Recurrence count**: 1
- **Confidence**: High
- **Last reviewed**: 2026-07-01

### LH-010: Collapsed Sidebars Vertical Toggle Labels
- **Status**: Active
- **Trigger**: Creating collapsible panels or sidebars in the workspace.
- **Working heuristic**: Collapsed toggles are narrow (e.g. 48px). Render collapsed labels vertically using CSS `writing-mode: vertical-rl`.
- **Evidence**: Collapsed panel toggle labels clipped horizontally in `9.0-citation-upgrade` until vertical writing mode was applied.
- **Recurrence count**: 1
- **Confidence**: High
- **Last reviewed**: 2026-07-01
