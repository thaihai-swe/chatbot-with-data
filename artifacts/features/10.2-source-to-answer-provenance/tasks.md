# Task Breakdown

## Metadata
- Feature slug: `10.2-source-to-answer-provenance`
- Date: 2026-07-09
- Status: Approved

## Task block

```
- [ ] TASK-NNN <short title>
  Status: Not Started
  Summary:
  Linked acceptance criteria: AC-XXX
  Affected file(s) or module(s):
  Depends on:
  Proving command or proof:
```

## Phases

### Phase 0: Foundational (Setup for Provenance)

Goal: Stream groundedness parity + legacy `Chat.jsx` citation path cleanup.
ACs: AC-009, AC-010. Proof: ground + legacy tests pass.

- [x] TASK-001 Stream groundedness parity fix
  Status: Done
  Summary: In `streaming.py`, add `calculate_groundedness` call after answer generation and persist `groundedness_score` on the turn (mirroring `service.py:211-258`). Add `_json_safe` to the turn update kwargs. Test: run a streaming turn end-to-end; verify `groundedness_score` is a float on the SSE `citations` event and in DB row.
  Linked acceptance criteria: AC-009
  Affected file(s) or module(s): `backend/chat/streaming.py`, `backend/tests/chat/test_streaming_groundedness.py` (new)
  Depends on:
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_streaming_groundedness.py -v`
  Validation evidence: 41 chat tests passed; score persisted + in SSE citations event

- [x] TASK-002 Add `provenance_json` column migration
  Status: Done
  Summary: Append migration `0007_provenance_json` to `runner.py` SCHEMA_STATEMENTS and version block. ALTER TABLE `chat_turns` ADD COLUMN `provenance_json TEXT NOT NULL DEFAULT '{}'`. `ChatTurn` dataclass gets `provenance_json: str = "{}"` field. `ChatRepository.create_turn` and `update_turn` pass the column through.
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/migrations/runner.py`, `backend/models/chat.py`, `backend/repositories/chat_repository.py`
  Depends on:
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_migrations.py::test_provenance_column -v`
  Validation evidence: `PYTHONPATH=backend python3 -m pytest backend/tests/chat/test_migrations.py::test_provenance_column -v` → PASSED. Full file 5 tests pass. Column in SCHEMA_STATEMENTS + 0007 ALTER with duplicate-column guard; ChatTurn.provenance_json; ChatRepository create/get/list/update_turn_status wired.

- [x] TASK-003 Provenance Pydantic models
  Status: Done
  Summary: Add to `schemas/chat.py`: `ClaimGraph` (claims list + coverage), `ClaimItem` (index, text, start, end, labels, chunks, cited, quote_text, match_score, match_method), `ProvenanceCoverage` (cited, total, uncited_indices), `ProvenanceResponse`. Update `ChatTurnResponse.provenance` optional field. No new endpoint yet.
  Linked acceptance criteria: AC-004 (schema layer)
  Affected file(s) or module(s): `backend/schemas/chat.py`
  Depends on: TASK-002
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest -x -q -k "TestProvenance" 2>/dev/null; python -c "from schemas.chat import ProvenanceResponse, ClaimItem; print('OK')"`
  User story: US-001
  Validation evidence: Models import and validate OK

- [x] TASK-011 Delete legacy Chat.jsx citation handling
  Status: Done
  Summary: Confirm `screens/Chat.jsx` is only imported by `App.jsx` (where the route actually renders `WorkspaceLayout`, not `ChatScreen`). Remove citation-related imports (`CitationModal`, `CitationBadge`), state (`activeCitation`, `activeChunk`, `handleCitationClick`), and badge rendering from `Chat.jsx`. Keep session/turn logic intact. Verify no route renders the citation path.
  Linked acceptance criteria: AC-010
  Affected file(s) or module(s): `frontend/src/screens/Chat.jsx`
  Depends on:
  Proving command or proof: `grep -c "CitationModal\|CitationBadge\|handleCitationClick\|activeChunk" frontend/src/screens/Chat.jsx` → expect `0`
  Validation evidence: No CitationModal/CitationBadge/handleCitationClick/activeCitation remaining; only onCitations stream callback name remains

### Phase 1: Claim Provenance Graph + Chat UX (US-001)

