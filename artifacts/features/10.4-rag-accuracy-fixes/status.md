# Status: RAG Accuracy Fixes

## Feature ID
`rag-accuracy-fixes`

## Phase
**Plan Approved** (2026-07-10)

## Last Updated
2026-07-10

## Session Notes
- Initial spec creation: 2026-07-10
- Clarify re-entry: 2026-07-10 — reason: mid-implement scope questions from user focus on RAG chat accuracy

## Complexity Classification
Simple / Low risk (targeted patches to existing services)

## Risk Flags
- [ ] Security sensitive (prompt injection, PII)
- [ ] Data migration / schema change
- [ ] Cross-service contract change
- [ ] Breaking API change
- [ ] Performance regression risk

## Scope Summary
Five focused patches to tighten groundedness, citation accuracy, provenance transparency, and conflict detection in document-based chat:

1. **Per-collection similarity config** (config + retrieval)
2. **Grounding: Jaccard pre-filter + LLM score** (grounding.py)
3. **Citation regex + schema** → `[Source <chunk_id>]` (citations.py)
4. **Provenance schema** with match_score + match_method (citations.py)
5. **Conflict score threshold** (conflict.py)

All changes are backward-compatible; no DB migration required.