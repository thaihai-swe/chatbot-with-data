# Feature Specification

## Metadata

- Feature name: Consolidate Settings Between .env and Setting UI
- Feature slug: 16-consolidate-settings
- Owner: Agent
- Status: Approved
- Last updated: 2026-05-23
- Related knowledge artifact(s): `analysis.md`, `proposal.md`

## Problem Statement

Currently, application configuration is fragmented. The `.env` file mixes immutable infrastructure credentials (e.g., API keys, database URLs) with mutable user preferences (e.g., chunk size, retrieval limits). The frontend Settings UI overwrites these user preferences in a JSON file that shadows the `.env` values, causing deployment confusion. Furthermore, the Chat UI contains advanced toggles that do not sync with the global Settings UI. We need a unified approach where `.env` handles system security exclusively, and the UI manages global user settings exclusively.

## Desired Outcomes

- Outcome 1: Clear separation of concerns between infrastructure deployment (via `.env`) and application behavior (via Settings UI).
- Outcome 2: A unified user experience where all user-configurable parameters, including Chat UI toggles, are found in the global Settings UI.

## Minimum Release Slice

- What ships in the first useful release:
  - Removal of all user-configurable default variables from `.env`.
  - Hardcoded application defaults for user settings, overridable by the Settings UI's backend store.
  - Merging Chat UI's per-session toggles into the global Settings UI state.
- What can wait:
  - Advanced role-based access control for settings.
  - Granular per-user profiles.

## Success Criteria

- SC-001: No user behavior settings (`RETRIEVAL_K`, `CHAT_MODEL`, toggles) are read from `.env` at runtime.
- SC-002: Changing an advanced toggle in the Settings UI immediately applies to subsequent chat requests.
- SC-003: The application boots successfully without user settings in the `.env` file.

## In Scope

- Migrating configuration schemas in `backend/schemas/settings.py` to stop using `os.getenv` for user variables.
- Updating `frontend/src/screens/Chat.jsx` to read global settings instead of local React state toggles.
- Updating `frontend/src/screens/SettingsScreen.jsx` and API routes to handle the unified settings schema.
- Hardcoding default fallback values for user settings in the backend code.

## Out Of Scope

- Implementing a migration script for existing `.env` values to `settings.json`. (We accept losing previous `.env` overrides).
- Adding new configuration features that do not already exist.

## Non-Goals

- Non-goal 1: Making system/security variables like API keys editable via the UI.
- Non-goal 2: Maintaining backward compatibility with user-defined `.env` values.

## Users And Stakeholders

- Primary users: System Administrators, End Users using the Chat UI.
- Secondary stakeholders: Developers deploying the application.

## User Stories And Key Scenarios

- US-001: As a user, I want all my AI chat configurations (model, retrieval size, AI features) in one central Settings UI, so I don't have to look in different places.
- US-002: As a deployer, I want `.env` to strictly require infrastructure secrets so I can template deployments easily without worrying about user preferences.

### Detailed Scenarios

- **Scenario 1 (Configuring System Defaults):**
  - **Given:** A fresh installation of the application.
  - **When:** The system boots with only security parameters in `.env`.
  - **Then:** The application uses hardcoded defaults for retrieval and models, and runs successfully.
- **Scenario 2 (Updating Global Settings):**
  - **Given:** A user navigating to the Settings UI.
  - **When:** They toggle `enable_intelligence` to `true` and save.
  - **Then:** The setting is persisted, and the next chat message automatically uses intelligence without requiring a per-chat toggle.

## Current Context

- The backend currently reads defaults like `CHAT_MODEL` and `RETRIEVAL_K` from `os.getenv` in `GlobalSettings`.
- `SettingsManager` saves overrides to `settings.json`.
- `Chat UI` holds toggles in local state (`advancedConfig`) and sends them as `payload.advanced_config`.
- Unchanged behavior to preserve: The actual backend execution logic for chunking, retrieval, and chat must behave the same given the same configuration values.

## Dependencies And External Touchpoints

- DEP-001: Settings API (`backend/routers/settings.py`)
- DEP-002: Chat API (`backend/routers/chat.py`)

## Functional Requirements

### REQ-001
Requirement: Remove user configuration defaults from `.env` and `os.getenv` calls.
Why it matters: Enforces the separation of system vs. user state.
Impacted users or scenarios: Deployers.
Related success criteria: SC-001, SC-003.
Priority: Must Have
Acceptance notes: Code inspection shows no `os.getenv` for variables like `CHAT_MODEL` or `RETRIEVAL_K`.
Validation surface: Code review.

### REQ-002
Requirement: Merge Chat UI advanced toggles into the Global Settings schema.
Why it matters: Unifies the user experience.
Impacted users or scenarios: US-001.
Related success criteria: SC-002.
Acceptance notes: The chat sidebar toggles are removed or moved to the Settings UI, and the chat API reads from the global settings.
Validation surface: Manual UI test.

## Non-Functional Requirements

- NFR-001 Performance: Settings retrieval must be fast (already handled via in-memory caching in `SettingsManager`).
- NFR-002 Supportability: Deployments are simpler as `.env` is minimal.

## Constraints

- Technical constraints: Must update the Chat payload schema to match the backend expectations now that `advanced_config` is globally managed.

## Assumptions

- ASM-001: Users are acceptable with losing their previous `.env` user configurations upon upgrade.

## Risks

- RISK-001 Risk: Chat API breaks if it expects `advanced_config` in the payload but it's no longer sent by the frontend.
  Mitigation: Update the backend Chat API to merge the payload config with global settings, or pull directly from global settings if omitted.

## Open Questions
None.

## Acceptance Criteria

- [ ] AC-001 Linked requirement(s): REQ-001
  Validation method: Manual review
  Proof target: Verify `.env` and `backend/schemas/settings.py` no longer use environment variables for user settings.
- [ ] AC-002 Linked requirement(s): REQ-002
  Validation method: Manual test
  Proof target: Toggle a setting in the Settings UI, send a chat message, and verify in the backend logs that the setting was applied.

## Notes
None.
