# Feature Specification: Configuration and Experiment Controls

## Metadata

- Feature name: Configuration and Experiment Controls
- Feature slug: configuration-and-experiment-controls
- Owner: Unassigned
- Status: Approved
- Last updated: 2026-05-17
- Related knowledge artifact(s): `prd-requirement.md`, `proposal.md`

## Problem Statement

The system requires a centralized way to manage behavior across the RAG pipeline. Currently, settings for ingestion, chunking, retrieval, generation, safety, and evaluation are either hard-coded or scattered. This makes experiments non-reproducible and prevents users from tuning the system without direct code modifications.

## Desired Outcomes

- A single source of truth for all behavior-shaping parameters using a JSON-based configuration model.
- Guaranteed experiment reproducibility by capturing "effective configuration" snapshots for every run.
- Seamless persistence of behavioral changes made through the UI directly to the master configuration.

## Success Criteria

- SC-001: All core RAG pipeline settings are centrally managed in a documented JSON structure.
- SC-002: Every chat or ingestion run generates a reproducible "effective config" JSON artifact.
- SC-003: UI-driven configuration changes persist to the master JSON file for subsequent runs.

## In Scope

- **Master Configuration:** A primary `settings.json` file on the backend.
- **Run Artifacts:** Automatic generation of timestamped JSON snapshots for every chat session or ingestion job.
- **Secret Separation:** Integration with `.env` to keep API keys and credentials out of the behavioral JSON.
- **UI Persistence:** Backend logic to update the master JSON file when settings are changed via the frontend.
- **Schema Validation:** Strict validation (e.g., Pydantic) to ensure settings remain within valid bounds.

## Out Of Scope

- Managing infrastructure secrets (DB passwords, API keys) inside the JSON file (these remain in `.env`).
- Multi-user configuration isolation (all UI changes affect the global system state for now).

## Users And Stakeholders

- **Engineers/Learners:** Tuning RAG performance across different models, chunk sizes, and retrieval strategies.
- **Reviewers:** Validating that experiment results are driven by explicit settings rather than implementation side-effects.

## User Stories And Key Scenarios

- US-001: As a user, I can change the `top_k` or `chunk_size` in a JSON file or UI panel and see the impact immediately in the next run.
- US-002: As an experimenter, I can look at a "run config" JSON from last week and know exactly which settings produced a specific groundedness score.
- US-003: As a developer, I can safely add new configuration flags without worrying about manual syntax errors crashing the system, thanks to automatic validation.

## Current Context

The system has multiple RAG components (ingestion, retrieval, etc.) but lacks a unified control layer. This feature introduces that layer as the final architectural block.

## Dependencies And External Touchpoints

- DEP-001: All backend services must be refactored to consume settings from the new configuration manager.
- DEP-002: Frontend components must be updated to fetch and update settings via new REST endpoints.

## Functional Requirements

### REQ-001: Master JSON Configuration
Requirement: The system must use a central `settings.json` file to store all behavioral parameters (chunking, retrieval, safety, etc.).
Why it matters: Provides a single, human-readable source of truth.
Acceptance notes: Changing a value in `settings.json` and restarting (or refreshing) the service applies the change.

### REQ-002: Secret/Config Separation
Requirement: The configuration system must resolve environment variables (from `.env`) for sensitive fields while keeping logic settings in JSON.
Why it matters: Prevents leaking API keys into shared configuration files or run artifacts.
Acceptance notes: The JSON file may reference `"${OPENAI_API_KEY}"`, but the actual key must never be written to a run artifact.

### REQ-003: Effective Run Snapshots
Requirement: For every chat turn or ingestion job, the system must save a "snapshot" JSON file containing the exact configuration used.
Why it matters: Essential for auditability and experiment reproduction.
Acceptance notes: A new JSON file is created for each run in a designated `artifacts/runs/` directory.

### REQ-004: UI Persistence (Write-Back)
Requirement: When settings are modified in the frontend UI, the backend must update the master `settings.json` file.
Why it matters: Ensures user preferences survive restarts and apply to future sessions.
Acceptance notes: Toggling a setting in the UI updates the physical `settings.json` file on the server.

### REQ-005: Schema & Bounds Validation
Requirement: The system must validate all configuration inputs against a schema (e.g., Pydantic) to prevent invalid values.
Why it matters: Prevents system crashes from typos or illogical settings (e.g., negative `top_k`).
Acceptance notes: Attempting to set an invalid value via UI or JSON results in a clear error message.

## Non-Functional Requirements

- NFR-001 Reliability: Configuration errors must prevent the system from starting or running an operation rather than defaulting to hidden behaviors.
- NFR-002 Security: Run snapshots must be scrubbed of any PII or sensitive environment variables.

## Constraints

- Storage: Configuration and snapshots must be stored in the local file system as JSON.
- Concurrency: The backend must handle file-write locks to prevent corruption during UI-driven updates.

## Assumptions

- ASM-001: The user wants a global configuration change when using the UI, rather than per-session overrides.
- ASM-002: A standard JSON structure is sufficient for the complexity of the current RAG pipeline.

## Risks

- RISK-001: Concurrency issues if multiple settings are changed rapidly.
  Mitigation: Use atomic file writes or a simple file-lock mechanism.
- RISK-002: Configuration bloat as more features are added.
  Mitigation: Use a nested, domain-specific JSON structure (e.g., `ingestion`, `retrieval`, `llm`).

## Acceptance Criteria

- [ ] AC-001: A `settings.json` file successfully controls `chunk_size` and `retrieval_mode`.
- [ ] AC-002: Every chat interaction produces a timestamped JSON file in `backend/artifacts/runs/`.
- [ ] AC-003: Changing a setting in the UI and restarting the backend shows the new value is still active.
- [ ] AC-004: Providing an invalid JSON value (e.g., string instead of int) triggers a validation error.

## Notes
Implementation will likely involve a `ConfigService` in the backend that uses Pydantic for validation and handles file I/O.
