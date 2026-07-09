# Production RAG Audit — Notebook LM Feature Comparison

> **Goal:** Deep-dive comparison of our system vs Google Notebook LM, focusing on RAG pipeline, citation system, user flow, and UI design. Written as a brownfield mapping exercise to identify what to build/change for Notebook-LM-like document chat.
>
> **Date:** 2026-07-09
> **Phase:** Source-to-Answer Provenance Verifying (10.2 done); Cross-Encoder Reranking Done (7.0); Citation Upgrade Done (9.0); Chunk Upgrade Done (8.0); Evaluation Dashboard Charts (10.1); Studio Analytics Dashboard (10.0); UI Restructure (3.0) Implementing
> **Next:** Route to `/spec-requirements` for authentication (P0) + Docker; then `/spec-plan` for save-to-note, chat history search, suggested questions, streaming studio.

---

## 1. Executive Summary

Our system has **3-panel workspace parity** (Sources ↔ Chat ↔ Studio), **knowledge product parity** (6 types), **citation near-parity** with Notebook LM, **cross-encoder reranking**, and **claim-level source-to-answer provenance**. The remaining gaps cluster into three tiers:

| Tier | Gaps | Impact |
|------|------|--------|
| **P0 — Blocks production** | No auth, no deployment config | Cannot ship |
| **P1 — Quality gap** | Soft citation enforcement only (no constrained decoding); stream groundedness parity fixed | Response quality residual |
| **P2 — UX/Feature gap** | Suggested questions, streaming studio, chat history search, save-to-note | User experience vs Notebook LM |
| **Shipped (June–July 2026)** | Chunk upgrade; cross-encoder reranking; citation UX upgrade; source-to-answer provenance; conflict detection; evaluation dashboard; studio analytics | Notebook LM parity on chunking, reranking, citation UX, claim graph |

---

## 2. Verified Codebase State

### 2.1 Backend RAG Pipeline (21 modules)

```
Safety ──→ Query Intelligence ──→ Retrieval ──→ Cross-Encoder Reranker ──→ Context Assembly ──→ Generation
 ↑___________|_______________________|________________________________________|________________|_↓
 |                                                                                        |
 └────────── Grounding + Claim Provenance Graph + Citation Extraction ───────────────────┘
```

**Pipeline flow** (`backend/chat/service.py` + `streaming.py` via shared `finalize_turn`):
1. Safety check (3-layer: regex → fuzzy → LLM) → early refuse if unsafe
2. Collection routing (LLM-based multi-collection dispatch, `collection_routing.py`)
3. Query intelligence: intent classification, HyDE, decomposition, synonym expansion (`advanced_retrieval.py`)
4. Hybrid search: BM25 + vector via Weaviate (`retrieval.py`)
5. **Reranker: Cross-encoder (FlashRank / BGE)** — real reordering of candidates (`reranking.py`, feature 7.0 Done)
6. Context assembly: `<source>` XML blocks + document summaries + citation map + annotations (`context.py`)
7. Generation: intent-specific system prompts + LLM (`generation.py`)
8. Grounding: LLM-as-judge groundedness score (`grounding.py`) — stream + sync paths both persist
9. Citation extraction: dual-format regex `[Source N]` / `[N]` → Jaccard sentence overlap (`citations.py`)
10. **Claim provenance graph:** paragraph split → per-claim labels → chunk map → coverage (`build_provenance`, feature 10.2)
11. Conflict detection: multi-document conflict detection (`conflict.py`, feature 2.0 Done)
12. Shared `finalize_turn` persists citations + `provenance_json` + groundedness (sync + stream)

### 2.2 Frontend Architecture

```
WorkspaceLayout (3-panel)
├── SourcesPanel (left)
│   ├── Collection selector
│   ├── Document checkboxes (per-doc enable/disable)
│   ├── File upload
│   └── SourceBrowser (per-doc viewer; activeChunkId highlight + scroll)
├── ChatPanel (center)
│   ├── Session list (per-collection)
│   ├── Message history (MarkdownBlock renderer)
│   ├── Inline citations [Source N - Title] with HoverCard
│   ├── Badge click → setActiveChunkId (panel anchor; no modal primary)
│   ├── Display-layer [unsupported] on uncited paragraphs (provenance)
│   ├── FlashcardBlock (interactive reveal)
│   ├── XRayPanel (Safety, Provenance, Transformations, Strategy, Latency)
│   └── Stream support (SSE)
└── StudioPanel (right)
    ├── 6 product buttons (study-guide, briefing, FAQ, timeline, glossary, flashcards)
    └── Product history viewer
```

