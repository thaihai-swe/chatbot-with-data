# Research Analysis: 10.2 Source-to-Answer Provenance

## Metadata
- Investigation name: Source-to-Answer Provenance (claim → chunk attribution)
- Feature slug: `10.2-source-to-answer-provenance`
- Date: 2026-07-09
- Status: Research Complete
- Parent audit: `artifacts/features/production-rag-audit/analysis.md` §5.4
- Predecessor: `artifacts/features/9.0-citation-upgrade` (Done)

## Scope

- **What is being investigated:** End-to-end provenance from retrieved source chunks to individual claims in the generated answer. How far the system goes today; what Notebook LM–class token/claim-level attribution still lacks after 9.0; brownfield reuse points.
- **What is explicitly out of scope:**
  - True provider-native token-level attribution / constrained decoding (research note only; not required for first slice).
  - Authentication, Docker, deployment.
  - Reranker model swap (7.0).
  - Multi-modal (image/audio) citations.
  - Save-to-note / knowledge loop (audit P3).

## Current State

### Observed pipeline (fact)

```
Safety → Collection routing → Advanced retrieval (trace)
      → Chunk safety filter
      → Evidence sufficiency (GroundingService.evaluate_evidence)
      → Context assembly (<source label="Source N" id=chunk_id> + <citation-map>)
      → Free-text generation (prompt soft-enforces [Source N] per claim)
      → Post-hoc CitationService.extract_citations (regex)
      → map_citations_to_chunks (index or chunk_id)
      → extract_quote (Jaccard ≥ 0.5, else LLM fallback)
      → Persist citations + turn (retrieved_chunks_json, context_used_json)
      → SSE: token* → citations{citations, retrieved_chunks, traces} → done
```

### What 9.0 already shipped (fact)

| Capability | Status | Evidence |
|------------|--------|----------|
| Soft generation-time citation instruction | Shipped | `prompts.py:12-14` — every factual claim MUST be followed by a citation |
| Dual-format parser `[Source N]` / `[N]` | Shipped | `citations.py:19` `CITATION_PATTERN` |
| Short badge + HoverCard + invalid muted | Shipped | `CitationBadge.jsx` |
| Workspace `activeChunkId` + expand sources | Shipped | `WorkspaceContext.jsx:45-51, 98-100` |
| SourceBrowser reacts to `activeChunkId` | Shipped | `SourceBrowser.jsx:138-145` |
| Citation rows with `quote_text` | Pre-existing + kept | `models/chat.py:53-63`, `ChatRepository.create_citation` |

### What still fails provenance goals (fact + inference)

1. **No claim graph.** Citations are turn-level rows (`turn_id → chunk_id`). There is no `claim_text`, sentence index, char span, or confidence linking a specific answer sentence to a source.
2. **No coverage enforcement.** Uncited sentences are not detected, scored, or repaired. Prompt text is advisory only.
3. **Quote ≠ attribution.** `extract_quote` is reverse Jaccard/LLM guess after generation (`citations.py:46-118`), not generation-time binding.
4. **Streaming drops groundedness persistence.** Sync path writes `groundedness_score` (`service.py:211-258`); stream path finalizes answer + citations without calling `calculate_groundedness` or persisting the score (`streaming.py:204-258`).
5. **9.0 anchoring incomplete in ChatPanel.** `handleCitationClick` still opens `CitationModal` via local state (`ChatPanel.jsx:297-302`) and does **not** call `setActiveChunkId`. Badges still render `Source ${label} - ${docTitle}` (`ChatPanel.jsx:405-409`), not short-only labels from the 9.0 AC.
6. **X-Ray is retrieval/safety only.** `XRayPanel.jsx` shows groundedness %, risk, intent, transformations, latency — no citation map, claim coverage, or uncited-sentence list.
7. **Eval ignores citation quality.** `EvaluationService` measures document recall + groundedness score only (`evaluation.py:127-169`). No citation precision, coverage, or quote-match metrics.
8. **No reverse provenance.** Cannot answer "which claims does chunk X support?" without re-parsing answer text.

### Relevant boundaries

