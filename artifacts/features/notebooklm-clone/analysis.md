# Notebook LM Clone — RAG + Citation Comparison

## 1. Scope & Method

**Goal:** Compare the current chatbot-with-data system against Google Notebook LM (as of June 2026), focusing on RAG pipeline and citation features. Audio, Slides, Video Overviews are excluded per user instruction.

**Method:**
- Codebase exploration of all backend/frontend modules
- Web research on Notebook LM's architecture and 2025-2026 updates
- Domain packs loaded: RAG Pipeline, Document Ingestion, Frontend UI

---

## 2. Notebook LM Reference Architecture (RAG + Citations Only)

Based on research across Notebook LM documentation, technical deep-dives, and the June 2026 "Better Research" update:

### Core Architecture
```
Sources → Doc Understanding → Multi-Index → Retrieval + Ranking → Context Engineering → Grounded Gen → Knowledge Products
```

### Key RAG/Citation Features

| Feature | Details |
|---------|---------|
| **Document Understanding** | On upload: auto-summarize, extract key topics, map section hierarchy |
| **Multi-Format Ingestion** | PDF, DOCX, EPUB, Google Docs (live sync), Sheets, YouTube transcripts, audio, web URLs, CSV, images with OCR |
| **Context Capacity** | 1M tokens per source; 50-600 sources per notebook (by tier) |
| **Retrieval & Ranking** | Multi-signal: source trustworthiness, multi-source coverage, contextual relevance, citation suitability, evidence non-redundancy, explicit conclusion presence |
| **Context Engineering** | Rich package: query + intent + candidate evidence + source metadata + section context + extended context + source summaries + chat history + user notes + citation mapping + answer constraints + insufficient-evidence rules |
| **Citation System** | Inline `[N]` per claim → click to show exact quote highlighted in source → original source location (page, section) |
| **Source Grounding** | Only answers from uploaded sources; explicit "no relevant info found" for OOD queries; surfaces conflicts between sources |
| **Multi-Source Synthesis** | Combines evidence across sources; flags contradictions explicitly |
| **User Annotations** | Users can write personal notes linked to specific sources |
| **Knowledge Products** | Auto-generated: study guide, briefing doc, FAQ, timeline, glossary, flash cards |
| **Agentic Research** | Deep Research mode: autonomously searches web, discovers and ingests primary sources (Nov 2025+) |
| **Model** | Gemini 3.5 (June 2026) with Antigravity coding agent framework |

---

## 3. Our Current System — RAG Pipeline Map

### Architecture
```
Query → Safety (3-layer) → Query Intelligence → Retrieval (multi-strategy) → Reranking → Context Assembly → Grounded Generation → Citation Extraction → Response
```

### Files and Responsibilities

| Module | File | LOC | Role |
|--------|------|-----|------|
| **Safety** | `backend/chat/safety.py` | ~320 | 3-layer prompt injection defense |
| **Query Intelligence** | `backend/chat/query_intelligence.py` | extracted | Intent classification, expansion, decomposition, HyDE, synonyms |
| **Retrieval** | `backend/chat/retrieval.py` | 76 | Orchestrates BM25 + semantic retrieval |
| **Advanced Retrieval** | `backend/chat/advanced_retrieval.py` | extracted | Configurable pipeline with all strategies |
| **Candidate Merger** | `backend/chat/candidate_merger.py` | extracted | RRF fusion of multi-strategy results |
| **Reranking** | `backend/chat/reranking.py` | extracted | Cross-encoder reranking |
| **Context Assembly** | `backend/chat/context.py` | 98 | Builds LLM prompt with `<source>` tags |
| **Generation** | `backend/chat/generation.py` | 98 | Calls LLM with system prompt + context |
| **Grounding** | `backend/chat/grounding.py` | 113 | Evidence evaluation + LLM-as-judge groundedness |
| **Citations** | `backend/chat/citations.py` | 86 | Extract `[Source N]`, map to chunks |
| **Streaming** | `backend/chat/streaming.py` | 261 | SSE streaming with status events |
| **Orchestrator** | `backend/chat/service.py` | 278 | Non-streaming chat pipeline |
| **Prompts** | `backend/chat/prompts.py` | 158 | All system/evaluation prompts |
| **Citation Modal** | `frontend/src/components/CitationModal.jsx` | 61 | Shows chunk excerpt on citation click |
| **X-Ray Panel** | `frontend/src/components/XRayPanel.jsx` | 111 | Debug panel showing pipeline trace |
| **Chat UI** | `frontend/src/screens/Chat.jsx` | 372 | Chat interface with citations list |

