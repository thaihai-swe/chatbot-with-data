# Execution Tasks

## Phase 1: Backend Schema Consolidation

- `[x]` **TASK-1.1**: Update `backend/schemas/settings.py`
  - Target: `backend/schemas/settings.py`
  - Action: Remove `os.getenv` defaults from `IngestionSettings`, `LLMSettings`, and `SafetySettings`. Replace with sensible static hardcoded defaults. Add the missing advanced toggles (`enable_intelligence`, `enable_collection_routing`, etc.) to `RetrievalSettings`.
  - Proof: Run `pytest backend/tests/test_settings.py` or manually verify the settings endpoint `GET /settings` returns the expected defaults.
  - Evidence: Schema instantiation succeeds with static defaults.

- `[x]` **TASK-1.2**: Cleanup legacy Settings class
  - Target: `backend/config.py`
  - Action: Remove the duplicated behavioral settings (e.g., `context_window_size`, `max_history_turns`, `min_similarity_threshold`, `min_results_count`, `safety_risk_threshold`, `chat_model`) from the `Settings` dataclass to avoid two sources of truth.
  - Proof: Verify application boots without validation errors.
  - Evidence: Application imports without syntax/validation errors.

## Phase 2: Backend Chat API Update

- `[x]` **TASK-2.1**: Update Chat Schemas
  - Target: `backend/schemas/chat.py`
  - Action: Remove `AdvancedRetrievalConfig` and the `advanced_config` field from `ChatTurnCreate`.
  - Proof: Check syntax and pydantic validation.

- `[x]` **TASK-2.2**: Update Chat Router
  - Target: `backend/routers/chat.py`
  - Action: In `submit_turn` and `submit_turn_stream`, stop passing `payload.advanced_config`. Ensure the orchestrator and retrieval steps dynamically read from `get_config().retrieval`.
  - Proof: Verified by successful instantiation without syntax errors and pydantic schema passes.

## Phase 3: Frontend API Call Update

- `[x]` **TASK-3.1**: Cleanup ChatUI payload
  - Target: `frontend/src/screens/Chat.jsx`
  - Action: Remove `advancedConfig` state. Remove the `advanced_config` property from the payload sent to `/chat/sessions/{session_id}/turns/stream`.
  - Proof: Verify React compiles. frontend and verify the Chat page renders without the sidebar toggles.

- `[x]` **TASK-3.2**: Add Toggles to Settings UI
  - Target: `frontend/src/screens/SettingsScreen.jsx`
  - Action: Add the new advanced toggles (e.g., `enable_intelligence`, `enable_rewriting`, `enable_dynamic_routing`, `enable_expansion`, `enable_reranking`, `enable_parent_child`, `enable_collection_routing`, `enable_multi_hop`) to the Global Settings UI, specifically mapping to `RetrievalSettings`.
  - Proof: Verify toggles update the state and successfully save to `GET/PUT /settings`.