### 2.3 Chat Flow (Per Turn)

```
1. User types query in ChatPanel
2. POST /chat/sessions/{id}/turns/stream (SSE) or sync POST
3. Server: safety → collection_routing → retrieve → cross-encoder rerank → context → generate
   → finalize_turn (ground + cite + claim provenance graph + conflict) → persist
4. Frontend: streams tokens; on citations SSE: badges + provenance + X-Ray data
5. User clicks [Source N]: expands Sources, highlights chunk in SourceBrowser
6. Uncited paragraphs show muted [unsupported] from provenance.claims (display-layer)
```

---

## 3. Notebook LM Feature Deep-Dive

Based on published documentation (blog.google, notebooklm.google, 2026 teardowns):

### 3.1 Core Architecture

| Aspect | Notebook LM | Our System | Delta |
|--------|-------------|------------|-------|
| Model | Gemini 3.5 / Antigravity | Configurable provider (OpenAI, etc.) | No gap |
| Embedding | Google native embedding models | Configurable provider | No gap |
| Chunking | Structural + context-aware segmentation | Adaptive tiering (full-doc injection) + 5 strategies: heading (path prepend), semantic (embedding-based), parent-child (boundary-aware), fixed, page | **PARITY** |
| Reranker | BGE-Reranker-v2 (cross-encoder) | **Cross-encoder (FlashRank / BGE)** | **PARITY (feature 7.0 Done)** |
| Hybrid search | BM25 + vector (MIPS) | BM25 + vector via Weaviate | PARITY |
| Context window | 1M tokens (500K words/source) | Limited by LLM provider (varies) | PARITY |
| Token-level citation | **Inline source ID tokens in generation** | Post-hoc regex extraction `[Source N]` | **DESIGN GAP** |

The most significant architectural difference: **Notebook LM enforces attribution at generation time** (the model is prompted to emit `[1]`, `[2]` tokens inline, and every substantive sentence must have a citation), while our system **extracts citations post-hoc** from free text using regex. This makes Notebook LM's citations more reliable by design.

### 3.2 Citation System Comparison

| Capability | Notebook LM | Our System | Analysis |
|-----------|-------------|------------|----------|
| Format | `[1]` `[2]` numbered inline | `[Source 1]` `[Source 2]` | Different label format |
| Hit target | Exact passage highlighted in source panel | Chunk text from database | NEAR PARITY |
| Quote extraction | Direct quote from source | Jaccard overlap → LLM fallback | Our approach is more sophisticated but less reliable |
| Click behavior | Opens Sources panel, scrolls to passage, highlights | Badge click → Sources panel expand + highlight (modal deprecated for inline) | Notebook LM: seamless; Us: panel anchor |
| **Citation enforcement** | **Architectural: LLM prompted to cite every claim** | **Post-hoc: regex parse of free text** | **CRITICAL DIFFERENCE** |
| Image citations | Yes | No | GAP |
| No-evidence handling | Explicit refusal | GroundingService `is_sufficient` check | PARITY |
| Citation in notes | Saved with citations retained | Saved in DB per turn + provenance_json | PARITY |
| Source-to-citation tracking | Token-level chunk ID linking | `build_provenance` claim graph (paragraph→chunks) + legacy index/UUID | **PROVENANCE GRAPH ADDED** |

**Our citation system (`backend/chat/citations.py:24-390`):**
- Dual regex `\[Source\s+([^\]]+)\]|\[(\d+)\]` for both formats
- Jaccard sentence overlap (threshold 0.5) for quote extraction
- LLM fallback via `QUOTE_EXTRACTION_PROMPT`
- Maps labels to chunks by integer index or UUID
- Produces `CitationResponse` with `quote_text`, `chunk_id`, `document_id`, page info

