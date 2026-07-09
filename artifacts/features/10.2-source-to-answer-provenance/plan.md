# Implementation Plan: 10.2 Source-to-Answer Provenance

## Metadata

- Feature slug: `10.2-source-to-answer-provenance`
- Date: 2026-07-09
- Status: Approved
- Spec approved date: 2026-07-09

---

## Global Constraints

- **Non-goals (from spec):** Constrained decoding, hard repair loops, token/logprob attribution, new claim SQL table, multi-modal cites, save-to-note, badge label change, CitationModal as primary click, history answer mutation.
- **Technical constraints:** `provenance_json` on turn (no new table); additive field on SSE `citations` event (no new event type); append-only migration; shared provenance builder for sync+stream.
- **Security / trust boundaries:** No new trust boundaries; provenance is internal data.
- **Protected / preserved behavior:** SSE token-then-citations sequence (INV-003); legacy `[Source N]` history; invalid-label drop+mute; grounding refusal no-fake-cites; `retrieved_chunks_json` full metadata.
- **Explicit out of scope:** Constrained decoding, restore/repair loops, normalized claim table, sentence-level claims (paragraph blocks), badge label re-format.

---

## Part 1: Technical Design

### Comprehensive Design

- **Design Summary:** After generation, segment the answer into paragraphs (blank-line split), resolve citation labels per paragraph, compute coverage, and persist the claim graph as `provenance_json` on the turn. A shared `finalize_turn` function in `citations.py` replaces the duplicated finalize logic in `service.py` and `streaming.py`. Frontend renders `[unsupported]` on uncited paragraphs (display-layer only) and finishes the badge→panel anchor wire-up. X-Ray gets a Provenance section. Eval computes `citation_coverage`.

- **Current State:**
  - `citations.py`: post-hoc regex, unique labels only, no claim structure.
  - `service.py` finalize: groundedness + extract + map + persist.
  - `streaming.py` finalize: same logic duplicated, no groundedness persist.
  - `ChatPanel.jsx`: badge click opens `CitationModal`; badges show `Source N - Title`.
  - `screens/Chat.jsx`: duplicate citation path (modal + badge).
  - `XRayPanel.jsx`: no provenance section.
  - `evaluation.py`: no citation coverage metric.
  - Migration version: `0006_single_collection_chat`.

- **Proposed Architecture:**
  1. **Shared finalize builder** (`CitationService.build_provenance`): input `answer_text`, `retrieved_chunks` → output `{claims: [...], coverage: {...}}`. Paragraph split → label extract → map to chunks → Jaccard quote (no LLM fallback) → coverage aggregate.
  2. **Shared finalize function** (`finalize_turn` in `citations.py`): calls `build_provenance` + `calculate_groundedness` + `create_citation` DB rows + update turn with answer+groundedness+provenance. Used by both `service.py` and `streaming.py`.
  3. **Migration**: `ALTER TABLE chat_turns ADD COLUMN provenance_json TEXT NOT NULL DEFAULT '{}'`.
  4. **SSE/GET**: Add `provenance` field to SSE `citations` event payload; add GET endpoint `/chat/turns/{id}/provenance`.
  5. **Frontend ChatPanel**: Parse `provenance` from SSE/GET; for each claim, render `[unsupported]` if `cited=false`. Badge click → `setActiveChunkId` + expandSources. Delete `CitationModal` invocation from click handler (keep modal accessible via HoverCard/notes).
  6. **X-Ray**: New Provenance section reading from `provenance` prop.
  7. **Eval**: `citation_coverage` computed from `provenance.coverage` on turn.
  8. **Phase 0**: Stream groundedness call; delete legacy `Chat.jsx` citation handling.

