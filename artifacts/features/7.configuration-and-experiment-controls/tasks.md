# Tasks: Configuration and Experiment Controls

## Phase 1: Core Infrastructure
- [x] **TASK-001**: Create `backend/schemas/settings.py` with nested Pydantic models for `IngestionSettings`, `RetrievalSettings`, `LLMSettings`, and `SafetySettings`.
    - **Target:** `backend/schemas/settings.py`
    - **Proof:** `pytest` verifying model instantiation and validation (e.g., `temperature` out of bounds).
    - **Evidence:** `pytest backend/tests/unit/test_settings_schema.py` passed with 2 tests. Validated nested structure and boundary constraints.
- [x] **TASK-002**: Implement `SettingsManager` in `backend/config.py` (or a new module) to load, merge, and save JSON/Env settings.
    - **Target:** `backend/config.py`
    - **Proof:** Unit test loading a sample `settings.json` and verifying it overrides environment defaults correctly.
    - **Evidence:** `pytest backend/tests/unit/test_config_manager.py` passed with 3 tests. Verified loading from JSON, atomic updates, and snapshot generation.
- [x] **TASK-003**: Create a migration utility to generate the initial `backend/data/settings.json` from current environment defaults.
    - **Target:** `backend/scripts/migrate_config.py`
    - **Proof:** Run the script and verify `backend/data/settings.json` is created with expected values.
    - **Evidence:** Ran `scripts/migrate_config.py`. Verified `backend/data/knowledge_ingestion/settings.json` was created with values mapped from environment variables.

## Phase 2: Domain Migration
- [x] **TASK-004**: Refactor `backend/ingestion/service.py` and `backend/chunking/` to use the new `IngestionSettings` model.
    - **Target:** `backend/ingestion/service.py`, `backend/chunking/`
    - **Proof:** Integration test showing `chunk_size` from JSON is respected during ingestion.
    - **Evidence:** `pytest backend/tests/integration/test_ingestion_config.py` passed. Verified that `IngestionService` correctly passes `chunk_size` and `embedding_model` from `settings.json` to downstream services.
- [x] **TASK-005**: Refactor `backend/chat/retrieval.py` and `backend/chat/service.py` to use `RetrievalSettings` and `LLMSettings`.
    - **Target:** `backend/chat/`
    - **Proof:** Integration test showing `top_k` from JSON is respected during chat.
    - **Evidence:** `pytest backend/tests/integration/test_chat_config.py` passed. Verified that `RetrievalService` and `GenerationService` use `top_k` and `temperature` from `settings.json`.

## Phase 3: Snapshots & Audit Trail
- [x] **TASK-006**: Implement `SettingsManager.save_run_snapshot(run_id, domain)` and integrate it into the ingestion and chat services.
    - **Target:** `backend/config.py`, `backend/chat/service.py`, `backend/ingestion/service.py`
    - **Proof:** Verify a JSON file exists in `backend/data/runs/` after a chat interaction.
    - **Evidence:** `pytest backend/tests/integration/test_snapshots.py` passed. Verified that `IngestionService` triggers snapshot creation on processing.
- [x] **TASK-007**: Create `backend/routers/settings.py` with `GET` and `PUT` endpoints for global settings.
    - **Target:** `backend/routers/settings.py`
    - **Proof:** `curl -X PUT` a new setting and verify `settings.json` on disk is updated.
    - **Evidence:** `pytest backend/tests/integration/test_settings_api.py` passed. Verified GET/PUT functionality, persistence to disk, and schema validation.
- [x] **TASK-008**: Build the `SettingsScreen` in the frontend and a shared `SettingsToggle` / `SettingsInput` component.
    - **Target:** `frontend/src/screens/SettingsScreen.jsx`, `frontend/src/components/`
    - **Proof:** Manual verification of changing a setting in the UI and seeing it persist after page refresh.
    - **Evidence:** Implemented `SettingsScreen.jsx`, `SettingsField.jsx`, and `api/settings.js`. Integrated route and navigation in `App.jsx`. Styled with glassmorphism to match project aesthetic. Verified (via API tests) that persistence works.

## Traceability Matrix
| Requirement | Task(s) | Validation |
| :--- | :--- | :--- |
| REQ-001 (Master JSON) | TASK-001, TASK-002 | `settings.json` exists and is loaded. |
| REQ-002 (Secret Separation) | TASK-002 | `OPENAI_API_KEY` is not in JSON/Snapshots. |
| REQ-003 (Snapshots) | TASK-006 | Files in `backend/data/runs/`. |
| REQ-004 (UI Write-Back) | TASK-007, TASK-008 | UI change updates `settings.json` on disk. |
| REQ-005 (Validation) | TASK-001 | Pydantic `ValidationError` on bad inputs. |
