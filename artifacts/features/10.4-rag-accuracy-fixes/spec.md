# Spec: RAG Accuracy Fixes

## 1. Per-Collection Similarity Config

### REQ-01: Collection-level `min_similarity_threshold`
**Description**: Allow each document collection to define its own similarity threshold for grounding evaluation, overriding the global default.

**Why**: Different domains (legal, medical, casual) need different strictness. A legal collection may need 0.8; a brainstorming collection 0.3.

**Acceptance Criteria**:
- **AC-01.1**: `Collection` model has optional `min_similarity_threshold: float | None` field.
- **AC-01.2**: `GroundingService.evaluate_evidence()` reads collection config first, falls back to global `safety.min_similarity_threshold`.
- **AC-01.3**: Unit test: create two collections with thresholds 0.3 and 0.8; same chunks → different `is_sufficient` results.
- **AC-01.4**: No DB migration needed; `NULL` means "use global default".

### REQ-02: Runtime config exposure
**Description**: Expose the effective threshold in `RetrievalTrace` so the X-Ray panel can display it.

**Acceptance Criteria**:
- **AC-02.1**: `RetrievalTrace.grounding_threshold_used: float` populated.
- **AC-02.2**: Frontend X-Ray shows "Grounding threshold: 0.45" (example).

---

## 2. Grounding: Jaccard Pre-filter + LLM Score

### REQ-03: Two-step groundedness evaluation
**Description**: Replace single LLM call with:
1. **Jaccard filter** — compute word-overlap between answer sentences and each chunk; keep top-K (default 3) chunks with highest overlap.
2. **LLM judge** — run existing `GROUNDEDNESS_EVALUATION_PROMPT` only on filtered chunks.

**Why**: Reduces LLM context length, improves score accuracy by removing noise, lowers latency/cost.

**Acceptance Criteria**:
- **AC-03.1**: `GroundingService.calculate_groundedness()` signature unchanged; returns `(score, reason)`.
- **AC-03.2**: New private method `_jaccard_top_k(answer_text, chunks, k=3) -> List[Dict]`.
- **AC-03.3**: Integration test: answer fully supported by 1 of 10 chunks → score ≥ 0.85 (was ~0.5 before).
- **AC-03.4**: Latency: LLM call receives ≤ 3 chunks worth of context (≈1500 tokens vs 5000+).
- **AC-03.5**: Configurable `grounding.jaccard_top_k` (default 3) and `grounding.jaccard_min_overlap` (default 0.1).

### REQ-04: Traceability
**Description**: Record which chunks passed Jaccard filter in `RetrievalTrace.grounding_filtered_chunks: List[str]` (chunk IDs).

**Acceptance Criteria**:
- **AC-04.1**: Trace includes filtered chunk IDs.
- **AC-04.2**: X-Ray panel can display "Grounding used 3/10 chunks (Jaccard filter)".

---

## 3. Citation Schema: `[Source <chunk_id>]`

### REQ-05: Canonical citation format
**Description**: Change LLM prompt and parsing to use chunk UUID as citation label: `[Source abc-123-def]` instead of `[Source 1]`.

**Why**: Numeric indices are fragile (reordering breaks mapping). Chunk IDs are stable and traceable to DB.

**Acceptance Criteria**:
- **AC-05.1**: Generation prompt (`prompts.py`) instructs LLM: "Cite sources using `[Source <chunk_id>]` where chunk_id is the UUID provided in context."
- **AC-05.2**: `CitationService.CITATION_PATTERN` matches `\[Source\s+([a-f0-9-]{36})\]`.
- **AC-05.3**: `extract_citations()` returns list of chunk UUIDs.
- **AC-05.4**: `map_citations_to_chunks()` looks up by `chunk_id` directly (no numeric index fallback).
- **AC-05.5**: Backward-compat: if legacy `[Source N]` appears, log warning but still attempt numeric fallback.

### REQ-06: Context assembly includes chunk IDs
**Description**: `ContextService.assemble_context()` must inject `chunk_id` into each source block presented to LLM.

**Acceptance Criteria**:
- **AC-06.1**: Context block format:
  ```
  [Source abc-123-def]
  Title: Doc Title
  Page: 5
  Content: ...
  ```
- **AC-06.2**: Unit test verifies LLM receives chunk IDs in context.

---

## 4. Provenance Schema Extension

### REQ-07: ClaimNode with match metadata
**Description**: Extend `build_provenance()` output `claims` array items with:
- `match_score: float` — Jaccard overlap (0.0–1.0) between claim paragraph and best-matching cited chunk.
- `match_method: "jaccard" | "llm"` — how the quote was extracted.
- `matched_chunk_id: str | null` — chunk that produced the best match.

**Why**: Enables UI to highlight strong vs weak citations; supports "show evidence" drill-down.

**Acceptance Criteria**:
- **AC-07.1**: `ProvenanceResponse` Pydantic model updated with new fields.
- **AC-07.2**: `build_provenance()` computes Jaccard per paragraph vs its cited chunks; stores max score + method.
- **AC-07.3**: If no citation in paragraph → `match_score: 0.0`, `match_method: "none"`, `matched_chunk_id: null`.
- **AC-07.4**: `/turns/{turn_id}/provenance` returns extended schema.
- **AC-07.5**: Frontend X-Ray can render "Citation strength: 0.72 (jaccard)" per claim.

---

## 5. Conflict Detection Score Threshold

### REQ-08: Numeric conflict score
**Description**: `ConflictDetectionService.detect_conflict()` returns `conflict_score: float` (0.0–1.0) from LLM judge. `has_conflict` becomes derived: `conflict_score >= 0.8`.

**Why**: Binary flag loses nuance; score enables UI to show "minor tension (0.45)" vs "major contradiction (0.92)".

**Acceptance Criteria**:
- **AC-08.1**: Prompt `CONFLICT_DETECTION_EVALUATION_PROMPT` asks LLM to return `conflict_score` (0–1) + `conflict_details`.
- **AC-08.2**: Response parsed to float; default 0.0 on parse failure.
- **AC-08.3**: `has_conflict = conflict_score >= 0.8` (configurable via `safety.conflict_score_threshold`).
- **AC-08.4**: `surfaced_correctly` logic unchanged (answer acknowledges conflict).
- **AC-08.5**: Unit test: mock LLM returning 0.3 → `has_conflict=false`; 0.85 → `has_conflict=true`.

### REQ-09: Threshold configuration
**Description**: Add `safety.conflict_score_threshold` (default 0.8) to settings.

**Acceptance Criteria**:
- **AC-09.1**: Config value read in `ConflictDetectionService`.
- **AC-09.2**: Can be overridden per-collection (future) or globally.

---

## Cross-Cutting

### REQ-10: No breaking API changes
All endpoints keep same request/response shape; new fields are optional additions.

### REQ-11: Test coverage
Each REQ has ≥1 unit test + 1 integration test in `backend/tests/chat/`.

### REQ-12: Observability
All new logic emits structured logs with `turn_id`, `chunk_ids`, `scores` for debugging.

---

## Open Questions (resolved in this clarify pass)
- ~~Numeric vs UUID citations?~~ → **UUID** (stable, traceable).
- ~~Jaccard threshold?~~ → Configurable, default 0.1 overlap.
- ~~Conflict threshold?~~ → 0.8, configurable.
- ~~DB migration?~~ → No; config fields nullable.