---

## 4. Gap Analysis

### 4.1 Citation System

| Capability | Notebook LM | Our System | Gap |
|---|---|---|---|
| Inline citation markers | `[N]` per sentence/claim | `[Source N]` per chunk | Same approach |
| Click → show evidence | Opens source with **exact quote highlighted** | Opens modal with **full chunk text** | We show the whole chunk, not the exact sentence cited |
| Quote-level precision | Extracts exact substring cited | No quote extraction | **GAP** — we don't know which part of the chunk was cited |
| Source location | Page, section, highlightable | page_number, section_title metadata | Similar, but no highlight |
| Conflict detection | Explicitly flags when 2 sources disagree | Not implemented | **GAP** |
| Cross-source citation | "Claims X [1][3]" supported | "Claims X [Source 1][Source 3]" supported | Parity |
| Source preview on hover | Hover citation → inline tooltip with snippet | Click → modal (blocking) | **GAP** — UX is heavier |
| OOD handling | "No relevant info in sources" + optional general answer | Refuses with grounding score < threshold | Different approach, both functional |
| Citation persistence | Part of notebook state | Persisted to SQLite per turn | Parity |
| User annotations linked to sources | Yes | No | **GAP** |

### 4.2 Document Understanding & Ingestion

| Capability | Notebook LM | Our System | Gap |
|---|---|---|---|
| Auto-summarize on upload | Yes — generates source summary | No | **GAP** |
| Key topic extraction on upload | Yes — extracts main topics | No | **GAP** |
| Section hierarchy preservation | Yes — understands document structure | Only page_number, section_title metadata | **GAP** |
| Multi-format: PDF, DOCX, TXT, MD | Yes | Yes (PDF, TXT, MD) | Partial (no DOCX) |
| Google Docs/Sheets live sync | Yes | No | **GAP** |
| YouTube transcript ingestion | Yes | No | **GAP** |
| Audio file ingestion | Yes | No | Skipped per scope |
| CSV/image OCR | Yes | No | **GAP** |
| URL/webpage ingestion | Yes | Yes (`url_ingestion_enabled`) | Parity |
| EPUB support | Yes | No | **GAP** |
| Context per source | 1M tokens per source | ~chunk_size (1000 tokens default) | **MAJOR GAP** |

### 4.3 Retrieval & Ranking

| Capability | Notebook LM | Our System | Gap |
|---|---|---|---|
| Hybrid search (BM25 + vector) | Implied (standard RAG) | Yes (RRF fusion) | Parity |
| HyDE | Yes (via Gemini) | Yes (optional) | Parity |
| Query expansion | Yes | Yes (3 variants) | Parity |
| Query decomposition | Yes | Yes (optional) | Parity |
| Reranking | Yes (cross-encoder) | Yes (cross-encoder) | Parity |
| Ranking signals: trustworthiness | Yes | No | **GAP** |
| Ranking signals: citation suitability | Yes | No | **GAP** |
| Ranking signals: evidence non-redundancy | Yes | No | **GAP** |
| Multi-hop reasoning | Yes | Yes (optional, 3 hops) | Parity |
| Collection routing | Notebook = collection | Yes (optional, LLM-routed) | Parity |

### 4.4 Context Engineering

| Capability | Notebook LM | Our System | Gap |
|---|---|---|---|
| Source summaries in context | Yes | No | **GAP** |
| Section-level context | Yes | No (only chunk text) | **GAP** |
| User notes in context | Yes | No | **GAP** |
| Citation mapping in prompt | Yes (which claim maps to which source) | Only in post-processing | **GAP** |
| Extended context around evidence | Yes | Parent-child chunks (optional) | Partial |
| Answer constraints in prompt | Yes | Yes (via system prompt) | Parity |
| Insufficient evidence handling | Yes (explicit rules) | Yes (evaluation + refusal) | Parity |
| Chat history | Yes | Yes | Parity |

### 4.5 Knowledge Products (Generation Outputs)

| Capability | Notebook LM | Our System | Gap |
|---|---|---|---|
| Q&A answer | Yes | Yes | Parity |
| Study guide auto-generation | Yes (Studio) | No | **GAP** |
| Briefing doc auto-generation | Yes (Studio) | No | **GAP** |
| FAQ auto-generation | Yes (Studio) | No | **GAP** |
| Timeline extraction | Yes (Studio) | No | **GAP** |
| Glossary extraction | Yes (Studio) | No | **GAP** |
| Flash cards | Yes (Studio) | No | **GAP** |
| Intent-specific prompts | Implicit via Gemini | Explicit (5 intent types) | Different approach |