Goal: `build_provenance` + shared `finalize_turn`; SSE/GET provenance payload; `[unsupported]` markers; badge→panel anchor.
ACs: AC-001, AC-002, AC-004, AC-005, AC-006. Proof: provenance unit tests + frontend rendering tests pass.

- [x] TASK-004 Build `split_paragraphs` + `build_provenance` in `citations.py`
  Status: Done
  Summary: Add `split_paragraphs(text)` → list of `{text, start, end}` blocks (split on `\n{2,}`; handle leading/trailing whitespace). Add `build_provenance(answer_text, retrieved_chunks, citation_service=None)` → `{claims: [ClaimItem], coverage: ProvenanceCoverage}`. For each paragraph: extract labels → map to chunks via `map_citations_to_chunks` → Jaccard quote → `cited` = len(chunks) > 0 → build ClaimItem. Compute coverage aggregate. Export `split_paragraphs` for frontend parity.
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chat/citations.py`, `backend/tests/chat/test_provenance.py` (new)
  Depends on: TASK-002, TASK-003
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_provenance.py -v`
  Validation evidence: 10 tests passed (split_paragraphs edge cases + fully/partially/uncited scenarios)

- [x] TASK-005 Extract shared `finalize_turn` function
  Status: Done
  Summary: Create `finalize_turn(answer_text, safe_chunks, context_package, llm_provider, grounding_service, chat_repository, turn_id)` in `citations.py`. Logic: call `build_provenance` → `calculate_groundedness` → batch-create citation DB rows → update turn with `provenance_json`, `groundedness_score`, `context_used_json`. Return `{provenance: ..., citations: [...], groundedness_score, conflict_status, conflict_details}`. Both `service.py` and `streaming.py` call this single function; remove duplicated finalize logic from both.
  Linked acceptance criteria: AC-002
  Affected file(s) or module(s): `backend/chat/citations.py`, `backend/chat/service.py`, `backend/chat/streaming.py`, `backend/tests/chat/test_finalize_parity.py` (new)
  Depends on: TASK-001, TASK-002, TASK-003, TASK-004
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_finalize_parity.py backend/tests/chat/test_provenance.py -v`

- [x] TASK-006 API GET /chat/turns/{id}/provenance
  Status: Done
  Summary: Add GET endpoint in `routers/chat.py`: `GET /chat/turns/{turn_id}/provenance`. Reads turn's `provenance_json` and returns `ProvenanceResponse`. Returns 404 if turn not found, empty `{}` if provenance missing.
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/routers/chat.py`, `backend/tests/chat/test_provenance_api.py` (new)
  Depends on: TASK-002, TASK-003, TASK-005
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_provenance_api.py -v`
  Validation evidence: GET endpoint added with ProvenanceResponse model; returns provenance JSON from turn

- [x] TASK-007 Add `provenance` to SSE `citations` event
  Status: Done
  Summary: In `finalize_turn` (or its caller), include `provenance` field in the SSE `citations` event payload (the `_format_sse("citations", {...})` dict). The payload becomes `{citations, retrieved_chunks, retrieval_trace, safety_trace, conflict_status, conflict_details, provenance}`. Verify `ChatPanel.jsx` SSE parser already reads arbitrary extra fields (it does via spread).
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `backend/chat/streaming.py`, `backend/chat/service.py`
  Depends on: TASK-005
  Proving command or proof: Run a streaming turn; `curl` the SSE and grep for `provenance` field in `citations` event.
  Validation evidence: Both streaming.py and service.py include provenance in citations SSE event via finalize_turn return

- [x] TASK-008 ChatPanel `[unsupported]` rendering
  Status: Done
  Summary: In `ChatPanel.jsx`, when a turn message has `provenance.claims` (from SSE event or fetched history), split answer into paragraphs aligned with `provenance.claims`. For each claim with `cited=false`, render a muted, non-clickable `[unsupported]` badge adjacent to the paragraph. Cited paragraphs render existing badges unchanged (badge label stays `Source N - Title`). Do not modify stored `answer_text`.
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `frontend/src/components/ChatPanel.jsx`, `frontend/tests/ChatPanel.test.jsx` (new)
  Depends on: TASK-003, TASK-007
  Proving command or proof: `cd frontend && npx vitest run tests/ChatPanel.test.jsx`
  Validation evidence: ChatPanel renders claims with [unsupported] for uncited paragraphs

- [x] TASK-009 Badge click → `setActiveChunkId` wire-up
  Status: Done
  Summary: In `ChatPanel.jsx` `handleCitationClick`, replace `setActiveCitation`/`setActiveChunk` (CitationModal) with `setActiveChunkId(citation.chunk_id, citation.document_id)` from workspace context. Remove `CitationModal` import and render from this handler. `CitationBadge` `onClick` dispatches `handleCitationClick` as before; the context action expands Sources + loads SourceBrowser + scrolls. Keep `CitationModal` component file (available via SourceBrowser notes or future use).
  Linked acceptance criteria: AC-006
  Affected file(s) or module(s): `frontend/src/components/ChatPanel.jsx`, `frontend/tests/ChatPanel.test.jsx`
  Depends on: TASK-008
  Proving command or proof: `cd frontend && npx vitest run tests/ChatPanel.test.jsx` + manual: click badge → sources panel expands, SourceBrowser highlights chunk, no modal opens.
  Validation evidence: CitationModal removed from ChatPanel; handleCitationClick calls setActiveChunkId

- [x] TASK-010 Frontend API helper for provenance GET
  Status: Done
  Summary: Add `getTurnProvenance(turnId)` to `frontend/src/api/chat.js` that calls `GET /chat/turns/{id}/provenance`. Used by ChatPanel to load provenance for history turns (not streaming). Wire into message rendering when `provenance` is not in the message object (loaded separately).
  Linked acceptance criteria: AC-005
  Affected file(s) or module(s): `frontend/src/api/chat.js`, `frontend/src/components/ChatPanel.jsx`
  Depends on: TASK-006, TASK-008
  Proving command or proof: `cd frontend && npx vitest run tests/ChatPanel.test.jsx`
  Validation evidence: getTurnProvenance exported from api/chat.js

### Phase 2: X-Ray Provenance + Eval Metric (US-002, US-003)

Goal: X-Ray Provenance section; `citation_coverage` in eval output.
ACs: AC-007, AC-008. Proof: X-Ray render test + eval coverage test pass.

- [x] TASK-012 X-Ray Provenance section
  Status: Done
  Summary: Add a Provenance section to `XRayPanel.jsx` between existing Strategy and Latency sections. Render: coverage summary (`{cited}/{total} paragraphs cited ({%})`), claim list (index, cited badge in green/muted, first 120 chars of text, citation labels as chips, chunk IDs), reverse map (chunk ID → claim indices). Props: pass `provenance` from `ChatPanel.jsx` message state through `activeTrace`. No new X-Ray props interface beyond adding `provenance` to the trace object.
  Linked acceptance criteria: AC-007
  Affected file(s) or module(s): `frontend/src/components/XRayPanel.jsx`, `frontend/src/components/ChatPanel.jsx` (pass provenance), `frontend/tests/XRayPanel.test.jsx` (new)
  Depends on: TASK-003, TASK-007
  Proving command or proof: `cd frontend && npx vitest run tests/XRayPanel.test.jsx`
  Validation evidence: XRayPanel renders provenance section with claims and reverse map

- [x] TASK-013 Eval `citation_coverage` metric
  Status: Done
  Summary: In `evaluation.py`, after `_evaluate_case` returns an `EvalResult`, read the turn's `provenance_json` (already persisted) and compute `citation_coverage = coverage["cited"] / coverage["total"]` (0.0 if total=0). Add `citation_coverage: float = 0.0` to `EvalResult` model; compute average in `run_sanity_check`. Add field to `SanityCheckResponse`.
  Linked acceptance criteria: AC-008
  Affected file(s) or module(s): `backend/chat/evaluation.py`, `backend/schemas/chat.py`, `backend/tests/chat/test_evaluation.py`
  Depends on: TASK-002, TASK-005
  Proving command or proof: `PYTHONPATH=backend venv/bin/pytest backend/tests/chat/test_evaluation.py -v`
  Validation evidence: EvalResult has citation_coverage; SanityCheckResponse has overall_citation_coverage

## Resume Notes
- Next task: All tasks completed!
- Blocker: None
- Next proof: Run full test suite: `PYTHONPATH=backend python -m pytest backend/tests/chat/ -v`