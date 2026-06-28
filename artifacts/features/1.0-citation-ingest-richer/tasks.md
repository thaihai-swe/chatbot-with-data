# Tasks: Citation, Document Understanding, and Richer Context

## Phase 1 — Gap 1: Quote-Level Citations

### TASK-001: Add quote extraction to CitationService

**Target:** `backend/chat/citations.py`, `backend/chat/prompts.py`, `backend/tests/chat/test_citations.py`

**Status:** Done

**Validation:** 17/17 tests passed

**Description:**
- Add `extract_quote(chunk_text, answer_text, label, llm_provider=None) -> str` method to `CitationService`
- Sentence splitting via regex `(?<=[.!?])\s+`
- Jaccard word-overlap matching with threshold 0.5
- LLM fallback with `QUOTE_EXTRACTION_PROMPT`
- Update `map_citations_to_chunks()` to accept `answer_text` and `llm_provider`, populate `quote_text`
- Create test file with unit tests

**Covers:** AC-1.1, AC-1.2, AC-1.3, AC-1.4

**Proof:** `PYTHONPATH=backend python3 -m pytest backend/tests/chat/test_citations.py -v`

**Heuristic references:** LH-003 (no migration needed — column exists)

---

### TASK-002: Integrate quote extraction into chat paths

**Target:** `backend/chat/service.py`, `backend/chat/streaming.py`

**Status:** Done

**Validation:** 17/17 tests passed, both files compile clean

**Description:**
- In `chat/service.py:process_turn`, pass `answer_text` and `llm_provider` to `map_citations_to_chunks()`
- Pass `quote_text=cit_data.get('quote_text')` to `create_citation()`
- In `chat/streaming.py:stream_turn`, same integration
- Include `quote_text` in citation objects sent via SSE

**Covers:** AC-1.5, AC-1.6

**Proof:** `PYTHONPATH=backend python3 -m pytest backend/tests/chat/test_citations.py -v`

**Depends on:** TASK-001

---

### TASK-003: Update CitationModal for quote display

**Target:** `frontend/src/components/CitationModal.jsx`, `frontend/src/styles.css`

**Status:** Done

**Validation:** JSX syntax verified

**Description:**
- If `quote_text` is non-null: display as primary content with `.quote-highlight` class (italic, accent border, curly-quoted)
- Add collapsed "Show full context" toggle revealing `chunk.text` (uses `useState`)
- If `quote_text` is null: display full chunk text as before
- Add CSS class `quote-highlight` with border-radius
- Backward compatible: old citations without `quote_text` display unchanged

**Covers:** AC-1.7, AC-1.8, AC-1.9, AC-1.10

**Proof:** Visual inspection in browser; verify backward compatibility with existing citation data

**Depends on:** TASK-001, TASK-002

---

## Phase 2 — Gap 2: Document Understanding Pipeline

### TASK-004: Create DocumentUnderstandingService

**Target:** `backend/indexing/understanding.py` (new file), `backend/chat/prompts.py`, `backend/schemas/settings.py`

**Status:** Done

**Validation:** 12/12 tests passed

**Description:**
- Create `DocumentUnderstandingService` class with `understand(text, title) -> dict` method
- Add `DOCUMENT_UNDERSTANDING_PROMPT` in `chat/prompts.py`
- Parse LLM JSON response into `{summary, topics, sections}`
- Add `doc_understanding_enabled: bool = True` and `doc_understanding_model: Optional[str] = None` to `IngestionSettings` in `schemas/settings.py`

**Covers:** AC-2.1, AC-2.2, AC-2.8

**Proof:** `PYTHONPATH=backend python3 -m pytest backend/tests/ingestion/test_understanding.py -v`

---

### TASK-005: Integrate understanding step into ingestion pipeline

**Target:** `backend/ingestion/service.py`

**Status:** Done

**Validation:** Compiles clean, all 29 tests pass

**Description:**
- Insert `_understand_document()` call between extraction and `_finalize_successful_ingestion()`
- Also called in `apply_duplicate_decision()` before `_finalize_successful_ingestion()`
- Skip if text > 100K chars (log warning)
- Skip if `doc_understanding_enabled` is false (from `schemas/settings.py`)
- Skip on LLM error (non-fatal, log warning)
- Store result in attempt's `metadata_json["doc_understanding"]`
- Document created by `_finalize_successful_ingestion()` picks up the enriched metadata