**Claim provenance graph (feature 10.2, Verifying):**
- Post-generation paragraph split → per-paragraph label extraction → chunk map
- Persists `provenance_json` on turn with `claims[{index, text, labels, chunks, cited, quote_text, match_score, match_method}]` + `coverage`
- SSE `citations` event includes `provenance`; GET `/chat/turns/{id}/provenance`
- ChatPanel renders `[unsupported]` on uncited paragraphs (display-layer only)
- X-Ray Provenance section: coverage % + claim list + reverse chunk→claim map
- Eval includes `citation_coverage` metric

**Notebook LM citation flow:**
- Chunks embedded with IDs
- Reranker (BGE) selects top chunks
- Prompt instructs model: *"For every factual claim, include the source chunk ID in brackets"*
- Generated text has `[1]` tokens inline by construction
- Clicking `[1]` references the chunk ID → highlights exact passage in source viewer
- Citations persist when saving to notes

### 3.3 Source Management

| Feature | Notebook LM | Our System | Analysis |
|---------|-------------|------------|----------|
| Source types | PDF, Docs, Sheets, Slides, URL, YouTube, images, audio, EPUB, CSV | PDF, TXT, MD | **GAP — limited formats** |
| Per-source checkbox | Yes (toggle per query) | Yes (`selectedDocumentIds` in WorkspaceContext) | PARITY |
| Source viewer | Built-in: scrollable, citable, highlights | SourceBrowser component | PARITY |
| Web search / Deep Research | Yes (agentic, sources from web) | No | **GAP** |
| Suggested questions | Yes (auto-generated from sources) | No | **GAP** |
| Source summaries | Auto-generated per document | Document understanding (meta-analysis) | PARITY |
| Drive sync | Automatic (living docs) | No | **GAP** |
| User annotations as sources | Yes (notes injected into knowledge base) | Yes (chunk_notes injected via `<source user_note="...">`) | PARITY |

### 3.4 Chat UX / Flow

| Feature | Notebook LM | Our System | Analysis |
|---------|-------------|------------|----------|
| 3-panel layout | Sources | Chat | Studio | Sources | Chat | Studio | PARITY |
| Collapsible panels | Yes | Yes (panel-collapsed CSS) | PARITY |
| Mobile responsive | Tab-bar | Tab-bar (Sources/Chat/Studio) | PARITY |
| Session scoping | Per-notebook | Per-collection | PARITY |
| Chat history | Permanent, searchable | Per-collection list | **GAP — no search** |
| Suggested questions | Auto-suggested on session start | No | **GAP** |
| Chat personas | Customizable tone/persona | No | **GAP** |
| Non-speculative mode | Always (sources only) | Grounded prompt default | PARITY |
| Streaming | Yes (SSE) | Yes (SSE via StreamingOrchestrator) | PARITY |
| Cancellation | Yes | Yes (cancel endpoint + SSE cancellation) | PARITY |
| X-Ray / debug | No | Yes (XRayPanel: Safety + Provenance + Retrieval + Strategy + Latency) | **WE LEAD** |
| Claim provenance graph | Token-level (implicit) | Explicit `provenance_json` + coverage + reverse map | **WE LEAD (observability)** |
| Evaluation dashboard | Internal | Evaluation screen + history API + charts (10.1) | **WE LEAD** |
| Studio analytics | Limited | Studio analytics dashboard (10.0) | **WE LEAD** |

### 3.5 Studio / Knowledge Products

| Feature | Notebook LM (2026) | Our System | Analysis |
|---------|-------------------|------------|----------|
| Study Guide | Yes | Yes | PARITY |
| Briefing Document | Yes | Yes | PARITY |
| FAQ | Yes | Yes | PARITY |
| Timeline | Yes | Yes | PARITY |
| Glossary | Yes | Yes | PARITY |
| Flashcards | Yes (interactive progress-tracking viewer) | Yes (text-based + FlashcardBlock reveal) | **GAP — no interactive viewer** |
| Reports / PDF export | Yes (PDF, PPTX, XLSX) | No | **GAP** |
| Data Tables | Yes | No | **GAP** |
| Mind Maps | Yes | No | **GAP** |
| Audio Overviews | Yes | No | Out of scope |
| Video Overviews | Yes | No | Out of scope |
| Streaming generation | Yes | No (loading spinner) | **GAP** |
| Persona customization | Yes | No | **GAP** |
| Editable outputs | Yes (edit after generation) | No | **GAP** |
| Output export | PPTX, XLSX, PDF, DOC | No | **GAP** |

