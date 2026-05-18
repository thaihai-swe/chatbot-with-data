# Implementation Plan: Consolidated Configuration Management

This plan outlines the steps to unify feature-level configurations into the `GlobalSettings` system, ensuring a clear boundary between Infrastructure (environment-only) and Features (JSON-manageable).

## 1. Schema Expansion
Extend the Pydantic sub-models in `backend/schemas/settings.py` to include feature-level settings that were previously handled by the legacy `Settings` class.

- **IngestionSettings**: Add `url_timeout_seconds`.
- **LLMSettings**: Add `context_window_size` and sync `chat_history_limit` with `MAX_HISTORY_TURNS`.
- **SafetySettings**: Add `min_similarity_threshold` and `min_results_count`.

## 2. Service Refactoring
Update backend services to consume these settings from the unified `get_config()` accessor.

- `WebExtractor`: Refactor to use `config.ingestion.url_timeout_seconds`.
- `GroundingService`: Refactor to use `config.safety.min_similarity_threshold` and `config.safety.min_results_count`.
- `ContextService`: Refactor to use `config.llm.chat_history_limit`.

## 3. Verification Strategy
- **Unit Testing**: Verify that `GlobalSettings` correctly pulls defaults from environment variables.
- **Integration Testing**: Verify that `settings.json` overrides correctly propagate to the refactored services.
- **Regression Testing**: Ensure existing chat and ingestion flows continue to work with default settings.
