# Implementation Plan

## Metadata
- Feature name: Consolidate Settings Between .env and Setting UI
- Related spec: `spec.md`
- Related requirements review: `requirements-review.md`
- Owner: Agent
- Status: Draft
- Last updated: 2026-05-23

## Plan Summary
We will execute the settings consolidation in three phases to minimize risk:
1. **Schema Update:** Update `GlobalSettings` in the backend to remove `os.getenv` defaults and hardcode fallbacks. Clean up duplicated fields in the legacy `config.py` `Settings` class. Update `RetrievalSettings` to include the advanced toggles.
2. **Backend API Cleanup:** Remove `advanced_config` from the chat request payload schema (`ChatTurnCreate`). Update `backend/routers/chat.py` and downstream services to pull retrieval settings dynamically from `get_config().retrieval`.
3. **Frontend Unified UI:** Strip the "Retrieval Config" toggles and local state out of `Chat.jsx`. Migrate those toggles to `SettingsScreen.jsx`, binding them to the global settings state.

## Execution Context
- Design reference: `backend/schemas/settings.py` controls the global defaults.
- Unchanged behavior that must be preserved: Core ingestion and retrieval behaviors should operate identically, they will just pull flags from a consolidated source rather than per-request overrides.

## First Delivery Slice
- Smallest useful slice: Updating the backend schemas and `SettingsManager` to sever the `.env` dependency for user settings.
- Why this slice goes first: It is the foundational layer. The frontend cannot be updated until the backend `GlobalSettings` schema accepts the new toggles.
- What proof should exist: A backend unit test or manual check showing that missing `.env` fields do not crash the app, and that settings update successfully via `/settings`.

## Technical Approach
- Chosen approach: Hardcoded static defaults in Pydantic models.
- Key interfaces or contracts: `ChatTurnCreate` (removes `advanced_config`), `GlobalSettings` (adds advanced toggles to `RetrievalSettings`).

## Requirements And Constraints
- REQ-001 (Remove user config defaults from `.env`):
  Implementation note: Affects `backend/schemas/settings.py` and `backend/config.py`.
- REQ-002 (Merge Chat UI toggles into Global Settings):
  Implementation note: Affects `Chat.jsx` and `SettingsScreen.jsx`.

## Impacted Areas
- Services or modules: Chat Router, Settings Router, Settings Manager
- APIs or interfaces: `POST /chat/sessions/{session_id}/turns/stream`
- UI or UX: `SettingsScreen.jsx` and `Chat.jsx` sidebar.

## Protected Behavior
- Behavior that must not regress: Core chat logic, retrieval logic, routing logic must continue to conditionally branch based on the settings flags.

## Affected Files
- `backend/schemas/settings.py`: Strip `os.getenv`, add advanced toggles to `RetrievalSettings`.
- `backend/config.py`: Remove duplicate behavioral settings from `Settings` dataclass.
- `backend/schemas/chat.py`: Remove `AdvancedRetrievalConfig` and `advanced_config`.
- `backend/routers/chat.py`: Stop parsing `payload.advanced_config`.
- `frontend/src/screens/Chat.jsx`: Remove local `advancedConfig` state and sidebar checkboxes.
- `frontend/src/screens/SettingsScreen.jsx`: Add advanced toggles.

## Execution Phases

### Phase 1: Backend Schema Consolidation
Goal: Decouple user settings from `.env` and merge the advanced toggles into `RetrievalSettings`.
Entry proof: App runs.
Exit proof: `GlobalSettings` loads with hardcoded defaults.

### Phase 2: Backend Chat API Update
Goal: Remove per-turn overrides.
Entry proof: Phase 1 complete.
Exit proof: `POST /chat/sessions/{session_id}/turns/stream` works without `advanced_config` payload.

### Phase 3: Frontend UI Consolidation
Goal: Unify Settings UI and remove Chat UI local toggles.
Entry proof: Phase 2 complete.
Exit proof: Toggling a setting in the Settings page applies to the next chat message.

## Validation Strategy
- Manual verification: Start app without user configs in `.env`, verify default settings populate in UI. Verify toggling a feature in the Settings UI affects the chat response.

## Rollout Plan
- Release approach: Direct update, breaking change to existing users' `.env` preferences (accepted in spec).

## Risks And Mitigations
- RISK-001 Risk: Frontend crashes if the backend `GlobalSettings` model requires new fields that the old frontend payload doesn't send.
  Mitigation: Deploy backend and frontend changes together. Ensure static defaults in Pydantic avoid strict required fields during migration.

## Open Questions
- None.
