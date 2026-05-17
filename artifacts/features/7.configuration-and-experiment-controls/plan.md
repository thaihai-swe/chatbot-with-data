# Implementation Plan: Configuration and Experiment Controls

## Metadata

- Feature name: Configuration and Experiment Controls
- Feature slug: configuration-and-experiment-controls
- Related spec: `artifacts/features/7.configuration-and-experiment-controls/spec.md`
- Related design: `artifacts/features/7.configuration-and-experiment-controls/design.md`
- Status: Approved
- Last updated: 2026-05-17

## Execution Strategy

The implementation will follow a "Parallel & Swap" approach. We will build the new configuration infrastructure alongside the existing `Settings` class, then incrementally migrate each domain (Ingestion, Retrieval, Chat) to the new system. Finally, we will expose the UI controls and enable the snapshotting logic.

## Phased Rollout

### Phase 1: Core Infrastructure (The Foundation)
*   **Goal:** Create the Pydantic models and `SettingsManager` that can load from both `.env` and JSON.
*   **Boundaries:** `backend/config/`
*   **Proving Strategy:** Unit tests verifying that settings are correctly merged and validated.

### Phase 2: Domain Migration (The Wiring)
*   **Goal:** Refactor existing services to use the new settings hierarchy.
*   **Boundaries:** `backend/chat/`, `backend/ingestion/`, `backend/chunking/`
*   **Proving Strategy:** Integration tests showing that changing a value in `settings.json` changes the behavior of these services.

### Phase 3: Run Artifacts & Snapshots (The Audit Trail)
*   **Goal:** Implement the automatic snapshotting of configurations for every significant run.
*   **Boundaries:** `backend/chat/service.py`, `backend/ingestion/service.py`
*   **Proving Strategy:** Verify that files are created in `backend/artifacts/runs/` after a chat turn or ingestion.

### Phase 4: UI Persistence & Settings API (The Control)
*   **Goal:** Expose REST endpoints for the frontend to read and update the global configuration.
*   **Boundaries:** `backend/routers/`, `frontend/src/api/`, `frontend/src/screens/`
*   **Proving Strategy:** Manual verification of the UI settings panel and automatic update of the `settings.json` file on disk.

## Impacted Boundaries

### Backend
- `backend/config.py`: Will be replaced or heavily refactored.
- `backend/main.py`: Will need to initialize the new configuration system.
- All Services: Will change their dependency from `Settings` to the new nested models.

### Frontend
- New `SettingsScreen.jsx`: To provide a centralized control panel.
- `api/settings.js`: New client for settings management.

## Proving Strategy

- **Automated:**
    *   `pytest backend/tests/unit/test_config.py`: Validates merging and schema validation.
    *   `pytest backend/tests/integration/test_settings_persistence.py`: Validates UI write-back and snapshots.
- **Manual:**
    *   Edit `settings.json` manually -> verify change in Chat/Ingestion behavior.
    *   Change setting in UI -> verify `settings.json` content on disk.

## Rollback Posture

The new system is additive. If it fails, we can revert the dependency injection in `main.py` back to the old `Settings` class (as long as we haven't deleted it yet). The `settings.json` file is just a data artifact and does not affect the DB schema.
