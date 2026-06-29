# Production RAG Audit

## Current Phase: Research Complete

## Complexity: Major

## Intake
- *Input type:* new_spec
- *Risk flags:* none
- *One-line restatement:* Comprehensive comparison of our RAG system against Notebook LM to build a production-ready RAG with restructured UI.
- *Reasoning:* Current system has closed all previously identified gaps but needs a full production-readiness audit and UI/architecture overhaul.

## Triggered Domain Packs
- [x] RAG Pipeline — triggered: `rag`, `retrieval`, `generation`, `query`, `context assembly`, `citation`
- [x] Frontend UI — triggered: `frontend`, `react`, `ui`, `screen`, `component`
- [x] Document Ingestion — triggered: `ingestion`, `document`, `chunking`, `embedding`

## Findings
- **UI structure is the biggest UX gap** - single-column vs Notebook LM's 3-panel (Sources + Chat + Studio)
- **No auth blocks deployment** - critical production blocker
- **Dummy reranker degrades quality** - cross-encoder reranker is highest-leverage RAG improvement
- **Sparse test coverage** - only 21 test cases for the entire chat pipeline; 317-line safety module has 0 tests
- **No monitoring or RAG evaluation** - blind in production

## Next Step
Route to `/spec-requirements` — scope is clear. Phase 1 (auth, reranker, Docker) is unambiguous. The UI panel restructure may benefit from an ADR on layout strategy before requirements.
