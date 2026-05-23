# Analysis: Consolidate Settings Between .env and Setting UI

## Metadata

- Investigation name: Consolidate Settings Between .env and Setting UI
- Feature or issue slug: 16-consolidate-settings
- Owner: Agent
- Last updated: 2026-05-23

## Scope

- What is being investigated: How settings and configurations are currently handled across the frontend (Chat UI, Setting UI) and backend (`.env`, config handling), with the goal of separating system/security settings from user configurations.
- What is explicitly out of scope: Actually implementing the settings consolidation. This is purely research.

## Current State

- Observed current behavior:
  - There are two places for settings in the frontend: `Settings UI` (global overrides) and `Chat UI` (per-request toggles like `enable_intelligence`).
  - `.env` contains feature defaults which the backend uses to populate `GlobalSettings` via `os.getenv`.
  - The Settings UI loads `GlobalSettings` and its updates are saved to `data/knowledge_ingestion/settings.json`, effectively shadowing `.env` values without changing the file.
- Relevant boundaries or components:
  - `frontend/src/screens/SettingsScreen.jsx`, `frontend/src/components/SettingsField.jsx`, `frontend/src/screens/Chat.jsx`.
  - `backend/.env`, `backend/routers/settings.py`, `backend/config.py` (`SettingsManager`), `backend/schemas/settings.py` (`GlobalSettings`).
- Unchanged behavior that must be preserved:
  - System and security values must stay strictly in `.env`.
  - Settings functionality such as the ability to customize user settings must not break.

## Decision-Ready Summary

- What matters most: Distinguishing between immutable infrastructure/security variables (to remain exclusively in `.env`) and mutable user configurations (to be moved to the Settings UI/database exclusively or default driven).
- Strongest supported conclusion: The current architecture mixes infrastructure settings (`OPENAI_API_KEY`, `WEAVIATE_URL`) and mutable user settings (`RETRIEVAL_K`, `CHAT_MODEL`) inside `.env` as defaults. The frontend relies on shadowing these defaults via `settings.json`. The `Chat UI` manages advanced toggles via local React state that are not synchronized with the `Settings UI` globals.
- Single next proving step: Define the exact schema separation and migration plan in a specification.

## Findings

- Finding: System/Security variables vs User variables are mixed.
  Evidence: `.env` and `GlobalSettings` both hold `WEAVIATE_URL` alongside `RETRIEVAL_K` and `CHAT_MODEL`.
  Type: Fact
  
- Finding: `Settings UI` shadows `.env` defaults.
  Evidence: `SettingsManager` in `backend/config.py` writes UI overrides to `settings.json`.
  Type: Fact
  
- Finding: `Chat UI` settings are isolated from `Settings UI`.
  Evidence: `Chat UI` stores advanced configurations in React state and passes them via `payload.advanced_config` instead of the global settings JSON.
  Type: Fact

## Risks And Unknowns

- Risk or unknown: Migrating existing user customizations.
  Why it matters: If the `.env` default vs `settings.json` overwrite model is changed entirely, existing deployments might lose configurations.
  Next proving step: Account for migration or backward compatibility in the spec.

## Recommendation

- Next skill or artifact: `aiddk-spec`
- Why: The current state is fully mapped, and the boundary between system configurations (`.env`) and user configurations (`Settings UI`) needs formal definition before implementation.
- Exact next prompt or action: `/aiddk-spec feature 16-consolidate-settings to define the specification for separating system settings into .env and user configurations into the UI.`