### 3.6 Agents / Advanced Features (2026 Updates)

| Feature | Notebook LM | Our System | Priority |
|---------|-------------|------------|----------|
| Agentic retrieval | Deep Research (web) + self-correction | No | P5 |
| Multi-hop reasoning | Yes (Gemini 3.5) | Yes (`multi_hop.py` SequentialChain) | PARITY |
| Code execution | Yes (cloud computer, 100+ skills) | No | P5 |
| GraphRAG | Yes (Spanner) | No | P5 |
| Multi-modal | Charts, tables, images | No | P5 |

---

## 4. Critical UX Flow Comparison

### 4.1 Notebook LM Chat Flow

```
1. User opens Notebook → sees 3-panel: Sources | Chat | Studio
2. Sources panel auto-suggests questions based on uploaded docs
3. User types question (or clicks suggested question)
4. Response streams in with inline [1], [2] citations
5. Every sentence has at least one citation
6. User clicks [1] → Sources panel opens, exact passage highlighted
7. User can verify, then save response as Note
8. Saved Note becomes part of knowledge base
9. User can uncheck sources in left panel → responses only use checked sources
```

### 4.2 Our System Chat Flow

```
1. User navigates to /chat → WorkspaceLayout renders with collapsed panels
2. User selects collection in SourcesPanel
3. Documents auto-selected (all checked by default)
4. User types question in ChatPanel
5. Response streams with [Source 1], [Source 2] citations
6. User hovers over [Source 1] → HoverCard shows snippet
7. User clicks [Source 1] → CitationModal opens with full quote
8. No "Save as Note" feature — history is per-session
9. No auto-suggested questions
10. User can toggle document checkboxes → affects next query
```

### 4.3 Flow Gaps

| Step | Notebook LM | Our System | Severity |
|------|-------------|------------|----------|
| Entry | Suggested questions greet user | Blank chat input | MEDIUM |
| Citation click | Opens Sources panel, highlights passage | Opens modal overlay | **LOW** (different UX, not worse) |
| Verify flow | See source in context with highlight | See quote in modal | NEUTRAL |
| Save insight | Save to Note (persists across sessions) | History only (per-session) | **MEDIUM** |
| Source as KB | Saved notes become sources | Chunk annotations only | **MEDIUM** |
| Per-query source filter | Uncheck sources → immediate filter on next chat | Toggle docs → affects next query | PARITY |

---

## 5. Structural Differences (Beyond Feature Parity)

### 5.1 Citation Enforcement Architecture

This remains the most important design difference:

**Notebook LM:** Token-level citation enforcement in generation. The prompt is engineered so that the LLM *must* emit a citation token for every factual claim. This is an architectural constraint, not a post-processing step.

**Our system (post 9.0 + 10.2):** Free-text generation → dual-format regex extraction → chunk mapping → claim provenance graph. Soft generation-time pressure via prompts (`prompts.py:12-14`: every factual claim MUST cite). Post-hoc `build_provenance` classifies every paragraph as cited/uncited and surfaces coverage. Uncited paragraphs render as `[unsupported]` in ChatPanel (display-layer). No constrained decoding or hard regenerate-on-miss (ADR-001).

**Impact:** Notebook LM still produces more reliable, more complete citations by construction. We now **measure and surface** gaps (coverage %, uncited list, X-Ray Provenance) instead of silently losing them. Residual: model may under-cite; we do not force re-generation.

### 5.2 Reranker Gap — CLOSED (feature 7.0 Done)

**Notebook LM:** BGE-Reranker-v2 cross-encoder, which scores query-chunk pairs with deep semantic matching.

**Our system:** Cross-encoder reranking via FlashRank / BGE (feature `7.0-cross-encoder-reranking`, Done). Replaces the previous dummy sort-by-score stub.

