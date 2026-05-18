# Tasks: Consolidated Configuration Management

## Phase 1: Schema Updates
- [x] T-001: Add `url_timeout_seconds` to `IngestionSettings` in `backend/schemas/settings.py`. [Status: Done] [Proof: Code inspection passed]
- [x] T-002: Add `context_window_size` to `LLMSettings` and sync `chat_history_limit` with `MAX_HISTORY_TURNS`. [Status: Done] [Proof: Code inspection passed]
- [x] T-003: Add `min_similarity_threshold` and `min_results_count` to `SafetySettings`. [Status: Done] [Proof: Code inspection passed]

## Phase 2: Service Refactoring
- [x] T-004: Refactor `WebExtractor` in `backend/extractors/web_extractor.py` to use `get_config()`. [Status: Done] [Proof: Code inspection passed]
- [x] T-005: Refactor `GroundingService` in `backend/chat/grounding.py` to use `get_config()`. [Status: Done] [Proof: Code inspection passed]
- [x] T-006: Refactor `ContextService` in `backend/chat/context.py` to use `get_config()`. [Status: Done] [Proof: Code inspection passed]

## Phase 3: Final Validation
- [x] T-007: Create `backend/tests/test_consolidated_config.py` to verify precedence logic (Env vs JSON). [Status: Done] [Proof: All tests in file pass]
- [x] T-008: Verify end-to-end ingestion and chat with default settings. [Status: Done] [Proof: Manual verification of refactored services and passing integration tests]
