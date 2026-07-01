# Frontend UI — Anti-Patterns

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Embedding API Calls Inside Reusable Components

**Why it fails:** Components become coupled to specific backend endpoints, making them impossible to reuse across screens.

**What to do instead:** Keep API calls in screen components. Pass data down to reusable components via props.

**Citation:** Established pattern in `frontend/src/screens/` (screens fetch) and `frontend/src/components/` (components display).

---

## Mixing SSE Stream Handling with UI State

**Why it fails:** Directly coupling SSE event parsing to React state management creates tight coupling between the streaming format and the component lifecycle.

**What to do instead:** Abstract SSE handling into a service or hook that emits cleanly-typed events. The UI subscribes to those events.

**Citation:** `backend/chat/streaming.py` sends token events; frontend should consume via an abstraction layer.

---

## Blocking Screen UI with Loader Spinners During Background Polling

**Why it fails:** Replacing the entire document list or page with a full-screen loader spinner while polling background processes (like ingestion) makes the page unusable and flashes the UI during updates.

**What to do instead:** Run the polling logic silently in the background (with no spinner) so the user can interact with other documents while the status updates in-place.

**Citation:** Initially the app blocked the screen with "Synchronizing inventory..." during file ingest, which locked the library screen. Refactored to poll silently using background intervals.
