# Testing Scenarios

## Purpose

This guide outlines manual and integration testing scenarios to validate quote-level citations, document understanding, and rich context engineering.

## Scope

- Feature name: Citation, Document Understanding, and Richer Context
- Feature slug: 1.0-citation-ingest-richer
- Delivered scope under test:
  - Exact quote extraction from chunk text
  - Source-level document understanding (summary, topics, section hierarchy)
  - Enriched system prompts (conflict/uncertainty handling) and context blocks
  - Frontend components (`CitationModal`, `DocumentLibrary`, `DocumentTable` integration)
- Out of scope:
  - Actual LLM generation engine behavior (mocked or external API behavior verified outside this feature context)

## Estimated Time

- Approximate total time: 30 minutes

## Prerequisites

- Required environment: Local dev environment with backend python server and frontend dev server running.
- Required accounts or permissions: Access to local database and Weaviate instance.
- Required services or dependencies: Weaviate instance running (via Docker).
- Required data or fixtures: A few sample text/markdown/PDF files.

## Setup

- Step 1: Ensure Weaviate is running: `docker-compose up -d`
- Step 2: Start backend: `uvicorn main:app --reload` (in backend/)
- Step 3: Start frontend: `npm run dev` (in frontend/)

## Scenario Matrix

| Scenario | Linked AC | Goal | Priority | Notes |
|----------|-----------|------|----------|-------|
| SCN-001 | AC-1.1, AC-1.2, AC-1.7 | Validate exact quote matching and display | High | |
| SCN-002 | AC-2.1, AC-2.4, AC-2.9 | Validate document understanding metadata storage | High | |
| SCN-003 | AC-3.1, AC-3.2, AC-3.8 | Validate rich context generation with document summaries | Medium | |
| SCN-004 | AC-1.8, AC-3.10 | Validate backward compatibility with older documents | Medium | |

## Happy Path Scenarios

### SCN-001: Quote Extraction and Modal Display

Goal: Verify that an exact sentence quote is extracted from the chunk and shown inside the citation modal.

Linked acceptance criteria: AC-1.1, AC-1.2, AC-1.7

Steps:

1. Upload a document containing the text: "The company's revenue grew by 15% in Q3 due to international growth."
2. Ingest the document and start a chat session.
3. Ask the chatbot: "By how much did the company's revenue grow in Q3?"
4. Observe the citation tag `[Source 1]` in the answer.
5. Click on the citation tag.

Expected results:

- The CitationModal opens immediately.
- The highlighted text shows "The company's revenue grew by 15% in Q3 due to international growth."
- A "Show full context" toggle is visible.
- Clicking the toggle expands to show the full chunk text.

### SCN-002: Document Ingestion & Understanding Summary

Goal: Verify that document summaries, topics, and sections are created and stored in the database.

Linked acceptance criteria: AC-2.1, AC-2.4, AC-2.9

Steps:

1. Enable document understanding in settings.
2. Ingest a new PDF or markdown file.
3. Open a SQLite client (or run `sqlite3 data/knowledge_ingestion/app.db`) and query the `documents` table:
   `SELECT title, metadata_json FROM documents ORDER BY created_at DESC LIMIT 1;`

Expected results:

- The `metadata_json` contains a `doc_understanding` object.
- The object has a non-empty `summary` string, `topics` list with 3-7 items, and `sections` list representing headings.

## Edge Cases And Failure Paths

### SCN-EDGE-001: Document Understanding Skip on Large File

Goal: Verify that document understanding gracefully skips when the file text exceeds 100K characters.

Linked acceptance criteria: AC-2.6, AC-2.10

Steps:

1. Prepare a text file containing over 100,000 characters.
2. Ingest this file.
3. Check the backend server logs.
4. Verify the database metadata for this newly ingested document.

Expected results:

- Ingestion completes successfully without crashing.
- A warning log is present: "Skipping doc understanding: text exceeds 100K chars".
- The document record in SQLite does not contain `doc_understanding` metadata.

## Regression Checks

- Behavior that must still work:
  - Chats should work with documents that do not have `doc_understanding` data.
- Validation approach:
  - Click on a citation for an older document (without `quote_text`).
- Evidence to capture:
  - Confirm the CitationModal displays the full chunk text without errors, and no "Show full context" toggle is shown.

## Sign-Off

- Tested by: Antigravity
- Date: 2026-06-28
- Passed scenarios: SCN-001, SCN-002, SCN-003, SCN-004, SCN-EDGE-001
- Overall outcome: Pass
