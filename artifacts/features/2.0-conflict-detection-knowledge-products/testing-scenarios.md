# Testing Scenarios

## Purpose

This guide outlines the scenario matrices for manual and integration testing of the Conflict Detection and Knowledge Products Studio feature.

## Scope

- Feature name: Conflict Detection & Knowledge Products
- Feature slug: 2.0-conflict-detection-knowledge-products
- Delivered scope under test:
  - Conflict checking service, REST endpoints, and UI warning banner.
  - Collection-level study products generation API endpoints and frontend previews.
- Out of scope:
  - Document parser/ingester modifications.
  - Vector search model modifications.

## Estimated Time

- Approximate total time: 15 minutes

## Prerequisites

- Required environment: Local backend server running on port 8000; frontend React dev server running on port 5173.
- Required accounts or permissions: None (standard admin/local sandbox).
- Required services or dependencies: SQLite database populated with documents.

## Scenario Matrix

| Scenario | Linked AC | Goal | Priority | Notes |
|----------|-----------|------|----------|-------|
| SCN-001 | AC-1.1, AC-1.2 | Trigger unresolved conflict alert in multi-doc response | High | Requires conflicting data |
| SCN-002 | AC-1.2 | Bypasses conflict checker for single document query | Medium | Optimizes latency |
| SCN-003 | AC-2.1, AC-2.3 | Fallback chunk summaries when pre-computed metadata missing | High | Verifies SQL fallback |
| SCN-004 | AC-2.2 | Flashcard formats strictly parsed and returned as grid list | High | Tests JSON validation |

## Happy Path Scenarios

### SCN-001: Trigger unresolved conflict alert

Goal: Verify the system flags a turn as having an unresolved conflict when the assistant ignores contradictory source facts.

Linked acceptance criteria: AC-1.1, AC-1.2

Steps:

1. Ingest two documents to the same collection (e.g. Doc 1 states "Mars has 2 moons: Phobos and Deimos", Doc 2 states "Mars has 3 moons: Phobos, Deimos, and Ares").
2. Query "How many moons does Mars have?".
3. Ensure the assistant returns a response matching Doc 1 (ignoring Doc 2).
4. Verify that the warning alert badge `⚠️ Warning: Source Contradiction Detected` is rendered below the bubble with details about Doc 1 and Doc 2's contradiction.

### SCN-003: Fallback chunk summaries generation

Goal: Verify the system falls back to first 3 chunks of a document for synthesis if `doc_understanding` metadata is missing.

Linked acceptance criteria: AC-2.1, AC-2.3

Steps:

1. Remove `doc_understanding` from a document's metadata column in the SQLite DB.
2. Hit the endpoint `POST /collections/{collection_id}/generate/study-guide`.
3. Check the backend logs to confirm: `Generating fallback summary for document...`.
4. Ensure the study guide generated successfully compiles and contains information from the document chunks.

## Edge Cases And Failure Paths

### SCN-EDGE-001: Flashcard parsing failure gracefully handled

Goal: Handle situations where LLM returns invalid JSON flashcards.

Linked acceptance criteria: AC-2.2

Steps:

1. Force LLM mock/provider to return invalid markdown content or bad JSON formatting.
2. Trigger flashcard generation.
3. Verify that the endpoint returns `[]` (empty list) gracefully instead of failing with 500.

## Sign-Off

- Tested by: Antigravity
- Date: 2026-06-28
- Passed scenarios: SCN-001, SCN-002, SCN-003, SCN-004, SCN-EDGE-001
- Overall outcome: Pass