- **Data Flow & Interfaces:**
  ```
  Generation complete (sync or stream)
    → finalize_turn(answer_text, safe_chunks, context_package)
      → CitationService.build_provenance(answer_text, safe_chunks)
          → split_paragraphs(text) -> [paragraph]
          → extract_citations(paragraph) -> labels[]
          → map_citations_to_chunks(labels, chunks) -> citations[]
          → jaccard_quote(paragraph, chunk_text) -> {quote_text, score}
          → aggregate coverage
          → return {claims: [...], coverage: ...}
      → grounding_service.calculate_groundedness(answer_text, safe_chunks)
      → ChatRepository.batch_create_citations(valid_citations)
      → ChatRepository.update_turn(..., provenance_json, groundedness_score)
      → return {provenance, citations, groundedness, ...sse payload}
  SSE: event "citations" { ..., provenance: {claims, coverage} }
  GET: /chat/turns/{id}/provenance -> {claims, coverage}
  ```

- **File / module touch list:**

  | Path | Change |
  |------|--------|
  | `backend/chat/citations.py` | Add `split_paragraphs`, `build_provenance`, `finalize_turn`; `jaccard_quote` (extract from `extract_quote` as helper) |
  | `backend/chat/service.py` | Replace inline finalize with `finalize_turn` call |
  | `backend/chat/streaming.py` | Replace inline finalize with `finalize_turn` call |
  | `backend/models/chat.py` | Add `provenance_json` to `ChatTurn` |
  | `backend/schemas/chat.py` | Add `ClaimGraph`, `ProvenanceCoverage`, `ProvenanceResponse`; update `ChatTurnResponse` |
  | `backend/repositories/chat_repository.py` | Pass `provenance_json` in create/update/list |
  | `backend/migrations/runner.py` | Add `0007_provenance_json` migration (ALTER TABLE) |
  | `backend/routers/chat.py` | Add `GET /chat/turns/{id}/provenance` |
  | `backend/chat/evaluation.py` | Compute `citation_coverage` from `provenance.coverage` |
  | `frontend/src/components/ChatPanel.jsx` | `[unsupported]` rendering; badge click → `setActiveChunkId` |
  | `frontend/src/components/XRayPanel.jsx` | Provenance section |
  | `frontend/src/screens/Chat.jsx` | Delete citation handling (Phase 0) |
  | `frontend/src/api/chat.js` | Add `getTurnProvenance` |
  | `backend/tests/chat/test_provenance.py` | New file for claim graph, finalize parity, API |

- **Key Decisions & Tradeoffs:**

  1. **Shared finalize function** (decided). Tradeoff: eliminates sync/stream drift at the cost of making the finalize contract explicit. A single entry point ensures groundedness + provenance + citations are always persisted together.
  2. **Paragraph-level claim unit** (spec lock). Tradeoff: Coarser than sentence-level, but more robust against markdown artifacts and fewer false uncited marks.
  3. **Jaccard-only quote; no LLM fallback** (spec lock). Tradeoff: Simpler, no latency spike; lower quote quality on paraphrase-heavy answers. Acceptable for v1 provenance metrics.
  4. **Display-layer only** `[unsupported]` (spec lock). Tradeoff: Reversible; no answer_text mutation. Frontend must re-parse provenance on history load.
  5. **`provenance_json` column, not new table** (spec lock). Tradeoff: Not queryable by SQL across turns; easy to normalize later if analytics demand it.

- **Non-Functional Considerations:**
  - **Performance:** `build_provenance` is O(n*m) where n=paragraphs (typically 2-8) and m=chunks (top-k, typically 5-20). Jaccard per match is set intersection on short strings. Estimated <5ms total.
  - **Reliability:** Provenance build errors caught at `finalize_turn` level; empty provenance on error with logged warning. Not a turn failure.
  - **Security:** No new trust boundaries; regex is same dual-format; no new user-controlled data paths.

- **Protected Behavior:**
  - SSE tokens emitted before `citations` event (order unchanged).
  - Both `[Source N]` and `[N]` labels parsed (dual regex reused).
  - Invalid labels dropped silently (same as today).
  - `CitationModal` remains accessible via HoverCard / document notes path (not called from badge click).
  - X-Ray retrieval/safety sections unchanged.
  - `retrieved_chunks_json` still full metadata.

