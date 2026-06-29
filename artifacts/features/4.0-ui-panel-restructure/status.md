# 4.0 — UI Panel Restructure

## Current Phase: Implementing

## Complexity: Complex

## Intake
- *Input type:* new_spec
- *Risk flags:* high (brownfield UI restructure — 7 screens, 16 components, 0 tests, routing redesign)
- *One-line restatement:* Restructure the single-column chat UI into a Notebook LM-style 3-panel layout (Sources + Chat + Studio) with collapsible panels and collection/document selection scope.
- *Reasoning:* Production RAG Audit (2026-06-29) identified the single-column UI as a CRITICAL gap vs Notebook LM.

## Triggered Domain Packs
- [x] Frontend UI — triggered: `ui`, `frontend`, `react`, `component`, `screen`

## High-Level Progress
- [x] Research complete
- [x] Spec approved
- [x] Plan approved
- [ ] Implementation complete
- [ ] Verification complete

## Findings
- **Most code already exists** — SourceBrowser, DocumentLibrary, CitationModal, knowledge product APIs just need re-parenting into a 3-panel container
- **Zero frontend tests** — all 16 components + 7 screens have 0 tests; refactoring is blind
- **Routing strategy: Option A** — nested routes under `/chat`, standalone pages for admin
- **State: React Context** — lightweight shared context for cross-panel state + generated products list
- **Knowledge products: sync with loading states** — no SSE streaming (out of scope)
- **CSS: append to existing styles.css** — no extraction (out of scope)

## Scope Changes
- `[ADDED]` Knowledge product generation buttons in ChatPanel composer toolbar (in addition to Studio panel)
- `[ADDED]` Generated products render as chat messages (assistant role) with formatted output
- `[ADDED]` Studio panel shows history of generated products

## Next Step
Route to `/spec-implement` — execute phase-by-phase: Foundation (P1) -> SourcesPanel (P2) -> ChatPanel (P3) -> Studio + Chat Gen (P4) -> Polish (P5).
