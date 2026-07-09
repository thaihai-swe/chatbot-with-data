# Handoff — 10.2 Source-to-Answer Provenance

**Date:** 2026-07-10  
**Branch:** features/rework-v2 (confirm with `git branch --show-current`)  
**Phase:** Verifying (implementation complete; formal Done blocked on harness-verify)

## What shipped

Claim-level source-to-answer provenance:
- Backend: `split_paragraphs`, `build_provenance`, `finalize_turn`; migration `0007_provenance_json`
- API: SSE `citations.provenance`; `GET /chat/turns/{id}/provenance`
- Frontend: `[unsupported]` display-layer; badge → `setActiveChunkId`; X-Ray Provenance + scroll fix
- Eval: `citation_coverage` on EvalResult / SanityCheckResponse
- ADR-001: post-gen graph, no constrained decoding in v1

## Proof status

- Unit: `pytest backend/tests/chat/test_provenance.py` + citations + migrations + conflict = **41 pass** when asyncio file excluded
- Fail env: `test_streaming_groundedness.py` needs `pytest-asyncio`
- Gate-runner: fails on missing frontend `npm run lint` script

## Blockers for Done

1. Complete `/harness-verify` (or document Pass-with-debt for lint/asyncio)
2. Run `/context-memory` already done for this ship — re-run only if more extracts appear

## Not done / residual

- Constrained decoding / hard citation repair (ADR-001 deferred)
- production-rag-audit next P0: auth + Docker

## Next command

```text
/harness-verify
```

Or start production gate:

```text
/spec-requirements  # authentication + Docker (P0 from production-rag-audit)
```
