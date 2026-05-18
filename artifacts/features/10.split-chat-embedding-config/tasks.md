# Tasks: Split Chat and Embedding Configuration

- [x] T-001: Update Settings dataclass in backend/config.py to include embedding_api_base and embedding_api_key. [Dependency: None] [Status: Done] [Proof: Unit test in backend/tests/test_config.py passed]
- [x] T-002: Refactor embedding service initialization in backend/embeddings/ to use new configuration variables. [Dependency: T-001] [Status: Done] [Proof: Integration test in backend/tests/test_split_config.py passed]
- [x] T-003: Verify chat service initialization to ensure no regression. [Dependency: T-001] [Status: Done] [Proof: test_llm_client_uses_openai_config in test_split_config.py passed]
- [x] T-004: Validate configuration fallback logic. [Dependency: T-001] [Status: Done] [Proof: test_settings_fallback_logic in test_split_config.py passed]