---

## Part 2: Delivery Strategy

### Execution Context
- **Delivery profile:** Complex (cross-boundary)
- **Locked spec decisions:** See Global Constraints above.

### First Delivery Slice
- **Smallest useful slice:** Phase 0 (stream groundedness parity + legacy `Chat.jsx` citation path delete). This primes the finalize code for refactoring in Phase 1. It is independently testable and shippable.
- **Why this slice goes first:** Groundedness parity and legacy deletion reduce surface area before the shared finalize refactor. Deleting `Chat.jsx` citations means Phase 1 only touches one frontend path.
- **What proof should exist when this slice is done:**
  - Stream turn persists `groundedness_score` (AC-009).
  - `Chat.jsx` no longer renders `CitationModal`/`CitationBadge` (AC-010).

### User Story Decomposition
The feature has two user stories (US-001 chat verify, US-002 X-Ray inspect). Strategy: **Incremental** — tightly coupled to same claim graph payload.

| Phase | Story | Ships independently |
|-------|-------|---------------------|
| P0 (Setup) | n/a | no |
| P1: Claim graph + Chat UX | US-001 | yes |
| P2: X-Ray + Eval | US-002, US-003 | yes (requires P1 deployed) |

### Execution Phases

#### Phase 0: Foundational (Setup for Provenance)
- **Goal:** Eliminate stream groundedness gap; delete legacy citation surface.
- **Enabled user scenario(s) or outcome(s):** Consistent groundedness observability; single frontend citation path.
- **Entry proof:** Baseline streaming test passes.
- **Exit proof:** Stream turn has `groundedness_score`; `Chat.jsx` no longer has citation code.
- **Completion criteria:**
  - `streaming.py` calls `calculate_groundedness` and persists score.
  - `grep` confirms `Chat.jsx` has no citation-related code.
  - AC-009, AC-010 pass.

#### Phase 1: Claim Provenance Graph + Chat UX
- **Goal:** Build `build_provenance` + `finalize_turn` shared function, migration, SSE/GET payload, ChatPanel `[unsupported]` markers, badge→panel anchor.
- **Enabled user scenario(s) or outcome(s):** US-001 (every paragraph classified cited/uncited; click badge → panel anchor).
- **Entry proof:** Phase 0 done; migration runner test passes.
- **Exit proof:** SSE `citations` event includes `provenance` with claims+coverage; ChatPanel renders `[unsupported]`; badge anchors panel.
- **Completion criteria:**
  - `0007_provenance_json` migration runs; column present.
  - `build_provenance` + `finalize_turn` in `citations.py`; both paths call same function.
  - SSE `provenance` field present; GET endpoint returns same data.
  - `ChatPanel.jsx` renders `[unsupported]` on uncited paragraphs.
  - Badge click → `setActiveChunkId` + panel expand + scroll (no modal).
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006 pass.

#### Phase 2: X-Ray Provenance + Eval Metric
- **Goal:** X-Ray Provenance section; `citation_coverage` in eval output.
- **Enabled user scenario(s) or outcome(s):** US-002, US-003.
- **Entry proof:** Phase 1 done; X-Ray baseline test passes.
- **Exit proof:** X-Ray shows coverage+claim list+reverse map; eval output includes `citation_coverage`.
- **Completion criteria:**
  - `XRayPanel.jsx` Provenance section.
  - `evaluation.py` computes `citation_coverage`.
  - AC-007, AC-008 pass.

