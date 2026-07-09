<!-- triaged: true, date: 2026-07-10 -->

# Session Extracts — 10.2 Source-to-Answer Provenance

## Pending Candidates

(none — all triaged 2026-07-10)

## Triaged

### EXT-001 — Shared finalize for dual orchestrators
- **Category:** Heuristic
- **Disposition:** promoted → `learned-heuristics.md` LH-011
- **Summary:** Sync (`service.py`) and stream (`streaming.py`) duplicated finalize logic and drifted (groundedness missing on stream). Extract shared `finalize_turn` used by both.

### EXT-002 — Post-gen claim graph over constrained decoding (v1)
- **Category:** Pattern
- **Disposition:** promoted → `domain/rag/patterns.md` + ADR-001 already recorded
- **Summary:** ADR-001: measure claim→chunk graph + coverage first; defer constrained decoding / hard repair.

### EXT-003 — X-Ray / debug UI must not hide behind unset flags
- **Category:** Heuristic
- **Disposition:** promoted → `learned-heuristics.md` LH-012
- **Summary:** `debugMode` toggle lived only on dead `Chat.jsx`; ChatPanel gated X-Ray on unset state. Always expose control or seed trace from SSE/history.

### EXT-004 — Provenance must merge into msg.trace for X-Ray open path
- **Category:** Pattern
- **Disposition:** promoted → `domain/rag/patterns.md`
- **Summary:** Storing provenance only on `debugTrace` leaves per-message X-Ray without Provenance section. Merge into `msg.trace` on citations SSE.

### EXT-005 — Absolute side panels need flex + overflow-y
- **Category:** Heuristic
- **Disposition:** promoted → `learned-heuristics.md` LH-013
- **Summary:** `.xray-panel { position:absolute; inset:0 0 0 auto }` without flex/overflow overflows viewport when Provenance section grows.

### EXT-006 — Injectable deps on shared finalize for tests
- **Category:** Heuristic
- **Disposition:** deferred (recurrence 1)
- **Summary:** `finalize_turn` must accept optional `conflict_service` so integration tests can mock without constructing LLM ConflictDetectionService.

### EXT-007 — pytest.mark.asyncio requires plugin
- **Category:** Harness gap
- **Disposition:** deferred → harness-telemetry note if recurs
- **Summary:** `test_streaming_groundedness.py` uses `@pytest.mark.asyncio` but env lacks pytest-asyncio; tests fail mechanically.

### EXT-008 — Live chat is ChatPanel via WorkspaceLayout, not Chat.jsx
- **Category:** Pattern
- **Disposition:** promoted → `project-knowledge-base.md` note / frontend domain if needed
- **Summary:** App routes `/chat` → WorkspaceLayout → ChatPanel. Chat.jsx is legacy; citation/X-Ray work must target ChatPanel.
