# Task Breakdown

## Metadata
- Feature slug: rag-accuracy-fixes
- Date: 2026-07-10
- Status: Draft

---

## Phase 1: Grounding & Similarity Config
**Goal**: Enable per-collection similarity thresholds and improve groundedness accuracy via Jaccard pre-filter
**ACs**: AC-01.1–AC-01.4, AC-02.1–AC-02.2, AC-03.1–AC-03.5, AC-04.1–AC-04.2

- [x] TASK-001 Add `min_similarity_threshold` column to collections table
  Status: Done
  Summary: Add nullable REAL column `min_similarity_threshold` to `collections` table in `migrations/runner.py` SCHEMA_STATEMENTS; no migration needed for existing rows (NULL = use global default)
  Linked acceptance criteria: AC-01.4
  Affected file(s) or module(s): backend/migrations/runner.py
  Proving command or proof: `python -c "import sqlite3; conn=sqlite3.connect('data/knowledge_ingestion/app.db'); print([r[1] for r in conn.execute(\"PRAGMA table_info(collections)\")])"` → contains `min_similarity_threshold`

- [x] TASK-002 Extend CollectionRepository with `min_similarity_threshold` param
  Status: Done
  Summary: Add optional `min_similarity_threshold: float | None = None` param to `create_collection()` and `update_collection()`; pass through to INSERT/UPDATE statements; update `Collection` model class
  Linked acceptance criteria: AC-01.1
  Affected file(s) or module(s): backend/repositories/collection_repository.py, backend/models/collection.py
  Depends on: TASK-001
  Proving command or proof: Create collection with threshold 0.3, retrieve, assert `min_similarity_threshold == 0.3`

- [x] TASK-003 Expose effective threshold in RetrievalTrace
  Status: Done
  Summary: Add `grounding_threshold_used: float` field to `RetrievalTrace` schema in `schemas/chat.py`; populate in `ChatService.process_turn()` or `AdvancedRetrievalService.retrieve()` by reading collection config or global default
  Linked acceptance criteria: AC-02.1
  Affected file(s) or module(s): backend/schemas/chat.py, backend/chat/service.py, backend/chat/advanced_retrieval.py
  Proving command or proof: Run chat turn, inspect `retrieval_trace.grounding_threshold_used` in response

- [x] TASK-004 Implement `_jaccard_top_k()` private method in GroundingService
  Status: Done
  Summary: Add private method `_jaccard_top_k(answer_text, chunks, k=3, min_overlap=0.1) -> List[Dict]` that computes word-overlap Jaccard score per chunk, returns top-K chunks with highest overlap ≥ min_overlap
  Linked acceptance criteria: AC-03.2, AC-03.5
  Affected file(s) or module(s): backend/chat/grounding.py
  Proving command or proof: Unit test calls method with 10 chunks, 1 relevant (high overlap), 9 irrelevant; returns exactly 1 chunk

- [x] TASK-005 Modify `calculate_groundedness()` to use Jaccard pre-filter
  Status: Done
  Summary: In `calculate_groundedness()`, call `_jaccard_top_k()` first to filter chunks; pass filtered subset (≤3 chunks) to existing LLM judge prompt; preserve public signature `(answer_text, retrieved_chunks) -> (score, reason)`
  Linked acceptance criteria: AC-03.1, AC-03.3, AC-03.4
  Affected file(s) or module(s): backend/chat/grounding.py
  Depends on: TASK-004
  Proving command or proof: Integration test: answer fully supported by 1 of 10 chunks → score ≥ 0.85; verify LLM receives ≤3 chunks (token count check)

- [x] TASK-006 Record Jaccard-filtered chunks in RetrievalTrace
  Status: Done
  Summary: Add `grounding_filtered_chunks: List[str]` (chunk IDs) to `RetrievalTrace`; populate in `calculate_groundedness()` or caller; expose in X-Ray panel
  Linked acceptance criteria: AC-04.1, AC-04.2
  Affected file(s) or module(s): backend/schemas/chat.py, backend/chat/grounding.py
  Depends on: TASK-005
  Proving command or proof: Run chat turn with 10 chunks, inspect trace shows `grounding_filtered_chunks` with 3 IDs

---

## Phase 2: Citation Schema (UUID Labels)
**Goal**: Replace fragile numeric citation indices with stable chunk UUID labels
**ACs**: AC-05.1–AC-05.5, AC-06.1–AC-06.2

- [x] TASK-007 Update generation prompt for UUID citation format
  Status: Done
  Summary: In `prompts.py`, update `GENERATION_PROMPT` or context assembly instruction to tell LLM: "Cite sources using `[Source <chunk_id>]` where chunk_id is the UUID provided in context blocks"
  Linked acceptance criteria: AC-05.1
  Affected file(s) or module(s): backend/chat/prompts.py
  Proving command or proof: Inspect prompt string contains instruction for `[Source <chunk_id>]` format

- [x] TASK-008 Update CitationService regex and mapping for UUID labels
  Status: Done
  Summary: Change `CITATION_PATTERN` to `r'\[Source\s+([a-f0-9-]{36})\]'`; update `extract_citations()` to return UUIDs; update `map_citations_to_chunks()` to lookup by `chunk_id` directly (remove numeric index fallback or keep as legacy warning)
  Linked acceptance criteria: AC-05.2, AC-05.3, AC-05.4
  Affected file(s) or module(s): backend/chat/citations.py
  Depends on: TASK-007
  Proving command or proof: `test_citation_uuid_format.py` — extract citations from text with `[Source abc-123-def]`, assert returns `['abc-123-def']`; map to chunks, assert lookup by chunk_id

