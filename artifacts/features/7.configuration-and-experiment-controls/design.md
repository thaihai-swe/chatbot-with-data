# Technical Design: Configuration and Experiment Controls

## Metadata

- Feature name: Configuration and Experiment Controls
- Feature slug: configuration-and-experiment-controls
- Related spec: `artifacts/features/7.configuration-and-experiment-controls/spec.md`
- Related requirements review: `artifacts/features/7.configuration-and-experiment-controls/requirements-review.md`
- Status: Approved
- Last updated: 2026-05-17

## Design Summary

The system will transition to a hierarchical configuration model using Pydantic. Secrets and infrastructure settings (DB paths, API keys) will continue to be sourced from environment variables/`.env`, while all "behavioral" settings (chunking, retrieval, safety thresholds) will be sourced from a `backend/config/settings.json` file. A new `SettingsManager` will handle the merging of these sources, handle atomic writes for UI-driven updates, and generate timestamped JSON snapshots for every chat/ingestion run.

## Current State And Context

- **Existing system baseline:** A monolithic `Settings` dataclass in `backend/config.py` that reads strictly from environment variables.
- **Relevant repository patterns:** Dataclasses for configuration, dependency injection for settings in FastAPI routers.
- **Unchanged behavior:** The use of `.env` for `OPENAI_API_KEY` and directory paths must be preserved for security and environment-specific setup.

## Design Drivers

- **REQ-001 (Master JSON):**
  Design implication: Introduce a `settings.json` file and a Pydantic model that mirrors its structure.
- **REQ-002 (Secret Separation):**
  Design implication: The `SettingsManager` must combine `os.getenv` values with `settings.json` values, prioritizing JSON for behavior but `.env` for secrets.
- **REQ-003 (Snapshots):**
  Design implication: Every service call (chat/ingestion) must invoke `SettingsManager.create_snapshot()` before execution.
- **REQ-004 (UI Write-Back):**
  Design implication: Add a `PUT /api/settings` endpoint that validates input and performs an atomic write to `settings.json`.
- **NFR-002 (Reliability):**
  Design implication: Use Pydantic's strict validation to fail-fast if `settings.json` is corrupted or contains out-of-bounds values.

## Proposed Architecture

### Major Components
1.  **`SettingsModel` (Pydantic):** A nested model defining the structure of `settings.json`.
2.  **`SettingsManager`:** A service responsible for:
    *   Loading/Merging config from `.env` and `settings.json`.
    *   Exporting "Effective Config" (JSON-ready dict without secrets).
    *   Writing updates to `settings.json`.
3.  **`SettingsRouter`:** New FastAPI endpoints for fetching and updating settings.

### Interaction Model
1.  On startup, `SettingsManager` loads the baseline.
2.  FastAPI routers use a dependency (e.g., `get_config`) to access the current settings.
3.  When a chat starts, the `ChatService` calls `SettingsManager.save_run_artifact(run_id)`.
4.  When the UI sends an update, the `SettingsRouter` calls `SettingsManager.update_settings(new_data)`, which validates and writes to disk.

## Data Flow And Interfaces

### Inputs
*   `.env` (Environment variables)
*   `backend/data/settings.json` (Behavioral settings)
*   `PUT /api/settings` (UI overrides)

### Storage
*   `backend/artifacts/runs/run_{timestamp}_{id}.json` (Run snapshots)
*   `backend/data/settings.json` (Persistent master config)

## Design Decisions And Tradeoffs

- **Decision: Pydantic over standard JSON/Dict**
  Why chosen: Automatic type casting, range validation (e.g., `Field(ge=0, le=1)` for temperature), and clear error messages.
  Tradeoff: Slightly more boilerplate for model definitions.

- **Decision: Local JSON file over Database Storage for config**
  Why chosen: Simplifies manual edits (user can open `settings.json` in VS Code) and avoids database dependency for core system bootstrapping.
  Tradeoff: Requires manual handling of file locks/concurrency.

- **Decision: Atomic writes via temporary file**
  Why chosen: Prevents data loss if the system crashes or power fails mid-write.
  Tradeoff: Minimal performance overhead for file operations.

## Brownfield Integration Notes

- **Boundary:** We must replace all references to `backend.config.get_settings()` with the new `ConfigManager`.
- **Migration:** I will create a migration script or a "one-time bootstrapper" that reads current `.env` behavioral defaults and populates the initial `settings.json`.

## Non-Functional Design Considerations

- **Reliability:** If `settings.json` is invalid, the backend will log a critical error and fall back to hard-coded safe defaults or refuse to start.
- **Security:** The `save_run_artifact` method will explicitly exclude fields marked as `sensitive` in the Pydantic model.

## Open Questions

- **Q-001:** Should we support "profiles" (e.g., `settings.dev.json` vs `settings.prod.json`)?
  Next step: Out of scope for now. Stick to a single `settings.json` with environment variable overrides for infra-level differences.
