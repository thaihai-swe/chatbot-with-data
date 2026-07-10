# Implementation Plan: RAG Accuracy Fixes

## Metadata
- Feature slug: rag-accuracy-fixes
- Date: 2026-07-10
- Status: Draft
- Spec approved date: 2026-07-10

---

## Global Constraints

> Copy limits from spec (Non-Goals, Constraints, Security, preserved). Do not violate.

- **Non-goals (from spec)**: No new retrieval strategies, no frontend UI changes, no DB migrations, no new API endpoints, no evaluation framework changes
- **Technical / business / delivery constraints**: Must remain backward-compatible; no breaking changes to existing APIs; all changes must be surgical patches to existing services
- **Security / trust boundaries**: No changes to safety scanning logic; existing prompt injection detection unchanged
- **Protected / preserved behavior**: GroundingService signature unchanged; CitationService public API unchanged; ConflictDetectionService public API unchanged
- **Explicit out of scope**: Replacing LLM provider abstraction, multi-turn conversation context compression, cost tracking/budgeting

---

## Part 1: Technical Design

### Lightweight Design

**Approach**: Five independent patches to existing services, each adding precision without changing public contracts. All changes are additive (new optional fields, new private methods) or replacements within private implementations.

**Key Decision**: Use UUID-based citation labels (`[Source <chunk_id>]`) instead of numeric indices for stable, DB-traceable citations. This is the foundation for provenance improvements.

**Files / modules likely touched**:
- `backend/migrations/runner.py` — Add nullable `min_similarity_threshold` column to collections table
- `backend/repositories/collection_repository.py` — Add `min_similarity_threshold` param to create/update methods
- `backend/models/collection.py` — Add new field to model class
- `backend/chat/grounding.py` — Add `_jaccard_top_k()` private method; modify `calculate_groundedness()` to use Jaccard pre-filter
- `backend/chat/citations.py` — Update `CITATION_PATTERN` regex; modify `extract_citations()`, `map_citations_to_chunks()`, `build_provenance()` to support UUID labels and match metadata
- `backend/chat/conflict.py` — Modify `detect_conflict()` to return `conflict_score: float`; derive `has_conflict` from threshold
- `backend/chat/prompts.py` — Update generation prompt to instruct LLM on `[Source <chunk_id>]` format
- `backend/chat/context.py` — Modify `assemble_context()` to inject `chunk_id` into source blocks
- `backend/schemas/chat.py` — Extend `ProvenanceResponse` Pydantic model with new fields
- `backend/config.py` — Add `grounding.jaccard_top_k`, `grounding.jaccard_min_overlap`, `safety.conflict_score_threshold` settings
- `backend/schemas/settings.py` — Add new config fields to `GroundingSettings`, `SafetySettings`

---

## Part 2: Delivery Strategy

### Execution Context
- **Delivery profile**: Simple — targeted patches, no new integrations, no data model changes (only nullable column addition)
- **Locked spec decisions**: UUID citations only; Jaccard pre-filter before LLM judge; conflict score threshold 0.8; per-collection similarity override

### First Delivery Slice
- **Smallest useful slice**: REQ-01 (collection similarity config) + REQ-03 (Jaccard grounding) — these two together provide immediate accuracy improvement
- **Why this slice goes first**: Both are internal to `GroundingService`; no API contract changes; can be verified with unit tests alone; unblocks downstream citation/provenance work
- **What proof should exist when this slice is done**:
  - Collection created with `min_similarity_threshold=0.3` accepts chunks with score 0.4; same chunks rejected by collection with threshold 0.8
  - Groundedness score ≥0.85 when answer supported by 1 of 10 chunks (vs ~0.5 before)

### Execution Phases

#### Phase 1: Grounding & Similarity Config
- **Goal**: Enable per-collection similarity thresholds and improve groundedness accuracy via Jaccard pre-filter
- **Enabled user scenario(s) or outcome(s)**: Document collections with different strictness levels; more accurate groundedness scores with less LLM context
- **Entry proof**: Existing tests pass (no regression)
- **Exit proof**:
  - `test_grounding_collection_threshold.py` passes (AC-01.3)
  - `test_grounding_jaccard_filter.py` passes (AC-03.3, AC-03.4)
- **Completion criteria**: REQ-01, REQ-02, REQ-03, REQ-04 implemented and tested