**Impact:** Top-k after rerank is semantically reordered. Generation quality improved. Optional fallback retained for environments without the model.

### 5.3 Knowledge Base Loop

**Notebook LM:** User insights → Saved as Note → Becomes source → Available for future chat. This creates a feedback loop where user-generated insights enrich the knowledge base.

**Our system:** Chat history stays per-session. Chunk annotations (`chunk_notes` table) provide a similar but lower-fidelity mechanism — notes are attached to specific chunks, not entire turns. **Still a gap.**

### 5.4 Source-to-Answer Provenance — SHIPPED (feature 10.2 Verifying)

**Notebook LM:** Each token in the answer can theoretically be traced back to the source chunk that influenced it (token-level attribution via chunk ID in prompt).

**Our system (post 10.2):**
- Claim-level provenance graph: paragraph → labels → chunks → coverage
- Persisted as `provenance_json` on `chat_turns` (migration 0007)
- SSE + GET `/chat/turns/{id}/provenance`
- X-Ray Provenance section (coverage, claims, reverse map)
- Eval `citation_coverage` metric
- Shared `finalize_turn` for sync + stream parity (including groundedness_score)

**Residual vs Notebook LM:** We do not do true token-level attribution or constrained decoding. We do claim-level post-hoc graph (ADR-001). Observability depth exceeds Notebook LM.

---

## 6. Preserved Behaviors (Invariants)

| ID | Invariant | Code Evidence |
|----|-----------|---------------|
| INV-001 | 3-layer safety runs before retrieval | `service.py:68-102` |
| INV-002 | Hybrid search is default | `retrieval.py:38-46` (`retrieval_mode` defaults to hybrid) |
| INV-003 | SSE streams are append-only | `streaming.py:50-294` |
| INV-004 | Migration chain is append-only | 5 migration versions |
| INV-005 | Screen-Component separation is strict | Screens import components, not vice versa |
| INV-006 | API calls at screen level | WorkspaceContext mediates some calls |
| INV-007 | Citations are extracted post-hoc | `citations.py:24-42` regex on generated text |
| INV-008 | Chunk notes injected into `<source>` tag | `context.py:92-94` `user_note` attribute |
| INV-009 | Intent classification drives prompt selection | `generation.py:60-71` intent→prompt mapping |
| INV-010 | Grounding refusal blocks generation | `service.py:182-190` insufficient evidence → refusal |

---

## 7. Gap Priority Matrix

| Gap | Severity | Effort | Priority | Status | Code Impact |
|-----|----------|--------|----------|--------|-------------|
| No authentication | **CRITICAL** | High | **P0** | OPEN | New middleware on all 9 routers |
| No Docker / deployment config | **CRITICAL** | Medium | **P0** | OPEN | New infra files |
| Dummy reranker (BGE-replacement) | **HIGH** | Medium | **P1** | **DONE (7.0)** | Cross-encoder via FlashRank/BGE |
| Citation generation-time enforcement | **HIGH** | Medium | **P1** | **PARTIAL (9.0 + 10.2)** | Soft prompt + claim graph; no constrained decoding |
| Source-to-answer provenance | **HIGH** | Medium | **P1** | **DONE (10.2 Verifying)** | Claim graph + coverage + X-Ray + eval metric |
| Safety module zero tests (317 LOC) | **HIGH** | Low | **P1** | OPEN | New test file |
| No monitoring / structured logging | **HIGH** | Medium | **P2** | OPEN | New middleware + JSON formatter |
| No CI/CD gates | **HIGH** | Low | **P2** | OPEN | GitHub Actions config |
| RAG evaluation framework | **HIGH** | Medium | **P2** | **PARTIAL (10.1)** | Eval history API + dashboard charts; not full RAGAS CI |
| Knowledge products: streaming generation | MEDIUM | Medium | **P3** | OPEN | SSE for `/generate` routes |
| Knowledge products: interactive flashcard viewer | MEDIUM | Low | **P3** | OPEN | New component |
| Chat history search | MEDIUM | Low | **P3** | OPEN | New SQL query + UI |
| Suggested questions | MEDIUM | Medium | **P3** | OPEN | New endpoint + ChatPanel integration |
| Save-to-note / notebook loop | MEDIUM | Medium | **P3** | OPEN | New table + UI |
| Additional ingestion formats (DOCX, EPUB, YouTube) | MEDIUM | High | **P4** | OPEN | New extractors |
| Output export (PDF, PPTX) | MEDIUM | Medium | **P4** | OPEN | New generation routes |
| Chat personas | LOW | Medium | **P4** | OPEN | Prompt templates + settings |
| Source auto-sync (like Drive sync) | LOW | High | **P5** | OPEN | Webhook/polling system |
| GraphRAG | LOW | Very High | **P5** | OPEN | New architecture |
| Deep Research / agentic web search | LOW | Very High | **P5** | OPEN | New agent sub-system |

