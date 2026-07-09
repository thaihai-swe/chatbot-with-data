# ADR-001: Source-to-Answer Provenance Mode

Status: Accepted
Date: 2026-07-09
Deciders: Feature owner (10.2)
Feature slug: `10.2-source-to-answer-provenance`
Related analysis: `artifacts/features/10.2-source-to-answer-provenance/analysis.md`
Related spec: (pending `/spec-requirements`)
Related plan: (pending)

## Context

Production RAG audit §5.4 and 10.2 research established that the system has **turn-level bag-of-citations** (post-hoc regex → chunk map + optional quote) but not **claim-level source-to-answer provenance**.

9.0 shipped stronger prompt language ("every factual claim MUST cite") and dual-format parsing. That is soft generation-time pressure only — free-text generation, post-hoc extraction, no claim graph, no coverage metric, no reverse lookup.

Three forces conflict:

1. **Reliability** — Notebook LM–class UX needs every substantive claim traceable to a source chunk.
2. **Provider portability** — the stack supports configurable LLM providers; constrained decoding / tool-forced cites are provider-specific and break streaming assumptions.
3. **Brownfield invariants** — SSE is append-only tokens then a final `citations` event (INV-003); citations are extracted post-hoc (INV-007); legacy `[Source N]` history must keep parsing.

We need a durable choice for **how** 10.2 binds answer claims to sources in v1, so requirements and plan do not thrash between "hard enforcement" and "observability graph."

## Decision

**v1 uses post-generation claim provenance graph (Option A).**

After free-text generation completes:

1. Segment the answer into claim units (sentences / markdown-aware blocks).
2. Attach citation labels present on each claim via existing dual-format regex.
3. Map labels → chunks using existing `map_citations_to_chunks` index/UUID rules.
4. Optionally attach quote span + match score/method (reuse Jaccard path; store score).
5. Compute coverage (`cited / total`, `uncited[]`).
6. Persist as `provenance_json` (or equivalent) on the turn and emit on the existing SSE `citations` event.
7. Expose in X-Ray; finish 9.0 UI wire-up (short badge + `setActiveChunkId`).

**Not in v1:** constrained decoding, tool-forced structured cites, hard fail/regenerate loops, provider logprobs/token attribution.

**Deferred (v2+):** soft repair pass when coverage &lt; threshold (one re-ask or `[unsupported]` marking); optional structured-generation experiment behind a flag if a single provider path proves valuable.

## Options Considered

### Option A: Post-generation claim provenance graph (CHOSEN)

Build a structured claim→chunk graph after free-text generation; keep prompt soft-enforcement and post-hoc regex as the binding mechanism.

| Dimension | Assessment |
|-|-|
| Complexity | Low–Med — extends `CitationService`, one JSON field, X-Ray section |
| Cost | Low — no extra LLM call in happy path if Jaccard-only quotes |
| Scalability | High — provider-agnostic; works on stream and sync paths |
| Team familiarity | High — reuses 9.0 regex, context labels, citation rows |

Pros:
- Preserves INV-003 / INV-007 and dual-provider abstraction.
- Delivers reverse provenance + coverage metrics without redesigning generation.
- Reuses `citations.py`, context `<source label>`, `retrieved_chunks_json`.
- Safe to ship behind existing SSE `citations` event shape (additive fields).

Cons:
- Still depends on the model emitting markers; uncited claims are measured, not prevented.
- Sentence segmentation quality bounds claim accuracy.
- Not true token-level attribution.

### Option B: Generation-time structured enforcement

Force the model to emit structured citations (JSON tool call, constrained decoding, or per-claim schema) during generation so every claim is bound before tokens leave the server.

| Dimension | Assessment |
|-|-|
| Complexity | High — provider adapters, stream protocol change, fallback path |
| Cost | Med–High — tool/JSON mode latency; possible multi-step gen |
| Scalability | Low–Med — diverges per provider; breaks or complicates SSE |
| Team familiarity | Low — no current structured-cite path in `generation.py` |

Pros:
- Stronger architectural guarantee (closer to Notebook LM intent).
- Cleaner claim spans if model cooperates.

Cons:
- Breaks or versions the streaming contract (tokens vs structured events).
- Provider portability risk (core product constraint).
- Legacy free-text history still needs Option A fallback forever.
- Overbuilds relative to 10.2 goal (verifiable provenance graph + UX).

### Option C: Soft prompt only (status quo after 9.0)

Keep prompt instructions and post-hoc unique-label citations; no claim graph.

| Dimension | Assessment |
|-|-|
| Complexity | None |
| Cost | None |
| Scalability | N/A |
| Team familiarity | High |

Pros:
- Zero code risk.

Cons:
- Does not close audit §5.4 gap.
- No coverage, no reverse lookup, no claim-level X-Ray.
- 9.0 residual UX debt remains unowned.

### Option D: Hybrid hard-repair loop (post-hoc verify → regenerate)

Option A graph, then if coverage &lt; threshold automatically regenerate or surgically rewrite uncited sentences.

| Dimension | Assessment |
|-|-|
| Complexity | Med–High |
| Cost | High — extra LLM pass on many turns |
| Scalability | Med — latency spikes on weak models |
| Team familiarity | Med |

Pros:
- Improves completeness without constrained decoding.
- Aligns with existing `[unsupported]` vocabulary.

Cons:
- Doubles latency on failure path; needs cancel/stream semantics.
- Conflicts with "finalize once" SSE simplicity unless carefully staged.
- YAGNI for v1 — measure coverage first, then decide repair policy.

## Trade-off Analysis

| Criterion | A Graph | B Structured gen | C Status quo | D Repair loop |
|-----------|---------|------------------|--------------|---------------|
| Closes §5.4 observability | Yes | Yes | No | Yes |
| Preserves SSE + providers | Yes | No / fragile | Yes | Partial |
| Latency | Near-zero | Higher | Baseline | Higher on miss |
| Reuse of 9.0 | Full | Partial | Full | Full |
| YAGNI / ponytail | Best fit | Overbuild | Underbuild | Premature |

**A wins:** it is the minimum architecture that produces claim-level provenance, coverage, and reverse lookup without violating streaming, provider abstraction, or legacy cite formats. B optimizes for enforcement purity the product cannot pay for across providers in v1. C fails the feature goal. D is a sensible **later** phase once coverage metrics exist to justify the cost.

Storage detail locked with A: **prefer `provenance_json` on the turn** (append-only migration) over a normalized claim table in v1. Normalize only if product queries require it.

## Consequences

**Easier:**
- Spec can require claim graph shape, coverage definition, SSE additive fields, X-Ray section.
- Implementation extends `CitationService` + shared builder used by `service.py` and `streaming.py`.
- Eval can add `citation_coverage` without new infra.

**Harder:**
- Must define claim segmentation rules (markdown lists, abbreviations).
- Must fix stream/sync groundedness parity while touching finalize path.
- Must finish 9.0 wire-up (`setActiveChunkId`, short labels) so graph is usable in UI.

**Revisit later:**
- Soft repair (Option D) when coverage baselines are known.
- Structured generation (Option B) only if a single-provider deployment needs hard guarantees.
- Normalized claim table if analytics need SQL over claims.

## Action Items

1. [ ] `/spec-requirements` for 10.2 using this ADR as locked decision (claim graph + `provenance_json` + coverage + X-Ray; no constrained decoding in v1).
2. [ ] Spec Phase 0: finish 9.0 residual UI (short badge, `setActiveChunkId` on click).
3. [ ] Spec requires single provenance builder shared by sync and stream paths.
4. [ ] Defer repair-loop and structured-gen to explicit later ADRs if pursued.
