# Progress: 10.2 Source-to-Answer Provenance

## 2026-07-09 Implementation

### Phase 0
- TASK-001: Stream groundedness parity — DONE (streaming.py calculates + persists score)
- TASK-002: provenance_json column migration 0007 — DONE
- TASK-011: Delete Chat.jsx citation handling — DONE

### Phase 1
- TASK-003: Pydantic models (ClaimItem, ProvenanceCoverage, ProvenanceResponse) — DONE
- TASK-004: split_paragraphs + build_provenance — DONE (10 unit tests pass)
- TASK-005: Shared finalize_turn — DONE (wired into service.py + streaming.py)
- TASK-006: GET /chat/turns/{id}/provenance — DONE
- TASK-007: SSE citations event includes provenance — DONE
- TASK-008: ChatPanel [unsupported] display-layer — DONE
- TASK-009: Badge click → setActiveChunkId (no modal) — DONE
- TASK-010: getTurnProvenance API helper — DONE

### Phase 2
- TASK-012: XRayPanel Provenance section — DONE
- TASK-013: Eval citation_coverage metric — DONE

### Notes
- Streaming groundedness tests use pytest.mark.asyncio but pytest-asyncio not installed — known env gap, not feature regression
- Chat.jsx still imported in App.jsx but unused by routes (WorkspaceLayout is the active path)

## 2026-07-10 Session END + context-memory

### UX follow-ups shipped in session
- Header X-Ray always clickable; seed debugTrace from SSE citations + history
- Merge provenance into msg.trace so X-Ray Provenance section appears
- X-Ray panel scrollable (flex column + overflow-y)

### Audit refresh
- `artifacts/features/production-rag-audit/analysis.md` refreshed for July ship set (7.0, 9.0, 10.2, eval/studio)

### context-memory (post-ship)
- Triaged session-extracts → LH-011, LH-012, LH-013; rag patterns + glossary; PKB paths
- Feature phase still **Verifying** (harness-verify incomplete: npm lint missing; asyncio tests)

### Next command
`/harness-verify` after fixing gate-runner lint script and/or pytest-asyncio, or continue with P0 auth from refreshed audit.
