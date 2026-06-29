# Proposal: Collection Scoped Chat Sessions

## 💡 The Problem

Currently, chat sessions are stored globally. When a user selects a collection/notebook, they see the same global list of chat sessions in the sidebar. This forces users to manually select relevant collection scopes each time they start a chat, and mixes conversation histories of entirely different notebooks, causing UX friction and context confusion.

## 🎯 Objectives

1. **Scoped Storage and Loading:** Ensure chat sessions are stored and loaded strictly by their associated Collection/Notebook.
2. **Database Normalization:** Refactor the database schema to replace the multi-collection join table with a direct `collection_id` column in `chat_sessions` to enforce a strict 1-to-1 relationship between sessions and collections.
3. **Seamless UX Transitions:** Automatically load the appropriate session history when a collection is selected, and clear the active chat state when switching collections.

## 🛠 High-Level Approach

- **Database Schema & Migrations:** Update `SCHEMA_STATEMENTS` in [runner.py](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/migrations/runner.py) to add `collection_id` to `chat_sessions`, drop the obsolete `chat_session_collections` table, and write a database migration step `0006_single_collection_chat` to backfill existing mappings.
- **Repository & Models:** Update `ChatSession` model and [ChatRepository](file:///Users/thaihai-swe/Desktop/chatbot-with-data/backend/repositories/chat_repository.py) to read and write a single `collection_id` directly to the `chat_sessions` table.
- **REST Endpoints:** Refactor the GET `/chat/sessions` endpoint to accept an optional `collection_id` query parameter for scoped queries. Update POST `/chat/sessions` to accept a single `collection_id` in the schema payload.
- **Frontend Workspace & Routing:** Map session list queries to the active `selectedCollectionId`. Clear the active session and message history when the selected collection changes, directing users to start a new chat or load an existing session for the new collection.

## ⚠️ Known Constraints / Risks

- **Backward Compatibility:** Legacy sessions that lack a collection association must be handled gracefully (either associated with a default collection or excluded from collection-specific sidebars).
- **Frontend Routing Sync:** Ensure active sessions loaded via URL (`/chat/:sessionId`) automatically select and lock the correct associated collection in the Sources panel on load.

## 🧩 Gray Areas Resolved

- **Unassigned Legacy Sessions:** Legacy sessions without collections will be excluded from the sidebar but remain accessible if navigated to directly via URL.
- **Strict 1-to-1 Mapping:** Standardizing on a single `collection_id` strictly at both db and code level rather than using joint-table abstractions.

## ✅ Success Criteria

- [ ] A SQLite schema migration `0006_single_collection_chat` is registered and executes successfully.
- [ ] GET `/chat/sessions?collection_id={id}` returns only sessions linked to that collection.
- [ ] Selecting a collection dynamically updates the sidebar session list.
- [ ] Switching collections automatically closes the active chat session.
- [ ] Loading a session via URL resolves and selects its collection in the Sources panel.
