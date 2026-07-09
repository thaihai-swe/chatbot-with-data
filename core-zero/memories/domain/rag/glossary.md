---
domain: rag
triggers: [rag, retrieval, generation, rerank, hybrid search, bm25, vector search, query, context assembly, streaming, citation, grounding, candidate merger, rrf, safety, prompt injection]
---

# RAG Pipeline — Glossary

> **Ownership:** Collaborative — skill-updated + user-maintained.
> **Updated by:** `/context-memory` post-ship sync when new terms emerge from a completed feature.
> **Read by:** `/spec-requirements`, `/spec-plan`, `/spec-implement` to enforce consistent naming.

## Ubiquitous Language

| Term | Definition | Source |
|------|------------|--------|
| Query Intelligence | Pre-retrieval pipeline: intent classification, query expansion, HyDE (Hypothetical Document Embedding), query decomposition, synonym expansion, dynamic collection routing | `backend/chat/query_intelligence.py` |
| Hybrid Search | Combined BM25 keyword search + semantic vector search fused via RRF (Reciprocal Rank Fusion) | `backend/chat/retrieval.py` |
| CandidateMerger | RRF-based combiner of multi-strategy retrieval results (BM25 + semantic + optional HyDE) | `backend/chat/retrieval.py` |
| Reranker | Cross-encoder or LLM-based reranking of retrieved chunks before context assembly | `backend/chat/reranking.py` |
| Context Assembly | Builds the LLM prompt from retrieved chunks, respecting token limits | `backend/chat/context_assembly.py` |
| Grounded Generation | Generates answers with evidence sufficiency scoring + groundedness checking + citation extraction | `backend/chat/generation.py` |
| Prompt Injection Defense | 3-layer protection: heuristic scanner (49 regex patterns) → fuzzy scanner (cosine similarity) → LLM scanner | `backend/chat/safety.py` |
| X-Ray Panel | Frontend debug panel showing safety, provenance claim graph, retrieval transformations, strategy, latency | `frontend/src/components/XRayPanel.jsx` |
| Collection Routing | LLM-routed selection of which document collections to search based on user query intent | `backend/chat/query_intelligence.py` |
| SSE Streaming | Server-Sent Events for real-time token streaming from LLM to frontend | `backend/chat/streaming.py` |
| Claim Provenance Graph | Post-generation map of answer paragraphs → citation labels → chunk IDs with coverage stats | `backend/chat/citations.py` `build_provenance` |
| Provenance Coverage | Aggregate `cited/total` paragraph counts plus `uncited_indices` for a turn | `provenance_json.coverage` on `chat_turns` |
| finalize_turn | Shared post-generation helper: provenance + groundedness + citations + conflict + persist | `backend/chat/citations.py` |
| Display-layer unsupported | UI marker `[unsupported]` for uncited paragraphs without mutating stored `answer_text` | `ChatPanel.jsx` + `provenance.claims` |
| Citation Coverage (eval) | Eval metric: fraction of paragraphs with resolved citations | `EvalResult.citation_coverage` |
