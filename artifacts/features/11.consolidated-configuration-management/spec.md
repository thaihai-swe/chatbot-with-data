# Feature Specification: 11.consolidated-configuration-management

## Metadata
- Feature name: Consolidated Configuration Management
- Feature slug: 11.consolidated-configuration-management
- Owner: Gemini CLI
- Status: Draft
- Last updated: 2026-05-18

## Problem Statement
The application's configuration is fragmented across legacy environment-driven settings and modern JSON-driven settings. Core infrastructure settings (URLs, Keys) and behavior-shaping feature settings (Timeouts, Thresholds) are inconsistently handled, making the system difficult to manage through the API and confusing for developers.

## Desired Outcomes
- Clear separation: Infrastructure settings stay in `.env`, Feature settings move to `GlobalSettings` (JSON).
- All behavior-shaping settings are unified in the `GlobalSettings` Pydantic models.
- Services consistently use `get_config()` to access feature-level settings.
- Backward compatibility is maintained by using environment variables as defaults for JSON-based settings.

## Minimum Release Slice
- Migration of four key feature settings: `url_timeout_seconds`, `context_window_size`, `min_similarity_threshold`, and `min_results_count`.
- Update the `SettingsManager` to ensure these settings are correctly synchronized with the environment.
- Refactor the following services: `UrlIngestionService`, `GroundingService`, and `RetrievalService`.

## In Scope
- Updates to `backend/schemas/settings.py` (Pydantic schemas).
- Updates to `backend/config.py` (precedence and synchronization logic).
- Refactoring affected services to consume settings from `GlobalSettings`.
- Comprehensive unit tests for the new configuration hierarchy.

## Out Of Scope
- Moving API keys or Base URLs into `GlobalSettings`.
- Building a UI for configuration management.
- Full removal of the legacy `Settings` class (partial reduction only).

## User Stories
- **US-001:** As a power user, I want to increase the `url_timeout_seconds` via the API so that I can ingest content from slow-responding servers without changing my deployment environment.
- **US-002:** As an evaluation researcher, I want to tweak the `min_similarity_threshold` in `settings.json` to see how it affects RAG groundedness metrics across a large dataset.

## Detailed Scenarios

### Scenario 1: Environment Defaulting
- **Given:** `MIN_SIMILARITY_THRESHOLD` is set to `0.5` in `.env`.
- **And:** `settings.json` does not have a `min_similarity_threshold` entry.
- **When:** `get_config().safety.min_similarity_threshold` is accessed.
- **Then:** It returns `0.5`.

### Scenario 2: JSON Override
- **Given:** `MIN_SIMILARITY_THRESHOLD` is set to `0.5` in `.env`.
- **And:** `settings.json` has `min_similarity_threshold: 0.8`.
- **When:** `get_config().safety.min_similarity_threshold` is accessed.
- **Then:** It returns `0.8`.

## Functional Requirements

### REQ-001: Schema Consolidation
- **Requirement:** Extend `GlobalSettings` sub-models with the following fields:
  - `IngestionSettings`: `url_timeout_seconds`
  - `LLMSettings`: `context_window_size`
  - `SafetySettings`: `min_similarity_threshold`, `min_results_count`
- **Priority:** Must Have.

### REQ-002: Service Integration
- **Requirement:** Services `UrlIngestionService`, `GroundingService`, and `RetrievalService` must be refactored to use the new fields from `GlobalSettings`.
- **Priority:** Must Have.

### REQ-003: Infrastructure Protection
- **Requirement:** API keys and Base URLs must **not** be added to `GlobalSettings` or saved to `settings.json`. They remain exclusively in `.env`.
- **Priority:** Must Have.

## Acceptance Criteria
- [ ] AC-001: All specified feature settings are present in `GlobalSettings`.
- [ ] AC-002: Unit tests confirm that `.env` values correctly default the new fields.
- [ ] AC-003: Unit tests confirm that JSON values correctly override `.env` defaults for feature settings.
- [ ] AC-004: Services are verified to use the unified configuration source.