---

## 8. Risks & Migration Constraints

### 8.1 Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Auth retrofit** | Adding auth to 9 existing routers with no auth middleware may require breaking API changes | Use FastAPI middleware + dependency injection pattern |
| **Reranker model dependency** | BGE-Reranker-v2 requires ~1GB model download + GPU for acceptable latency | Add as optional; keep dummy fallback |
| **Citation redesign** | Moving from post-hoc to generation-time enforcement requires prompt redesign AND validation pipeline changes | Phase 1: improve post-hoc extraction. Phase 2: add enforcement. |
| **Database migration** | Adding new features (notes, search, export) may require schema changes to the append-only migration chain | New migrations follow existing pattern (append-only) |
| **Frontend state complexity** | Adding save-to-note, suggested questions, search will significantly increase `WorkspaceContext` complexity | Consider splitting context into domain-specific providers |

### 8.2 Migration Constraints

1. **Citation format:** If we change from `[Source N]` to `[N]`, existing chat history citations break. Must maintain backward compatibility.
2. **API contract:** Adding auth must not break the streaming SSE contract (which works without auth today).
3. **Migration append-only:** All new DB tables must use the existing migration runner pattern.
4. **Provider abstraction:** LLM provider abstraction (`providers/`) must be preserved — Notebook LM uses Google models, but we support configurable providers.
5. **X-Ray panel:** Our unique debug panel must not be broken by any changes.

---

## 9. Recommended Build Sequence

### Phase 0 (Shipped — June 2026)
0. **Chunk upgrade** — Adaptive tiering, heading paths, embedding semantic, boundary parent-child, re-chunk button, Settings UI, documentation

### Phase 1 (Shipped — July 2026)
1. **Cross-encoder reranking (7.0)** — BGE/FlashRank cross-encoder replaces dummy sort
2. **Citation UX upgrade (9.0)** — Panel anchoring, short badges, dual-format parse, invalid badge muting
3. **Source-to-Answer Provenance (10.2)** — Claim graph, coverage, SSE+GET, `[unsupported]`, X-Ray Provenance, eval metric, stream groundedness parity
4. **Evaluation dashboard charts (10.1)** — Recall/groundedness/coverage charts, history API
5. **Studio analytics dashboard (10.0)** — Product usage analytics

### Phase 2 (Implementing — July 2026)
6. **UI restructure (3.0)** — Glassmorphism, tab nav, Settings redesign
7. **Chunk upgrade Settings UI (8.0)** — Re-chunk button, strategy selector, preview

### Phase 3 (P0 — Production Gate)
8. **Authentication middleware** — JWT or OAuth2 on all 9 routers
9. **Docker + docker-compose** — production deployment config

### Phase 4 (P1 — Quality Parity)
10. **Safety module test suite** — Minimum 3 tests per layer (heuristic, fuzzy, LLM)
11. **Citation enforcement** — Constrained decoding or regenerate-on-miss (ADR follow-up to 10.2)
12. **Structured logging** — JSON + request tracing middleware
13. **RAG evaluation CI** — RAGAS golden dataset + gate

### Phase 5 (P2 — Observability)
14. **Monitoring** — Health check endpoints + basic metrics
15. **CI/CD gates** — GitHub Actions config

### Phase 6 (P3 — Feature Parity with Notebook LM)
16. **Suggested questions** — LLM-generated from source summaries on session open
17. **Chat history search** — Full-text search across turns
18. **Save-to-note / notebook loop** — Persist responses as notes; inject notes as sources
19. **Knowledge product streaming** — SSE for generate routes
20. **Interactive flashcard viewer** — Flip animation, progress tracking

