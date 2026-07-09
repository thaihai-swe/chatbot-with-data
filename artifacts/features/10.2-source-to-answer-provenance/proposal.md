# Proposal: 10.2 Source-to-Answer Provenance

## Problem
Turn-level bag-of-citations cannot answer claim→source, coverage, or reverse-lookup questions. Audit §5.4 + 9.0 left this gap.

## Solution (ADR-001)
Post-generation claim provenance graph (paragraph units) + coverage metrics + X-Ray section + display-layer `[unsupported]` markers. No constrained decoding in v1.

## In Scope
- Phase 0: Stream groundedness parity; delete legacy Chat.jsx citation path
- Phase 1: Claim graph builder; `provenance_json`; SSE/GET; ChatPanel markers + panel anchor; X-Ray; eval coverage

## Out of Scope
Constrained decoding, hard repair loops, token attribution, multi-modal cites, save-to-note, new claim SQL table, badge label change, CitationModal as primary click.

## Success
Every paragraph classified cited/uncited; coverage stored; X-Ray shows graph; badge anchors panel; eval has `citation_coverage`.

## Complexity
Complex (cross-boundary: pipeline + schema + SSE + UI + eval).

## Next
`/spec-plan` after Spec Approved.