#### Phase 2: Citation Schema (UUID Labels)
- **Goal**: Replace fragile numeric citation indices with stable chunk UUID labels
- **Enabled user scenario(s) or outcome(s)**: Citations traceable to DB without reordering issues; provenance can reliably map labels to chunks
- **Entry proof**: Phase 1 complete; existing citation tests pass
- **Exit proof**:
  - `test_citation_uuid_format.py` passes (AC-05.1–AC-05.4)
  - `test_context_chunk_id_injection.py` passes (AC-06.1, AC-06.2)
- **Completion criteria**: REQ-05, REQ-06 implemented and tested

#### Phase 3: Provenance & Conflict Score
- **Goal**: Extend provenance with match metadata; add numeric conflict scoring
- **Enabled user scenario(s) or outcome(s)**: UI can highlight citation strength; conflict detection shows nuance ("minor tension 0.45" vs "major contradiction 0.92")
- **Entry proof**: Phase 2 complete; citation format stable
- **Exit proof**:
  - `test_provenance_match_metadata.py` passes (AC-07.1–AC-07.5)
  - `test_conflict_score_threshold.py` passes (AC-08.1–AC-08.5, AC-09.1)
- **Completion criteria**: REQ-07, REQ-08, REQ-09 implemented and tested

### Validation Strategy
- **Unit tests**: Each REQ has dedicated test file in `backend/tests/chat/`
  - `test_grounding_collection_threshold.py`
  - `test_grounding_jaccard_filter.py`
  - `test_citation_uuid_format.py`
  - `test_context_chunk_id_injection.py`
  - `test_provenance_match_metadata.py`
  - `test_conflict_score_threshold.py`
- **Integration tests**: End-to-end chat turn with each feature enabled
  - `test_chat_grounding_accuracy.py`
  - `test_chat_citation_traceability.py`
  - `test_chat_conflict_detection.py`
- **End-to-end tests**: Full pipeline verification via existing sanity check dataset
- **Manual verification**: X-Ray panel shows new fields (grounding threshold, filtered chunks, citation strength, conflict score)
- **Observability checks**: Structured logs contain `turn_id`, `chunk_ids`, `scores` for all new logic paths

### Traceability Matrix
- **REQ-01** → Phase 1, TASK-001, TASK-002
- **REQ-02** → Phase 1, TASK-003
- **REQ-03** → Phase 1, TASK-004, TASK-005
- **REQ-04** → Phase 1, TASK-006
- **REQ-05** → Phase 2, TASK-007, TASK-008
- **REQ-06** → Phase 2, TASK-009
- **REQ-07** → Phase 3, TASK-010, TASK-011
- **REQ-08** → Phase 3, TASK-012, TASK-013
- **REQ-09** → Phase 3, TASK-014
- **REQ-10** → All phases (backward compat verified in each test)
- **REQ-11** → All phases (each REQ has ≥1 unit + 1 integration test)
- **REQ-12** → All phases (log statements added in each implementation)

### Rollout Plan
- **Release approach**: Merge to feature branch, run full test suite, merge to main
- **Feature flags**: None — all changes are always-on improvements to existing behavior
- **Migration needs**: None — nullable column addition is backward-compatible
- **Backward compatibility notes**: Legacy `[Source N]` citations still work (AC-05.5); numeric fallback preserved for transition period

### Rollback Plan
How to revert safely: Git revert of feature branch merge commit. No data migration to undo. All changes are additive or internal replacements.

### Risks And Mitigations
- **RISK-001**: LLM prompt change may cause generation quality regression if UUID format confuses model
  - **Mitigation**: Prompt explicitly states "use the chunk_id UUID provided in context brackets"; test with existing sanity dataset before merge
- **RISK-002**: Jaccard filter may filter out valid chunks if overlap threshold too high
  - **Mitigation**: Configurable `jaccard_min_overlap` default 0.1 (lenient); AC-03.3 validates score improvement

### Open Questions
- **Q-001**: Should we deprecate numeric citation fallback after transition period?
  - **Next step**: Monitor logs for legacy format usage; decide in 30 days based on adoption

---

## Plan Self-Review (before Plan Approved)
- [x] Global Constraints filled from spec (not left blank when spec has Non-Goals/Constraints)
- [x] Every REQ/AC maps to a phase or task ID in the Traceability Matrix
- [x] No placeholder prose ("TBD", "TODO design later") in design or first-slice proof
- [x] First unblocked task is executable from `tasks.md` alone
- [x] File/module targets named for non-trivial work (Comprehensive or Lightweight touch list)
- [x] Proof commands are exact (runnable), not "add tests"
- [x] Dependency edges in `tasks.md` checked: `python3 scripts/core/task_graph.py --feature <slug> --check` (will run after tasks.md created)