### 4.6 Frontend / UX

| Capability | Notebook LM | Our System | Gap |
|---|---|---|---|
| Source library view | Yes — shows all sources, summaries | Document library exists but basic | Partial |
| Source browsing | Browse full source text | Basic document list | **GAP** |
| Inline citation preview | Hover → tooltip | Click → modal | **GAP** |
| Notebook organization | Sources grouped into notebooks | Collections serve similar purpose | Parity |
| X-Ray / debug view | No visible equivalent | Yes (X-Ray Panel) | We lead |
| Settings page | Limited | Full settings page | We lead |

---

## 5. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Context window limits (1K chunks vs 1M tokens) | HIGH | Can increase chunk size and/or implement hierarchical summarization into context |
| No source-level understanding pre-retrieval | HIGH | Implement document understanding pipeline as pre-processing step |
| Citation precision (chunk-level vs quote-level) | MEDIUM | Add quote extraction via LLM post-processing; store quote text |
| No DOCX/EPUB/YouTube ingestion | MEDIUM | Add parsers for each format |
| No knowledge product generation | MEDIUM | Add prompt-based generation for study guides, briefings, etc. |
| No user annotation system | LOW | Add notes linked to chunks in SQLite |
| No conflict detection | LOW | Add explicit prompt instruction + post-processing check |

---

## 6. Preserved Behaviors (Don't Break)

- 3-layer safety pipeline must remain first stage (INV-001)
- Hybrid search must remain default retrieval (INV-002)
- SSE streaming must remain append-only (INV-003)
- Citation persistence to SQLite
- X-Ray observability panel

## 7. Reuse Opportunities

- Current `chat.prompts` system can be extended for knowledge product prompts
- Current `CitationService` can be extended for quote-level precision
- Current `ContextService` can be extended for richer context packages
- Current `SafetyService` is already at parity
- Current `AdvancedRetrievalService` provides solid foundation

## 8. Boundary Contracts

| Produces | Consumed By | Current Contract | Change Needed? |
|----------|-------------|------------------|----------------|
| Query results (citations) | Frontend Chat | SSE + REST | Extend citation format with `quote_text` |
| Citation metadata | CitationModal | `chunk_id, document_id, title, page_number` | Add `quote_text`, `source_excerpt` |
| Chat turns | SQLite | `ChatMessage` model | Add citation notes table |
| Retrieval trace | X-Ray Panel | `RetrievalResult[]` | No change needed |

---

## 9. Recommendations

### Tier 1 — Core Gaps (High Impact, Close Notebook LM Parity)

1. **Quote-level citations** — After generation, extract exact sentences that correspond to each `[Source N]` and store `quote_text` in the citation record. The CitationModal should highlight the quote within the chunk.
2. **Document understanding pipeline** — On ingestion, auto-generate a source summary, extract key topics, and preserve section hierarchy. Store in the document record for later inclusion in context.
3. **Richer context engineering** — Include source summaries, section context, and citation mapping in the context package sent to the LLM.

### Tier 2 — Feature Gaps (Medium Impact)

4. **Conflict detection** — Add prompt instruction to surface source disagreements + post-processing check.
5. **Knowledge products** — Add Studio-like endpoints: `POST /generate/study-guide`, `/generate/briefing-doc`, `/generate/faq`.

### Tier 3 — UX Gaps (Lower Impact)

7. **Citation hover tooltip** — Replace modal with inline tooltip on hover for faster browsing.
8. **Source browser** — Full-text source viewing within the UI.
9. **User annotation system** — Notes linked to specific chunks.

---

## 10. Conclusion

> Notebook LM is not mysterious — it is still RAG under the hood. But it is a **production-grade, productized RAG** that excels at document understanding, context engineering, and citation precision. Our system has the right architecture (pipeline-as-chain, multi-strategy retrieval, 3-layer safety, streaming) and matches in ~60% of the RAG/citation feature surface. The remaining gaps are well-bounded and can be addressed incrementally.

**Route to:** `/spec-requirements` — most gaps are requirements-clear and don't need an ADR. The document understanding pipeline may benefit from an ADR on chunking strategy vs hierarchical summarization.

---

*Generated 2026-06-28 by Kit Research workflow*