| Layer | Files | Role in provenance |
|-------|-------|--------------------|
| Prompt / gen | `backend/chat/prompts.py`, `generation.py` | Soft cite-every-claim instruction |
| Context | `backend/chat/context.py` | Labels Source N, embeds chunk ids, builds `<citation-map>` |
| Extract | `backend/chat/citations.py` | Regex + map + quote |
| Orchestration | `service.py`, `streaming.py` | Persist chunks, citations, traces |
| Grounding | `grounding.py` | Evidence sufficiency + LLM-as-judge score (answer-level, not claim-level) |
| Models | `models/chat.py`, `schemas/chat.py` | `ChatTurn`, `Citation`, `CitationResponse`, traces |
| UI | `ChatPanel.jsx`, `CitationBadge.jsx`, `CitationModal.jsx`, `SourceBrowser.jsx`, `WorkspaceContext.jsx`, `XRayPanel.jsx` | Render/click/hover; partial anchor |

### Unchanged behavior that must be preserved

| ID | Invariant | Evidence |
|----|-----------|----------|
| INV-001 | 3-layer safety before retrieval | `service.py` / `streaming.py` order |
| INV-003 | SSE append-only tokens; citations finalize after generation | `streaming.py:192-268` |
| INV-007 | Citations extracted post-hoc from free text | `citations.py:24-44` |
| INV-010 | Insufficient evidence → refusal, no fake citations | `service.py:196-204`, `streaming.py:170-187` |
| BF-9.0 | Legacy `[Source N]` history must still parse | Dual regex already in place |
| BF-XRAY | X-Ray retrieval/safety traces must keep working | `XRayPanel.jsx` |

## Decision-Ready Summary

- **What matters most:** Provenance is **turn-level bag of citations**, not **claim-level source binding**. 9.0 improved prompt pressure + UI chrome; it did not build a verifiable claim→chunk graph or coverage metric.
- **Strongest supported conclusion:** First useful 10.2 slice is a **post-generation claim provenance graph** (sentence split → citation labels → chunk_id + quote span + coverage stats), persisted and exposed on the turn/SSE payload, rendered in X-Ray and optionally as reverse hover. Soft regenerate-on-missing-cites is a later phase. True constrained decoding is out of first slice.
- **Single next proving step:** `/spec-requirements` for claim-graph schema, coverage definition, API shape, and X-Ray/UI acceptance criteria. Use `/spec-adr` only if product insists on hard generation-time enforcement vs post-hoc repair in v1.

## Findings

### Finding 1 — Provenance stops at "which chunks were cited," not "which claim used which chunk"
- **Evidence:** `Citation` stores `turn_id, chunk_id, document_id, quote_text` only (`models/chat.py:53-63`). `map_citations_to_chunks` returns one row per unique label, not per occurrence/claim (`citations.py:120-172`).
- **Type:** Fact

### Finding 2 — Soft enforcement only; no validation gate
- **Evidence:** Prompt requires cite-every-claim (`prompts.py:12-13`). No post-gen check rejects or repairs uncited sentences before `status=completed`.
- **Type:** Fact

### Finding 3 — Stream path weaker observability than sync
- **Evidence:** Sync calls `calculate_groundedness` and persists score (`service.py:211-258`). Stream finalizes without score update (`streaming.py:253-258`).
- **Type:** Fact

### Finding 4 — 9.0 UI anchoring partially implemented
- **Evidence:** Context + SourceBrowser support `activeChunkId`. `ChatPanel.handleCitationClick` still sets modal state only (`ChatPanel.jsx:297-302`) and does not call `setActiveChunkId`. Badge label still includes document title (`ChatPanel.jsx:405`).
- **Type:** Fact
- **Inference:** 10.2 should either finish 9.0 anchoring as a prerequisite task or absorb the remaining wire-up so provenance UI is not modal-only.

### Finding 5 — Context already emits machine-readable source labels
- **Evidence:** `<source label="Source N" id="{chunk_id}" …>` and `<citation-map>` (`context.py:72-106, 183-199`). Generation-time binding has the IDs available; only free-text emission + post-hoc parse consume them.
- **Type:** Fact

### Finding 6 — X-Ray has no citation/provenance section
- **Evidence:** `XRayPanel.jsx` sections = Safety & Grounding, Transformations, Strategy, Latency, raw JSON. No claim coverage, no per-citation map.
- **Type:** Fact

### Finding 7 — Eval has no citation metrics
- **Evidence:** Pass = recall AND groundedness ≥ 0.7 (`evaluation.py:157-158`). No citation coverage / precision.
- **Type:** Fact

