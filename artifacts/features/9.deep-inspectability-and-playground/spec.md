# Feature Specification

## Metadata

- Feature name: Deep Inspectability and Playground
- Feature slug: deep-inspectability-and-playground
- Owner: Unassigned
- Status: Draft
- Last updated: 2026-05-16
- Related knowledge artifact(s): `prd-requirement.md`

## Problem Statement
While users can see the final answer and basic trace data, they cannot easily compare different retrieval strategies for a *single* query side-by-side, nor can they inspect the full source context for a specific citation, which limits the educational value of the lab.

## Desired Outcomes
- Users can click citations to see exact chunk content and parent context.
- Users have a "Playground" UI to test how different toggles (HyDE, Expansion, Routing) affect a single question in real-time.

## Success Criteria
- [ ] SC-001: The Chat UI includes a Citation Detail View modal that shows chunk metadata, retrieval scores, and text.
- [ ] SC-002: The system includes a Strategy Comparison playground where a query is run through two different configurations side-by-side.

## In Scope
- **Citation Detail View Modal (PRD 7.15.4):** Shows cited document title, chunk ID, parent chunk ID, retrieval score, and text snippet.
- **Strategy Comparison Playground (PRD 7.15.6):** A dedicated UI screen for side-by-side "Strategy A" vs "Strategy B" testing of a single query.
- Visual diffing of retrieved chunks between two strategies.

## User Stories
- **US-001:** As a learner, I want to click a citation and see the exact chunk and its parent page so I can verify the model's claim.
- **US-002:** As a developer, I want to type a query once and see how it performs with HyDE enabled vs. disabled side-by-side.

## Functional Requirements

### REQ-001: Citation Detail View
The Chat UI must support clicking a citation tag to open a modal showing:
- Document Title & ID
- Source URL (if web)
- Retrieval Score
- Full Chunk Text
- Parent Chunk Text (if Parent-Child retrieval was used)

### REQ-002: Strategy Comparison Playground
A new "Playground" screen must allow users to:
- Input a query.
- Select two different "Advanced Config" sets.
- Execute both and show Chunks + Answer side-by-side.
- Highlight the chunks that are present in one strategy but missing in the other.

## Acceptance Criteria
- [ ] AC-001: Clicking a source tag in chat opens a readable modal with chunk details.
- [ ] AC-002: The Playground screen allows running a query and displays two vertical panels for comparison.
