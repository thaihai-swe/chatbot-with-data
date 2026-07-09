# Feature Specification: 10.2 Source-to-Answer Provenance

## Metadata

- Feature name: Source-to-Answer Provenance
- Feature slug: `10.2-source-to-answer-provenance`
- Delivery profile: Complex
- Owner: Antigravity
- Status: Draft
- Related knowledge artifact(s): [analysis.md](file:///Users/thaihai-swe/Desktop/chatbot-with-data/artifacts/features/10.2-source-to-answer-provenance/analysis.md)

## Problem Statement

The RAG system retrieves relevant chunks and produces cited answers, but there is **no claim-level provenance**: we cannot answer "which specific claim does this citation support?" or "what fraction of claims are cited?" or "show all claims backed by chunk X." The production RAG audit §5.4 identified this as a gap vs Notebook LM. 9.0 improved prompt pressure and UI chrome but left provenance at turn-level bag-of-citations.

## Desired Outcomes

- **Chat UX:** Every paragraph/claim shows citation badges; uncited paragraphs display a muted `[unsupported]` marker (display-layer only). Clicking a badge anchors the left Sources panel and highlights the chunk (finishes 9.0 wire-up).
- **X-Ray:** New Provenance section shows claim graph, coverage %, and reverse lookup (claims per chunk).
- **API/SSE:** Existing `citations` event carries `provenance` field with claims + coverage; GET endpoint mirrors it.
- **Eval:** `citation_coverage` metric available alongside recall/groundedness.
- **Foundation:** Stream/sync groundedness parity fixed as Phase 0; legacy Chat.jsx citation path deleted.

## Minimum Release Slice

- **What ships in the first useful release:**
  - Phase 0: Stream groundedness parity (call `calculate_groundedness` in `streaming.py`; persist score).
  - Phase 0: Delete legacy `Chat.jsx` citation handling (verify no other dependents; route through `ChatPanel.jsx`).
  - Phase 1: Claim segmentation (paragraph blocks), citation label resolution per paragraph, provenance builder shared by sync/stream.
  - Phase 1: `provenance_json` on turn; additive `provenance` field on SSE `citations` event; GET `/chat/turns/{id}/provenance`.
  - Phase 1: Display-layer `[unsupported]` on uncited paragraphs in `ChatPanel.jsx` (no `answer_text` mutation).
  - Phase 1: Badge click → `setActiveChunkId` + expand sources + scroll (finish 9.0).
  - Phase 1: X-Ray Provenance section with claim list, coverage, reverse mapping.
  - Phase 1: `citation_coverage` in `EvaluationService` sanity check.
- **What can wait:**
  - Soft repair loop (re-ask / rewrite when coverage < threshold).
  - Structured generation / constrained decoding.
  - Normalized claim table (keep `provenance_json`).
  - Token-level attribution / provider logprobs.
  - Multi-modal citations (images, audio).
  - Save-to-note / knowledge loop.

## Success Criteria

- **SC-001:** Every paragraph in the answer is classified as cited (has ≥1 resolved citation label) or uncited, and this mapping is stored in `provenance_json` and returned on SSE/GET.
- **SC-002:** Coverage metric (`cited_paragraphs / total_paragraphs`, `uncited[]`) computed and persisted for every completed turn.
- **SC-003:** `ChatPanel.jsx` renders `[unsupported]` (muted, non-clickable) on uncited paragraphs; cited paragraphs show existing badges unchanged (badge label stays `Source N - Title` per user decision).
- **SC-004:** Clicking a badge calls `setActiveChunkId(chunk_id, document_id)`, expands Sources panel, and scrolls/highlights the chunk in `SourceBrowser`.
- **SC-005:** SSE `citations` event includes `provenance` field with claims + coverage; GET endpoint returns same shape.
- **SC-006:** X-Ray shows Provenance section: claim list (text, cited?, labels, chunks), coverage %, reverse map (chunk → claims).
- **SC-007:** `EvaluationService.run_sanity_check` output includes `citation_coverage` per case and overall.
- **SC-008:** Stream path persists `groundedness_score` (Phase 0 parity fix).
- **SC-009:** Legacy `Chat.jsx` no longer handles citations (deleted or delegated to `ChatPanel`).

## In Scope

- Claim segmentation (paragraph blocks by blank line).
- Citation label resolution per paragraph using existing dual-format regex.
- Shared provenance builder used by `service.py` and `streaming.py`.
- `provenance_json` column on `chat_turns` (append-only migration).
- SSE `citations` event additive `provenance` field; GET `/chat/turns/{id}/provenance`.
- Display-layer `[unsupported]` marker in `ChatPanel.jsx` paragraph rendering.
- Badge click wire-up: `setActiveChunkId` + expand sources + scroll (finishes 9.0).
- X-Ray Provenance section.
- `citation_coverage` in evaluation output.
- Stream groundedness parity (Phase 0).
- Legacy `Chat.jsx` citation path deletion (Phase 0).

## Out Of Scope

- Constrained decoding / tool-forced structured cites.
- Hard fail or regenerate loop on low coverage.
- Token-level attribution or logprob-based provenance.
- Normalized claim SQL table (use `provenance_json`).
- Multi-modal (image/audio) citation mapping.
- Save-to-note / knowledge loop (notes as sources).
- Sentence-level claim units (paragraph blocks chosen).
- Badge label format change (keep `Source N - Title`).
- CitationModal as primary click target (panel anchor only).
- Jaccard quote scoring persisted (graph stores quote_text + match_score from Jaccard; no LLM fallback in v1).

## Non-Goals

- Replacing Weaviate or vector search.
- Modifying safety pipeline.
- Changing streaming token protocol beyond additive field.
- Rewriting history answers (display-layer only).

## Users And Stakeholders

- **Primary users:** Researchers and analysts verifying chat claims against sources; engineers running eval harnesses.
- **Secondary stakeholders:** Product (audit parity); future features needing claim→chunk lookup.

## User Stories And Key Scenarios

- **US-001 (Chat verify):** As a researcher, I see every paragraph in the answer marked with badges or `[unsupported]`. I click a badge and the source chunk is highlighted in the left panel so I can verify instantly.
- **US-002 (X-Ray inspect):** As an engineer, I open X-Ray and see the provenance section with coverage % and the claim graph. I can click a chunk ID and see which paragraphs it supports.
- **US-003 (Eval metric):** As an eval runner, sanity check output includes `citation_coverage` so I can track regression.

### Detailed Scenarios

- **Scenario 1 (Happy Path — fully cited answer):**
  - **Given:** A turn completes with an answer containing 3 paragraphs, each with `[Source 1]`/`[Source 2]` markers.
  - **When:** The turn finalizes.
  - **Then:** `provenance_json` has 3 claims, all `cited=true`, coverage=100%. SSE `citations` event includes `provenance` with claims array and coverage. Chat shows 3 paragraphs with badges; no `[unsupported]`. X-Ray shows 3 claims, 100% coverage.

- **Scenario 2 (Edge Case — partially cited):**
  - **Given:** An answer with 4 paragraphs; paragraph 2 has no citation marker.
  - **When:** The turn finalizes.
  - **Then:** `provenance_json` has 4 claims; claim 2 `cited=false`, labels=[], chunks=[]. Coverage=75%, `uncited=[1]` (0-based index). Chat renders paragraph 2 with muted `[unsupported]` prefix/suffix; other paragraphs normal. X-Ray shows coverage 75%, uncited list.

- **Scenario 3 (Error State — no citations at all):**
  - **Given:** Model emits no citation markers (or all invalid).
  - **When:** The turn finalizes.
  - **Then:** All paragraphs `cited=false`. Coverage=0%. Chat renders `[unsupported]` on all. X-Ray shows 0% coverage. SSE `provenance` present with empty `labels`/`chunks` for each claim.

- **Scenario 4 (Badge click anchors):**
  - **Given:** Chat shows an answer with a `[Source 2 - MyDoc.pdf]` badge.
  - **When:** User clicks the badge.
  - **Then:** Sources panel expands, `SourceBrowser` loads `MyDoc.pdf`, chunk matching `Source 2` is highlighted and scrolled into view. No `CitationModal` opens.

- **Scenario 5 (Reverse lookup in X-Ray):**
  - **Given:** X-Ray Provenance section is open on a completed turn.
  - **When:** User clicks a chunk ID in the reverse map.
  - **Then:** Corresponding claim indices are highlighted in the claim list.

## Current Context

- **Current behavior summary:**
  - Post-hoc extraction: unique labels → chunks (deduped); `quote_text` via Jaccard/LLM fallback.
  - Citations stored per unique label, not per claim occurrence.
  - `CitationModal` on click; panel anchor state exists but not wired from chat click.
  - Badge labels show `Source N - Title`.
  - SSE `citations` event: citations[], retrieved_chunks[], traces, conflict_*.
  - Stream path missing `groundedness_score` persist.
  - `Chat.jsx` and `ChatPanel.jsx` duplicate citation rendering/modal logic.
  - X-Ray has Safety, Transformations, Strategy, Latency, Raw — no provenance.
  - Eval measures recall + groundedness only.

- **Impacted boundaries:**
  - `backend/chat/citations.py` — extend to per-paragraph graph builder.
  - `backend/chat/service.py`, `backend/chat/streaming.py` — shared provenance builder; stream groundedness fix.
  - `backend/models/chat.py` — add `provenance_json` to `ChatTurn`; migration.
  - `backend/schemas/chat.py` — `ProvenanceResponse` + updated `ChatTurnResponse`.
  - `backend/repositories/chat_repository.py` — persist/read `provenance_json`.
  - `backend/chat/evaluation.py` — add `citation_coverage` to `EvalResult`/`SanityCheckResponse`.
  - `frontend/src/components/ChatPanel.jsx` — paragraph rendering with `[unsupported]`; badge click → `setActiveChunkId`.
  - `frontend/src/components/XRayPanel.jsx` — Provenance section.
  - `frontend/src/screens/Chat.jsx` — delete legacy citation handling.
  - `backend/database/migrations/` — append-only migration for `provenance_json`.

- **Preserved behavior:**
  - Streaming SSE tokens first, then `citations` event (INV-003).
  - Legacy `[Source N]` history parses (dual regex).
  - Invalid labels dropped silently server-side, muted client-side.
  - `retrieved_chunks_json` full metadata; `context_used_json` traces.
  - Grounding refusal path emits no fake citations.

- **Brownfield risk rating:** Medium — shared module (`citations.py`), partial coverage, dual orchestrators (sync/stream), legacy screen duplication.

## Gray-Area Decisions

- **Locked decisions that shape this spec:**
  - ADR-001: Post-gen claim graph + `provenance_json`; no constrained decoding / hard repair in v1.
  - Claim unit = paragraph blocks (blank-line split).
  - Badge label = `Source N - Title` (keep current; 9.0 SC-004 not adopted).
  - Uncited mark = display-layer only in `ChatPanel.jsx` (no `answer_text` mutation).
  - Badge click = panel anchor only (`setActiveChunkId` + expand + scroll); `CitationModal` secondary.
  - Provenance payload = additive `provenance` field on existing SSE `citations` event + GET endpoint.
  - Phase 0: Stream groundedness parity fix + legacy `Chat.jsx` deletion before Phase 1.
  - Jaccard quote only; no LLM fallback in v1 provenance.

- **Remaining decisions that still block approval:** None (all resolved in grilling).

## Dependencies And External Touchpoints

- **DEP-001:** `WorkspaceContext.setActiveChunkId` + `SourceBrowser` scroll/highlight already implemented (9.0).
- **DEP-002:** `CitationService` dual regex + `map_citations_to_chunks` stable.
- **DEP-003:** Append-only migration runner pattern (5 versions exist).

## Functional Requirements

### REQ-001: Claim Segmentation & Graph Builder (Core)

- **Requirement:** After generation, split the answer text into paragraph blocks (separated by blank lines). For each paragraph, extract citation labels using the dual-format regex (`\[Source\s+([^\]]+)\]|\[(\d+)\]`). Map labels to chunks via existing index/UUID logic (`map_citations_to_chunks`). Build a claim object with `{text, start_char, end_char, labels[], chunks[], cited:boolean, quote_text, match_score, match_method}`. Aggregate into `{claims:[...], coverage:{cited,total,uncited_indices[]}}`.
- **Why it matters:** Produces the claim→chunk graph enabling coverage, reverse lookup, and UI markers.
- **Linked ACs:** SC-001, SC-002, SC-005
- **Priority:** Must Have
- **Validation surface:** `backend/tests/chat/test_citations.py` + new `test_provenance.py`

### REQ-002: Shared Provenance Builder (Sync + Stream)

- **Requirement:** Extract the post-generation finalize logic into a shared function `finalize_turn(answer_text, retrieved_chunks, context_package, llm_provider)` used by both `service.py` and `streaming.py`. It computes provenance, persists citations + `provenance_json`, updates turn with `groundedness_score`, and returns the SSE `citations` payload (with `provenance`).
- **Why it matters:** Eliminates sync/stream drift (groundedness parity) and single-source-of-truth for provenance.
- **Linked ACs:** SC-001, SC-005, SC-008
- **Priority:** Must Have

### REQ-003: Persistence — `provenance_json` on Turn

- **Requirement:** Add `provenance_json` TEXT column to `chat_turns` (append-only migration). Serialize the claim graph + coverage object to JSON on turn completion. Read back in `ChatTurnResponse`.
- **Why it matters:** Durable claim graph for history, X-Ray, eval, and future features without schema churn.
- **Linked ACs:** SC-001, SC-002, SC-005
- **Priority:** Must Have

### REQ-004: SSE + GET Provenance Payload

- **Requirement:** Extend the SSE `citations` event payload with an optional `provenance` field containing the claim graph + coverage. Add `GET /chat/turns/{id}/provenance` returning the same shape.
- **Why it matters:** Frontend X-Ray and future tooling can read provenance without re-parsing answer text.
- **Linked ACs:** SC-005
- **Priority:** Must Have

### REQ-005: Chat UX — Display-Layer `[unsupported]` on Uncited Paragraphs

- **Requirement:** In `ChatPanel.jsx`, when rendering a turn that has `provenance` (from SSE or history GET), split answer into paragraphs aligned with `provenance.claims`. For each claim with `cited=false`, render a muted, non-clickable `[unsupported]` marker adjacent to the paragraph (prefix or suffix). Cited paragraphs render existing badges unchanged (`Source N - Title`). Do not modify stored `answer_text`.
- **Why it matters:** Notebook-LM-like honesty without history mutation; reversible if model improves.
- **Linked ACs:** SC-003
- **Priority:** Must Have

### REQ-006: Badge Click → Panel Anchor (Finish 9.0 Wire-up)

- **Requirement:** In `ChatPanel.jsx`, badge `onClick` calls `setActiveChunkId(chunk_id, document_id)` (from `WorkspaceContext`). This expands Sources panel, loads `SourceBrowser` with the document, and scrolls/highlights the chunk. `CitationModal` is no longer opened from badge click (can remain accessible via HoverCard deep-dive or notes button in SourceBrowser).
- **Why it matters:** Completes the 9.0 anchored-UX design; modal was a temporary fallback.
- **Linked ACs:** SC-004
- **Priority:** Must Have

### REQ-007: X-Ray Provenance Section

- **Requirement:** Add a Provenance section to `XRayPanel.jsx` showing:
  - Coverage summary: `X/Y paragraphs cited (Z%)`.
  - Claim list: for each claim, show paragraph index, `cited` badge, text excerpt (first 120 chars), citation labels, linked chunk IDs (click → highlight in claim list).
  - Reverse map: chunk ID → list of claim indices it supports (click claim index → highlight claim).
- **Why it matters:** Debug/observability surface for claim graph; matches audit demand for X-Ray parity.
- **Linked ACs:** SC-006
- **Priority:** Must Have

### REQ-008: Eval `citation_coverage` Metric

- **Requirement:** Extend `EvaluationService._evaluate_case` to compute `citation_coverage = cited_paragraphs / total_paragraphs` from the turn's provenance. Add to `EvalResult` and `SanityCheckResponse`. Overall coverage in aggregate.
- **Why it matters:** Tracks citation completeness as a first-class quality signal alongside recall/groundedness.
- **Linked ACs:** SC-007
- **Priority:** Should Have

### REQ-009: Phase 0 — Stream Groundedness Parity

- **Requirement:** In `streaming.py` finalize block, call `grounding_service.calculate_groundedness(answer_text, safe_chunks)` and persist `groundedness_score` on the turn (mirroring `service.py:211-258`).
- **Why it matters:** Prerequisite for consistent provenance + groundedness observability; single finalize refactor in REQ-002.
- **Linked ACs:** SC-008
- **Priority:** Must Have (Phase 0)

### REQ-010: Phase 0 — Delete Legacy `Chat.jsx` Citation Path

- **Requirement:** Verify `screens/Chat.jsx` is not used by other routes/components. Remove its `handleCitationClick`, `activeChunk`, `CitationModal`, and badge rendering logic. Ensure `/chat` route uses `ChatPanel.jsx` exclusively.
- **Why it matters:** Eliminates duplicate citation UX surface; single source of truth for Phase 1 changes.
- **Linked ACs:** SC-009
- **Priority:** Must Have (Phase 0)

## Non-Functional Requirements

- **NFR-001 Performance:** Provenance builder adds <10ms post-generation latency (paragraph split + label resolve). **Linked ACs:** SC-001, SC-005.
- **NFR-002 Reliability:** Provenance JSON must never cause turn failure; on error, persist empty provenance and log warning. **Linked ACs:** SC-001, SC-005.
- **NFR-003 Security:** No new trust boundaries; `provenance_json` is internal data. **Linked ACs:** SC-005.
- **NFR-004 Accessibility:** `[unsupported]` marker has sufficient contrast; keyboard-focusable badge unchanged. **Linked ACs:** SC-003.
- **NFR-005 Observability:** Provenance appears in X-Ray, SSE, GET, eval output. **Linked ACs:** SC-005, SC-006, SC-007.

## Constraints

- **Technical:** Must use existing dual-format regex; must not break SSE token → `citations` event sequence; migration append-only.
- **Business:** ADR-001 boundaries frozen; no structured-gen scope creep.
- **Delivery:** Phase 0 (groundedness + legacy delete) before Phase 1 (provenance + X-Ray + eval).

## Assumptions

- **ASM-001:** Paragraph blank-line split is a sufficient claim unit for v1 coverage metrics.
- **ASM-002:** Existing `map_citations_to_chunks` index/UUID resolution correctly maps labels to chunks for paragraph-level use.
- **ASM-003:** `WorkspaceContext.setActiveChunkId` + `SourceBrowser` scroll/highlight works for all document types in scope.
- **ASM-004:** `Chat.jsx` is reachable only via `/chat` route and has no other callers of its citation methods.

## Risks

- **RISK-001 Paragraph alignment drift:** Model output may have blank lines inside a logical claim (lists, code blocks) or missing blank lines between claims. Mitigation: Spec defines paragraph = blank-line-separated block; edge cases accepted as noise in v1.
- **RISK-002 Legacy screen reach:** Deleting `Chat.jsx` citation logic may break an unknown route. Mitigation: Phase 0 search for `import.*Chat.jsx` and route usage before delete.
- **RISK-003 Sync/stream refactor risk:** Shared finalize function must not change SSE timing. Mitigation: keep `streaming.py` SSE order identical; unit test event sequence.
- **RISK-004 `provenance_json` size:** Long answers with many paragraphs could grow the column. Mitigation: TEXT column; typical <5KB; monitor.
- **RISK-005 Display-layer `[unsupported]` mismatch:** If frontend splits paragraphs differently from backend provenance builder, markers misalign. Mitigation: spec requires shared split logic (paragraphs by blank line) documented in one place (e.g., `citations.py` exported helper).

## Open Questions

- **Q-001:** Paragraph split exact regex (blank-line = `\n\s*\n`? handle Windows `\r\n`)? → Resolve in spec authoring; non-blocking, default to `/\n{2,}/`.
- **Q-002:** `quote_text` in provenance claim object — use Jaccard best match (no LLM fallback)? → Resolved: Jaccard only in v1; `match_method="jaccard"`, `match_score` stored.

## Acceptance Criteria

- [ ] **AC-001** Linked REQ: REQ-001
  - Linked scenario: Scenario 1, Scenario 2
  - Validation method: Unit test `test_provenance.py::test_build_claim_graph` — input answer with 3 paragraphs + 2 cited; output claims array length=3, coverage=2/3, uncited index correct.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest backend/tests/chat/test_provenance.py -v`

- [ ] **AC-002** Linked REQ: REQ-002
  - Linked scenario: Scenario 1, Scenario 3
  - Validation method: Both `service.py` and `streaming.py` import and call the same `finalize_turn` helper; `groundedness_score` persisted on stream turn; provenance JSON present on both.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest backend/tests/chat/test_finalize_parity.py -v`

- [ ] **AC-003** Linked REQ: REQ-003
  - Linked scenario: Scenario 1
  - Validation method: Migration runs; `provenance_json` column exists; `ChatTurn.provenance_json` round-trips valid JSON matching provenance schema.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest backend/tests/chat/test_migrations.py::test_provenance_column -v`

- [ ] **AC-004** Linked REQ: REQ-004
  - Linked scenario: Scenario 1
  - Validation method: SSE `citations` event contains `provenance` field with claims+coverage; `GET /chat/turns/{id}/provenance` returns identical object.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest backend/tests/chat/test_provenance_api.py -v`

- [ ] **AC-005** Linked REQ: REQ-005
  - Linked scenario: Scenario 2, Scenario 3
  - Validation method: `ChatPanel.jsx` renders `[unsupported]` (muted, non-clickable) on paragraphs corresponding to `cited=false` claims; cited paragraphs show badges. Stored `answer_text` unchanged.
  - Proof target: Manual UI check + `bash scripts/harness/gate-runner.sh pytest frontend/tests/ChatPanel.test.jsx::test_unsupported_marker -v`

- [ ] **AC-006** Linked REQ: REQ-006
  - Linked scenario: Scenario 4
  - Validation method: Click badge → Sources panel expands → `SourceBrowser` loads correct doc → target chunk highlighted + scrolled. `CitationModal` not opened.
  - Proof target: Manual UI check + `bash scripts/harness/gate-runner.sh pytest frontend/tests/ChatPanel.test.jsx::test_badge_anchors_panel -v`

- [ ] **AC-007** Linked REQ: REQ-007
  - Linked scenario: Scenario 5
  - Validation method: X-Ray Provenance section visible; coverage % matches provenance; claim list clickable; reverse map clickable.
  - Proof target: Manual X-Ray check + `bash scripts/harness/gate-runner.sh pytest frontend/tests/XRayPanel.test.jsx::test_provenance_section -v`

- [ ] **AC-008** Linked REQ: REQ-008
  - Linked scenario: US-003
  - Validation method: `EvaluationService.run_sanity_check` returns `SanityCheckResponse` with `citation_coverage` per case and aggregate.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest backend/tests/chat/test_evaluation.py -v`

- [ ] **AC-009** Linked REQ: REQ-009
  - Linked scenario: SC-008
  - Validation method: Stream turn has `groundedness_score` persisted and returned in SSE `citations` payload.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest backend/tests/chat/test_streaming_groundedness.py -v`

- [ ] **AC-010** Linked REQ: REQ-010
  - Linked scenario: SC-009
  - Validation method: `grep` confirms no citation handling in `Chat.jsx`; `/chat` route renders `ChatPanel` only.
  - Proof target: `bash scripts/harness/gate-runner.sh pytest frontend/tests/ChatScreen.test.jsx -v`

## Related ADRs

- **ADR-001:** Source-to-Answer Provenance Mode (post-gen claim graph + `provenance_json` + coverage; no constrained decoding in v1). See `core-zero/memories/repo/adr-log.md`.

## Notes

- Phase 0 (REQ-009, REQ-010) must complete before Phase 1 (REQ-001–008) to avoid re-touching finalize code.
- All ACs have verification commands; `bash scripts/harness/gate-runner.sh` is the proof mechanism per harness protocol.
- `provenance_json` schema (informal):
  ```json
  {
    "claims": [
      {"index":0,"text":"...","start":0,"end":120,"labels":["1"],"chunks":["chunk-uuid"],"cited":true,"quote_text":"...","match_score":0.72,"match_method":"jaccard"}
    ],
    "coverage": {"cited":2,"total":3,"uncited_indices":[1]}
  }
  ```