### Finding 8 — Jaccard quote match is brittle for short or paraphrased claims
- **Evidence:** Threshold 0.5 word Jaccard (`citations.py:22, 99-100`); else LLM fallback latency (`citations.py:102-116`).
- **Type:** Fact
- **Inference:** Claim graph should store match method + score for observability.

### Finding 9 — Unique-label dedup loses multi-claim occurrence
- **Evidence:** `extract_citations` returns unique labels only (`citations.py:24-44`). Same source supporting three sentences yields one citation row.
- **Type:** Fact

### Finding 10 — Invalid labels are silent drops
- **Evidence:** `map_citations_to_chunks` skips unmapped labels with no error row (`citations.py:156-157`). Frontend mutes unmatched badges; no server audit trail.
- **Type:** Fact

### Finding 11 — Source index is positional post-safety order
- **Evidence:** `context.py:73-74` labels `Source {i+1}` over the filtered list; `citations.py:145-148` maps digit labels by that index. Reordering filters would break stored answers that used index labels.
- **Type:** Fact

### Finding 12 — Legacy `Chat.jsx` still duplicates citation UX
- **Evidence:** `screens/Chat.jsx` has parallel badge/modal path alongside workspace `ChatPanel.jsx`.
- **Type:** Fact
- **Inference:** 10.2 must update both surfaces or delete the legacy screen path.

## Brownfield Mapping

### Target files (reuse, do not reinvent)

| Area | Path | Reuse mode |
|------|------|------------|
| Citation extract/map | `backend/chat/citations.py` | Extend with claim segmentation + coverage |
| Context labels | `backend/chat/context.py` | Keep Source N / chunk id contract |
| Sync orchestrator | `backend/chat/service.py` | Attach provenance payload; persist |
| Stream orchestrator | `backend/chat/streaming.py` | Emit provenance in `citations` SSE; fix groundedness parity |
| Models / schema | `models/chat.py`, `schemas/chat.py` | Add claim/provenance DTOs; optional migration |
| Repository | `repositories/chat_repository.py` | Persist claim rows or JSON blob |
| Tests | `backend/tests/chat/test_citations.py` | Extend |
| Badge / chat | `CitationBadge.jsx`, `ChatPanel.jsx` | Finish short labels + `setActiveChunkId` |
| Anchor | `WorkspaceContext.jsx`, `SourceBrowser.jsx` | Already ready for highlight |
| Debug | `XRayPanel.jsx` | Add Provenance section |
| Eval | `chat/evaluation.py` | Optional citation coverage metric |

### Preserved behaviors

- Post-hoc extraction remains the primary path for v1 (INV-007). Do not break free-text generation or SSE token stream.
- Existing `citations` table rows and history with `[Source N]` stay valid.
- Grounding refusal path emits no fake citations.

### Fragile boundaries

- Dual orchestrators (sync vs stream) already drift on groundedness — provenance must land in **both** or stream will ship incomplete data.
- `CitationModal` vs panel-anchoring dual UX; keep modal optional for quote/notes if product still wants it, but primary path should be panel + claim graph.
- `SourceBrowser` matches `c.id === activeChunkId` while chat chunks use `chunk_id` — confirm ID field parity when wiring reverse provenance.

### Existing validation surface

- `backend/tests/chat/test_citations.py` — parser/map.
- Manual X-Ray + chat UI scenarios from 9.0.

## Gap Matrix (vs Notebook LM–class provenance)

| Capability | Notebook LM (audit) | Ours today | 10.2 target |
|------------|---------------------|------------|-------------|
| Generation-time cite tokens | Architectural | Soft prompt | Soft + optional repair (P2) |
| Claim → source binding | Token/chunk ID | Unique labels only | Claim graph per sentence |
| Quote span | Passage highlight | Jaccard/LLM quote | Span + score + method |
| Coverage | Every claim cited | Not measured | % cited + uncited list |
| Reverse lookup | Source panel focus | Chunk bag | Claims-for-chunk view |
| Debug | Limited | X-Ray retrieval | X-Ray provenance section |
| Eval metric | Internal | Recall + groundedness | + citation coverage |

## Risks And Unknowns