### Validation Strategy
- **Unit tests (`test_provenance.py`):** `build_provenance` with fully cited, partially cited, uncited, empty, invalid-label inputs. `split_paragraphs` edge cases. `finalize_turn` groundedness persist.
- **Integration tests (`test_finalize_parity.py`):** Same input → service.py and streaming.py produce identical provenance + groundedness.
- **Migration test (`test_migrations.py`):** 0007 runs idempotently.
- **Frontend tests (`ChatPanel.test.jsx`, `XRayPanel.test.jsx`):** `[unsupported]` rendering; badge click dispatches `setActiveChunkId`; provenance section renders.
- **Manual verification:** Scenarios 1–5 from spec.

### Traceability Matrix
| Scenario | Plan phase | Tasks |
|----------|----|-------|
| S1 (fully cited) | P1 | TASK-004, TASK-005, TASK-006, TASK-007 |
| S2 (partially cited) | P1 | TASK-004, TASK-005, TASK-008 |
| S3 (no citations) | P1 | TASK-004 |
| S4 (badge anchors) | P1 | TASK-009, TASK-010 |
| S5 (reverse lookup X-Ray) | P2 | TASK-012 |
| US-001 | P1 | TASK-004–TASK-010 |
| US-002 | P2 | TASK-012 |
| US-003 | P2 | TASK-013 |

| REQ | Phase | Task IDs |
|-----|----|----------|
| REQ-001 (claim graph) | P1 | TASK-004 |
| REQ-002 (shared finalize) | P1 | TASK-005, TASK-006 |
| REQ-003 (provenance_json) | P1 | TASK-002, TASK-003 |
| REQ-004 (SSE/GET) | P1 | TASK-007 |
| REQ-005 ([unsupported] display) | P1 | TASK-008 |
| REQ-006 (panel anchor) | P1 | TASK-009, TASK-010 |
| REQ-007 (X-Ray) | P2 | TASK-012 |
| REQ-008 (eval coverage) | P2 | TASK-013 |
| REQ-009 (stream groundedness) | P0 | TASK-001 |
| REQ-010 (legacy Chat.jsx delete) | P0 | TASK-011 |

### Rollout Plan
- **Release approach:** Atomic deployment (backend + frontend update together).
- **Feature flags:** None.
- **Migration needs:** Append-only `0007_provenance_json` (ALTER TABLE).
- **Backward compatibility notes:** Old turns without `provenance_json` return empty `{}`; frontend gracefully handles missing provenance.

### Rollback Plan
Revert git changes; `0007` migration is additive only (no data loss on rollback). `Chat.jsx` restore if deletion breaks — but verified in Phase 0.

### Risks And Mitigations
- **RISK-001 Paragraph alignment drift:** Blank lines inside lists or code blocks split logically. Mitigation: spec accepts paragraph-boundary noise in v1; log alignment mismatch metric for later tuning.
- **RISK-002 Legacy screen reach:** `Chat.jsx` imported by `App.jsx` but route `/chat` uses `WorkspaceLayout`, not `ChatScreen`. GitHub search confirms no other import. Mitigation: Phase 0 confirm no route renders `ChatScreen` before deleting citations.
- **RISK-003 Sync/stream refactor drift:** Shared `finalize_turn` must preserve SSE event order. Mitigation: unit test asserts SSE event sequence identical before/after refactor.
- **RISK-004 `provenance_json` size:** <5KB typical. Mitigation: TEXT column; no index needed.
- **RISK-005 Display-layer `[unsupported]` misalignment:** Frontend/backend split matching may drift. Mitigation: both use same `split_paragraphs` exported from citations.py; unit test verifies parity.

### Open Questions
- None (all resolved in spec grilling + ADR-001).

---

## Plan Self-Review (before Plan Approved)

- [x] Global Constraints filled from spec.
- [x] Every REQ/AC maps to a phase or task ID in Traceability Matrix.
- [x] No placeholder prose in design or first-slice proof.
- [x] First unblocked task executable from `tasks.md` alone.
- [x] File/module targets named.
- [x] Proof commands exact (runnable).
- [x] Dependency edges in `tasks.md` will be checked with `python3 scripts/core/task_graph.py --feature 10.2-source-to-answer-provenance --check`.