**Covers:** AC-2.3, AC-2.4, AC-2.5, AC-2.6, AC-2.7, AC-2.9, AC-2.10

**Proof:** `PYTHONPATH=backend python3 -m pytest backend/tests/ingestion/test_understanding.py -v`

**Depends on:** TASK-004

---

## Phase 3 — Gap 3: Richer Context Engineering

### TASK-006: Enrich ContextService with summaries, section paths, and citation map

**Target:** `backend/chat/context.py`, `backend/repositories/document_repository.py`

**Status:** Done

**Validation:** Compiles clean, all 29 tests pass

**Description:**
- Add `get_document_batch(ids)` to `DocumentRepository`
- Update `ContextService.assemble_context()` to accept `collection_ids`
- Build `<document-summaries>` block from doc_understanding data
- Add `section` attribute to each `<source>` tag from chunk metadata
- Build `<citation-map>` block from chunk-document mapping
- Inject enriched blocks before the raw context string
- Gracefully skip all new blocks when no doc_understanding data exists
- Updated callers: `service.py`, `streaming.py`

**Covers:** AC-3.1, AC-3.2, AC-3.3, AC-3.4, AC-3.5, AC-3.10, AC-3.8

**Proof:** `PYTHONPATH=backend python3 -m pytest backend/tests/ingestion/test_understanding.py backend/tests/chat/test_citations.py -v`

**Depends on:** TASK-004, TASK-005

---

### TASK-007: Add conflict and uncertainty instructions to system prompt

**Target:** `backend/chat/prompts.py`, `backend/chat/context.py`

**Status:** Done

**Validation:** Compiles clean, all 29 tests pass

**Description:**
- Add `CONFLICT_INSTRUCTION` and `UNCERTAINTY_INSTRUCTION` constants
- Update `BASE_GROUNDED_CHAT_SYSTEM_PROMPT` with `{conflict_instruction}` and `{uncertainty_instruction}` format slots
- Update `get_grounded_system_prompt()` signature with optional params
- Update all intent-specific prompt functions (factual, comparison, etc.) to pass the new slots as empty
- In `ContextService`, count unique document IDs, include conflict instruction only when > 1 unique document
- Always include uncertainty instruction

**Covers:** AC-3.6, AC-3.7, AC-3.9

**Proof:** `PYTHONPATH=backend python3 -m pytest backend/tests/ingestion/test_understanding.py backend/tests/chat/test_citations.py -v`

**Depends on:** TASK-006

---

## Traceability Matrix

| AC | Task | Phase |
|----|------|-------|
| AC-1.1 | TASK-001 | P1 |
| AC-1.2 | TASK-001 | P1 |
| AC-1.3 | TASK-001 | P1 |
| AC-1.4 | TASK-001 | P1 |
| AC-1.5 | TASK-002 | P1 |
| AC-1.6 | TASK-002 | P1 |
| AC-1.7 | TASK-003 | P1 |
| AC-1.8 | TASK-003 | P1 |
| AC-1.9 | TASK-003 | P1 |
| AC-1.10 | TASK-003 | P1 |
| AC-2.1 | TASK-004 | P2 |
| AC-2.2 | TASK-004 | P2 |
| AC-2.3 | TASK-005 | P2 |
| AC-2.4 | TASK-005 | P2 |
| AC-2.5 | TASK-005 | P2 |
| AC-2.6 | TASK-005 | P2 |
| AC-2.7 | TASK-005 | P2 |
| AC-2.8 | TASK-004 | P2 |
| AC-2.9 | TASK-005 | P2 |
| AC-2.10 | TASK-005 | P2 |
| AC-3.1 | TASK-006 | P3 |
| AC-3.2 | TASK-006 | P3 |
| AC-3.3 | TASK-006 | P3 |
| AC-3.4 | TASK-006 | P3 |
| AC-3.5 | TASK-006 | P3 |
| AC-3.6 | TASK-007 | P3 |
| AC-3.7 | TASK-007 | P3 |
| AC-3.8 | TASK-006 | P3 |
| AC-3.9 | TASK-007 | P3 |
| AC-3.10 | TASK-006 | P3 |

**All 30 ACs mapped ✓**
