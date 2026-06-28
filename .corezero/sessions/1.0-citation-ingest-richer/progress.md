# Session Progress: 1.0-citation-ingest-richer

## Phase 1 — Gap 1 (Quote-Level Citations)

### TASK-001: Quote extraction
- Added `extract_quote()` to `CitationService` with sentence-overlap + LLM fallback
- Added `QUOTE_EXTRACTION_PROMPT` to `prompts.py`
- Updated `map_citations_to_chunks()` to accept `answer_text`/`llm_provider`
- Fixed LLM fallback logic: was gated on `best_sentence` (falsy when no overlap), now always tries LLM when provider is given
- Created `backend/tests/chat/test_citations.py` — 17 tests
- **Result:** 17/17 pass

### TASK-002: Integrate into chat paths
- `service.py`: pass `answer_text` + `llm_provider` to `map_citations_to_chunks()`, pass `quote_text` to `create_citation()`
- `streaming.py`: same integration + SSE payload includes `quote_text`
- **Result:** 17/17 pass, all compile clean

### TASK-003: CitationModal frontend
- `CitationModal.jsx`: shows `quote_text` as block quote (italic, curly quotes, accent border), collapsible "Show full context" toggle
- Falls back to full excerpt when no `quote_text`
- Added `.quote-highlight` CSS class
- **Result:** JSX syntax verified, backward compatible

## Phase 2 — Gap 2 (Document Understanding)

### TASK-004: DocumentUnderstandingService
- Created `backend/indexing/understanding.py` with `understand(text, title) -> dict`
- Added `DOCUMENT_UNDERSTANDING_PROMPT` to `prompts.py`
- Added `doc_understanding_enabled`/`doc_understanding_model` to `IngestionSettings`
- Handles JSON parsing with markdown fence stripping
- Created `backend/tests/ingestion/test_understanding.py` — 12 tests
- **Result:** 12/12 pass

### TASK-005: Integrate into ingestion pipeline
- Added `_understand_document()` to `IngestionService` with skip guards (disabled, >100K chars, LLM error)
- Called in both `process_ingestion_attempt()` and `apply_duplicate_decision()` paths
- Stores result in attempt's `metadata_json["doc_understanding"]` before `_finalize_successful_ingestion()`
- **Result:** Compiles clean, all 29 tests pass

## Phase 3 — Gap 3 (Richer Context)

### TASK-006: ContextService enrichment
- Added `get_document_batch(ids)` to `DocumentRepository`
- `_build_enriched_blocks()` builds `<document-summaries>` and `<citation-map>` from doc_understanding data
- Added `section` attribute to `<source>` tags
- Updated call sites in `service.py` and `streaming.py` to pass `collection_ids`
- Graceful skip when no understanding data exists
- **Note:** Used `DocumentRepository()` directly, consistent with existing patterns

### TASK-007: Conflict/uncertainty instructions
- Added `CONFLICT_INSTRUCTION` and `UNCERTAINTY_INSTRUCTION` constants
- Updated `BASE_GROUNDED_CHAT_SYSTEM_PROMPT` with `{conflict_instruction}` and `{uncertainty_instruction}` slots
- Updated all intent-specific prompt functions with the new slots
- ContextService includes conflict instruction only when > 1 unique document
- **Result:** All compile clean

## Summary
- **All 30 ACs covered** across 3 phases, 7 tasks
- **29 tests** (17 citation + 12 understanding) all pass
- **Files changed:** 12 files across backend and frontend

## Verification & Closeout Session (2026-06-28)
- Created the required `harness-config.yaml` to fix the `ConfigError`.
- Verified preconditions and ran the mechanical verification gates (29 tests passing).
- Documented findings in `review.md` and manual test steps in `testing-scenarios.md`.
- Transitioned active feature state to `Done` in `harness-state.json`.
- Triaged the `session-extracts.md` candidates and promoted `LH-006` for the missing config file watchout.
- Logged new patterns and anti-patterns for progress polling / UI blocking in the frontend domain memory.
- Updated `harness-config.md` and `project-knowledge-base.md` to reflect new files.