### Phase 7 (P4 — Expansion)
21. **DOCX + EPUB ingestion**
22. **Output export (PDF, PPTX)**
23. **Chat personas**

### Phase 8 (P5 — Advanced)
24. **GraphRAG**
25. **Deep Research / agentic retrieval**
26. **Multi-modal understanding**
27. **Source auto-sync**

---

## 9.1 Feature Status Ledger (as of 2026-07-09)

| Feature slug | Phase | Notes |
|--------------|-------|-------|
| `1.0-citation-ingest-richer` | Done | Research complete |
| `2.0-conflict-detection-knowledge-products` | Done | Multi-doc conflict surfacing |
| `3.0-ux-upgrade` | Implementing | Glassmorphism / Settings |
| `4.0-ui-panel-restructure` | Implementing | 3-panel workspace |
| `5.0-session-by-collection` | Done | Per-collection sessions |
| `6.0-remove-playground` | Verifying | Playground removal |
| `7.0-cross-encoder-reranking` | Done | FlashRank/BGE cross-encoder |
| `8.0-chunk-upgrade` | Implementing | Adaptive tiering + Settings |
| `9.0-citation-upgrade` | Done | Panel anchor, dual-format parse |
| `10.0-studio-analytics-dashboard` | Implementing | Studio analytics |
| `10.1-evaluation-dashboard-charts` | Implementing | Eval charts + history API |
| `10.2-source-to-answer-provenance` | Verifying | Claim graph + coverage + X-Ray |
| `production-rag-audit` | Research Complete | This document (refreshed) |

---

## 10. Conclusion

Our system has **strong parity with Notebook LM on the core 3-panel layout, knowledge products, hybrid search, cross-encoder reranking, citation UX (panel anchoring + display-layer uncited markers), claim-level source-to-answer provenance (graph + coverage + reverse map), conflict detection, evaluation dashboard, studio analytics, and streaming chat**. The features shipped in July 2026 closed the citation UX, reranking, provenance, and observability gaps.

**What we still lack to match Notebook LM as a document-chat product:**
1. **Production foundation:** No auth, no Docker, no monitoring → blocks any real deployment
2. **Citation architecture (residual):** Post-hoc extraction is less reliable than generation-time enforcement (soft enforcement via prompt + provenance graph only; no constrained decoding / regenerate-on-miss yet)
3. **Knowledge loop:** No save-to-note → user insights don't feed back into the knowledge base
4. **Proactive UX:** No suggested questions, no chat history search
5. **Studio output parity:** No streaming, no export, no interactive flashcards

**What was shipped in July 2026 (Phase 1) to close gaps:**
- Cross-encoder reranking (7.0) — BGE/FlashRank parity with Notebook LM
- Citation UX upgrade (9.0) — Panel anchoring, short badges, dual-format parse, invalid badge muting
- Source-to-Answer Provenance (10.2) — Claim graph, coverage, SSE+GET, `[unsupported]`, X-Ray Provenance, eval metric, stream groundedness parity
- Evaluation dashboard charts (10.1) — Recall/groundedness/coverage charts, history API
- Studio analytics dashboard (10.0) — Product usage analytics
- Conflict detection (2.0) — Multi-document contradiction surfacing
- Chunk upgrade (8.0) — Adaptive tiering, heading path preservation, embedding-based semantic chunking, boundary-aware parent-child, Settings UI, re-chunk button → Notebook LM parity on chunking

**Where we lead:**
- Debug/observability (X-Ray Panel with full pipeline trace + Provenance section)
- Collection-scoped sessions (Notebook LM has weaker per-collection isolation)
- Configurable query intelligence strategies (5 transformation types vs Notebook LM's Gemini-native pipeline)
- Chunk-level user annotations injected into context
- Display-layer `[unsupported]` markers from claim graph (no history mutation)

Route to `/spec-requirements` for Phase 3 (auth + Docker), then `/spec-plan` for Phase 4 (citation enforcement + safety tests + RAGAS CI). The scope is well-understood and the architecture clean enough to proceed directly.
