# Testing Scenarios

## Purpose

This guide validates that chat sessions are scoped strictly to the selected Collection/Notebook, database constraints are enforced, switching collections resets feed states, and loading a session via URL resolves collection contexts.

## Scope

- Feature name: Collection Scoped Chat Sessions
- Feature slug: 5.0-session-by-collection
- Delivered scope under test: DB schema migration, repository filters, endpoint query parameters, frontend state and router links.
- Out of scope: Multi-collection session support.

## Estimated Time

- Approximate total time: 10 minutes

## Prerequisites

- Required environment: Local development server (`npm run dev` and `python3 backend/main.py`).
- Required accounts or permissions: Local development access.
- Required services or dependencies: SQLite, Weaviate.
- Required data or fixtures: Two collections created with at least one document in each.

## Setup

- Step 1: Run local backend and frontend development servers.
- Step 2: Ensure database migrations are applied.
- Step 3: Open the browser workspace at `http://localhost:5173/chat`.

## Scenario Matrix

| Scenario | Linked AC | Goal | Priority | Notes |
|----------|-----------|------|----------|-------|
| SCN-001  | AC-001, AC-002 | Verify sidebar displays only collection-specific sessions | High | Happy Path |
| SCN-002  | AC-002    | Verify collection change clears active session and chat feed | High | Happy Path |
| SCN-003  | AC-002    | Verify direct URL entry auto-aligns left sources panel collection | High | Edge Case |

## Happy Path Scenarios

### SCN-001: Collection Scoped Sidebar

Goal: Verify session history displays only sessions matching the currently selected collection.

Linked acceptance criteria: AC-001, AC-002

Steps:

1. Select "Collection A" in the left Sources panel.
2. Type a message in the chat input and hit send. Verify a new session (Session A1) is created in the sidebar.
3. Select "Collection B" in the left Sources panel.
4. Type a message and send. Verify a new session (Session B1) is created.
5. Switch back to "Collection A".

Expected results:

- When "Collection A" is active, only Session A1 is visible in the sidebar list. Session B1 is hidden.
- When "Collection B" is active, only Session B1 is visible. Session A1 is hidden.

---

### SCN-002: Collection Switch Reset

Goal: Verify switching collections closes the active session and clears the feed.

Linked acceptance criteria: AC-002

Steps:

1. Select "Collection A" and open "Session A1" to view messages.
2. Click on "Collection B" in the left Sources panel.

Expected results:

- The central chat feed clears immediately.
- The URL redirects from `/chat/SessionA1` back to `/chat`.
- The sidebar updates to display only Collection B's sessions.

---

## Edge Cases And Failure Paths

### SCN-003: Direct URL Load Resolution

Goal: Verify opening a direct URL to a session resolves and auto-selects its collection.

Linked acceptance criteria: AC-002

Steps:

1. Copy the URL of Session A1 (e.g. `http://localhost:5173/chat/SessionA1`).
2. Close the browser tab.
3. Open a new tab and paste the URL.

Expected results:

- The page loads with Session A1's messages visible.
- The left Sources panel automatically selects "Collection A" and checks its documents.

---

## Regression Checks

- **Behavior that must still work:** Ingesting files, re-ingesting documents, citations rendering, product studio generation.
- **Validation approach:** Verify that clicking "View" on a document in the library loads chunks and notes correctly, and clicking "Generate" inside the chat creates products correctly.
- **Evidence to capture:** Browser screenshots of the document detail drawer showing populated chunks.

## Notes For Testers

- **Known limitations:** Legacy sessions without collection associations will not appear in the sidebar scoped lists.
- **What should be escalated immediately:** Database locks, Pydantic validation errors, or empty chunk lists when viewing documents.

## Sign-Off

- Tested by: Antigravity
- Date: 2026-06-29
- Passed scenarios: SCN-001, SCN-002, SCN-003
- Failed scenarios: None
- Deferred scenarios: None
- Overall outcome: PASS
- Evidence or screenshots linked: None
