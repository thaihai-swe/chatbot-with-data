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