- [x] TASK-009 Inject `chunk_id` into context blocks for LLM
  Status: Done
  Summary: In `ContextService.assemble_context()`, format each source block as:
  ```
  [Source <chunk_id>]
  Title: ...
  Page: ...
  Content: ...
  ```
  Ensure chunk_id is always present
  Linked acceptance criteria: AC-06.1, AC-06.2
  Affected file(s) or module(s): backend/chat/context.py
  Proving command or proof: Unit test assembles context with 2 chunks, verifies output contains `[Source <uuid>]` for each
  Validation evidence: `test_context_chunk_id_injection.py` passes successfully with pytest.

---

## Phase 3: Provenance & Conflict Score
**Goal**: Extend provenance with match metadata; add numeric conflict scoring
**ACs**: AC-07.1–AC-07.5, AC-08.1–AC-08.5, AC-09.1–AC-09.2

- [x] TASK-010 Extend `ProvenanceResponse` schema with match metadata
  Status: Done
  Summary: Add fields to `ClaimItem` in `schemas/chat.py`: `match_score: float | None`, `match_method: str | None` ("jaccard" | "llm" | "none"), `matched_chunk_id: str | None`
  Linked acceptance criteria: AC-07.1
  Affected file(s) or module(s): backend/schemas/chat.py
  Proving command or proof: Pydantic model validation accepts new fields; serialization roundtrip preserves values

- [x] TASK-011 Compute match metadata in `build_provenance()`
  Status: Done
  Summary: In `CitationService.build_provenance()`, for each paragraph with citations: compute Jaccard overlap between paragraph text and cited chunks; store max score + method ("jaccard") + matched_chunk_id; if no citation → `match_score=0.0`, `match_method="none"`, `matched_chunk_id=null`
  Linked acceptance criteria: AC-07.2, AC-07.3
  Affected file(s) or module(s): backend/chat/citations.py
  Depends on: TASK-010
  Proving command or proof: `test_provenance_match_metadata.py` — build provenance for answer with 2 paragraphs (1 cited, 1 uncited); assert cited has `match_score > 0`, `match_method="jaccard"`; uncited has `match_score=0`, `match_method="none"`

- [x] TASK-012 Update conflict detection prompt for numeric score
  Status: Done
  Summary: Modify `CONFLICT_DETECTION_EVALUATION_PROMPT` in `prompts.py` to ask LLM to return `conflict_score: float` (0.0–1.0) in addition to `has_conflict`, `surfaced_correctly`, `conflict_details`
  Linked acceptance criteria: AC-08.1
  Affected file(s) or module(s): backend/chat/prompts.py
  Proving command or proof: Inspect prompt string requests `conflict_score` field in JSON response

- [x] TASK-013 Parse conflict score and derive `has_conflict`
  Status: Done
  Summary: In `ConflictDetectionService.detect_conflict()`, extract `conflict_score` from LLM JSON (default `0.0`). Set `has_conflict = conflict_score >= conflict_score_threshold`. Return `conflict_score` in output dict.
  Linked acceptance criteria: AC-08.2, AC-08.3
  Affected file(s) or module(s): backend/chat/conflict.py
  Depends on: TASK-012, TASK-014
  Proving command or proof: `test_conflict_threshold.py` — mock LLM returns `conflict_score=0.7`; with threshold=0.8 → `has_conflict=False`; with threshold=0.6 → `has_conflict=True`

- [x] TASK-014 Add `conflict_score_threshold` to safety settings
  Status: Done
  Summary: Add `conflict_score_threshold: float = 0.8` to `SafetySettings` in `schemas/settings.py`; expose via `config.safety.conflict_score_threshold`; read in `ConflictDetectionService.__init__()` or `detect_conflict()`
  Linked acceptance criteria: AC-09.1, AC-09.2
  Affected file(s) or module(s): backend/schemas/settings.py, backend/config.py, backend/chat/conflict.py
  Proving command or proof: Config load returns 0.8 default; override via settings file, assert service uses new value

---

## Resume
- **Next task**: TASK-001 (add nullable column to collections table — no dependencies, first step in Phase 1)
- **Blocker**: None
- **Next proof**: `python -c "..."` to verify column exists in SQLite schema

---

## Traceability Verification
Every REQ/AC from `spec.md` maps to a task:
- REQ-01 (AC-01.1–01.4) → TASK-001, TASK-002
- REQ-02 (AC-02.1–02.2) → TASK-003
- REQ-03 (AC-03.1–03.5) → TASK-004, TASK-005
- REQ-04 (AC-04.1–04.2) → TASK-006
- REQ-05 (AC-05.1–05.5) → TASK-007, TASK-008
- REQ-06 (AC-06.1–06.2) → TASK-009
- REQ-07 (AC-07.1–07.5) → TASK-010, TASK-011
- REQ-08 (AC-08.1–08.5) → TASK-012, TASK-013
- REQ-09 (AC-09.1–09.2) → TASK-014
- REQ-10, REQ-11, REQ-12 → All phases (backward compat + test coverage verified per task)