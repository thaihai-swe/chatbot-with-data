# Production RAG Audit

## Current Phase: Research Complete

## Complexity: Major

## Intake
- *Input type:* feature_comparison
- *One-line restatement:* Deep-dive comparison of current RAG system vs Google Notebook LM (2026) to identify gaps in RAG pipeline, citation, flow, and UX design.
- *Reasoning:* Existing analysis was outdated — needed fresh codebase survey + Notebook LM feature research to map brownfield gaps for Notebook-LM-like document chat.

## Triggered Domain Packs
- [x] RAG Pipeline — triggered: `rag`, `retrieval`, `generation`, `query`, `citation`, `grounding`, `rerank`, `hybrid search`, `bm25`, `vector search`, `context assembly`, `streaming`
- [x] Frontend UI — triggered: `frontend`, `react`, `ui`, `screen`, `component`, `chat ui`, `x-ray`
- [x] Document Ingestion — triggered: `ingestion`, `document`, `chunking`, `embedding`, `pdf`, `upload`

## Findings (Refreshed 2026-06-30)
- **3-panel layout PARITY** — WorkspaceLayout (Sources + Chat + Studio) matches Notebook LM
- **Knowledge products PARITY** — 6 product types live in StudioPanel
- **Citation NEAR-PARITY** — Dual-strategy quote extraction, but post-hoc regex vs Notebook LM's generation-time enforcement
- **Reranker CRITICAL GAP** — `reranking.py` still uses `model="dummy-reranker"` (sort by similarity_score only)
- **Authentication CRITICAL** — None on any of 9 routers; blocks production
- **Suggested questions MISSING** — Notebook LM greets users with suggestions; we have blank input
- **Knowledge loop MISSING** — No save-to-note feature; Notebook LM feeds saved notes back into source base
- **No monitoring/Docker/CI** — Production blindness persists

## Next Step
Route to `/spec-requirements` for authentication (P0) — the highest-leverage production gate. Then `/spec-plan` for reranker replacement + citation UX upgrade (P1).