| Risk / unknown | Why it matters | Next proving step |
|----------------|----------------|-------------------|
| **Hard enforcement vs soft** | Constrained decoding / regenerate loops add latency and provider coupling | Spec decision: v1 post-hoc graph only; v2 optional repair |
| **Sentence segmentation quality** | Period-split (`citations.py:12`) fails on abbreviations, lists, markdown | Spec AC for markdown-aware split or reuse existing answer AST if any |
| **Schema migration** | New claim table vs JSON column on turn | Prefer `provenance_json` on turn first (append-only migration); normalize later if queried |
| **Stream/sync parity** | Already diverged on groundedness | Requirement: same provenance builder used by both paths |
| **9.0 residual debt** | Modal still primary; long badge labels | Absorb wire-up into 10.2 Phase 0 or file as bugfix before feature work |
| **Chunk id field mismatch** | `id` vs `chunk_id` in SourceBrowser vs chat payloads | Prove with one integration test on anchor from claim graph |
| **Latency of quote LLM fallback** | Blocks finalize stage | Prefer Jaccard/span only in graph v1; LLM optional async |

## Recommendation

### Proposed feature shape (for requirements, not a plan)

1. **Phase 0 — Finish 9.0 wire-up (small)**  
   ChatPanel: short badge labels; `setActiveChunkId(chunk_id, document_id)` on click; keep HoverCard; modal optional for notes/quote deep-dive.

2. **Phase 1 — Claim provenance graph (core)**  
   After generation: segment answer → attach citation labels per sentence → map to chunks → store `{claims: [{text, start, end, citations:[{label, chunk_id, document_id, quote_text, match_score, match_method}]}], coverage: {cited, total, uncited[]}}` on the turn (JSON) and in SSE `citations` event.

3. **Phase 2 — Observability**  
   X-Ray Provenance section; stream groundedness parity; optional eval metric `citation_coverage`.

4. **Phase 3 — Soft repair (optional)**  
   If coverage < threshold, one repair pass or append `[unsupported]` markers (already in prompt language via `UNCERTAINTY_INSTRUCTION`).

### What not to build yet
- Provider-specific token attribution APIs.
- Graph database / GraphRAG.
- Multi-hop claim trees beyond existing `ReasoningChainTrace`.

### Architecture decision (locked)
- **ADR-001 Accepted:** post-generation claim provenance graph; `provenance_json` on turn; coverage metrics; no constrained decoding / hard repair in v1.
- Artifact: `core-zero/project/adr/001-source-to-answer-provenance-mode.md`

### Next skill
- **Next:** `/spec-requirements`
- **Why:** Decision mode is locked by ADR-001; requirements can specify claim graph shape, coverage, SSE/API, X-Ray, Phase 0 9.0 wire-up.
- **Exact next prompt:**  
  `/spec-requirements` for `10.2-source-to-answer-provenance` — implement ADR-001: claim graph schema, coverage definition, SSE/API fields, X-Ray section, Phase 0 9.0 wire-up, acceptance criteria. Prefer `provenance_json` on turn over new table for first slice.

## Reproduction Evidence

Not a bug investigation. Baseline behaviors verified by code read (paths above). Manual product repro if needed:

1. Ask a multi-source factual question in chat (stream).
2. Observe `[Source N]` markers and `citations` SSE payload: unique chunk list, no per-claim graph.
3. Click badge → modal (not guaranteed panel scroll).
4. Open X-Ray → no claim coverage.

## Appendix A — Audit origin (verbatim intent)

From `production-rag-audit/analysis.md` §5.4:

> **Notebook LM:** Each token in the answer can theoretically be traced back to the source chunk that influenced it (token-level attribution via chunk ID in prompt).  
> **Our system:** We track which chunks were used in context (`retrieved_chunks_json` on each turn) and extract citations post-hoc, but there's no token-level attribution. The X-Ray panel shows the retrieval trace…

Gap priority in audit matrix: **Citation generation-time enforcement — HIGH / P1** (partially addressed by 9.0 prompts). Remaining provenance depth is the subject of **10.2**.

## Appendix B — Domain language (from `core-zero/memories/domain/rag/glossary.md`)

| Term | Use in 10.2 |
|------|-------------|
| Grounded Generation | Keep; extend with claim coverage |
| X-Ray Panel | Add provenance view |
| SSE Streaming | Finalize provenance after tokens (INV-003) |
| Context Assembly | Source of Source N ↔ chunk_id map |
