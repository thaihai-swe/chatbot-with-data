# Feature Specification: Provider Abstraction Layer

## Metadata

- Feature name: Provider Abstraction Layer
- Feature slug: 14.provider-abstraction-layer
- Owner: Engineering Team
- Status: In Review
- Last updated: 2026-05-19
- Related knowledge artifact(s): `artifacts/features/14.provider-abstraction-layer/analysis.md`

## Problem Statement

The codebase is tightly coupled to the OpenAI SDK. All LLM and embedding functionality directly imports and uses OpenAI's Python library, making it impossible to switch providers without modifying service code. This creates vendor lock-in and prevents users from choosing providers based on cost, performance, or feature requirements.

**Current pain points:**
1. Cannot switch to Anthropic, Ollama, or other providers without code changes
2. Users cannot choose providers based on their needs
3. Testing is difficult without OpenAI API access
4. The `LLMSettings.provider` field exists but is unused—indicating incomplete prior work

**Why now:** The system is currently using a local model via OpenAI-compatible API (rag-combo), demonstrating the need for provider flexibility. Formalizing this abstraction enables future provider support and improves testability.

## Desired Outcomes

1. **Configuration-Driven Provider Selection:** Users can switch LLM and embedding providers via configuration without code changes
2. **Clean Abstraction:** Abstract interfaces define provider contracts; concrete implementations handle provider-specific details
3. **Seamless Migration:** All 5 existing services work identically with the new abstraction; no behavior changes
4. **Foundation for Future Providers:** Architecture supports adding Anthropic, Ollama, HuggingFace, and Local providers in future releases

## Minimum Release Slice

**What ships in the first release:**
- `BaseLLMProvider` and `BaseEmbeddingProvider` abstract base classes
- `OpenAILLMProvider` and `OpenAIEmbeddingProvider` implementations
- `LLMProviderFactory` and `EmbeddingProviderFactory` for provider selection
- Migration of all 5 services to use factories
- Configuration system supporting independent LLM and embedding provider selection
- All existing functionality works identically to before

**What can wait:**
- Anthropic provider implementation
- Ollama provider implementation
- HuggingFace embedding provider implementation
- Local embedding provider implementation
- Provider-specific features (Anthropic thinking tokens, OpenAI function calling)
- Advanced provider capabilities (streaming, async, batch operations)

## Success Criteria

- SC-001: Configuration changes can switch providers without code changes
- SC-002: All existing functionality (generation, retrieval, safety, grounding, indexing) works identically
- SC-003: No direct `import openai` statements remain in service code
- SC-004: Provider abstraction follows the same pattern as existing `VectorStore` abstraction
- SC-005: Services can be tested without OpenAI API access (via mock providers)
- SC-006: Custom base URL configuration migrates cleanly to new provider pattern

## In Scope

- Define `BaseLLMProvider` abstract base class with core LLM operations
- Define `BaseEmbeddingProvider` abstract base class with core embedding operations
- Implement `OpenAILLMProvider` wrapping existing OpenAI SDK logic
- Implement `OpenAIEmbeddingProvider` wrapping existing embedding client logic
- Create `LLMProviderFactory` for provider selection based on configuration
- Create `EmbeddingProviderFactory` for provider selection based on configuration
- Update all 5 services to use factory functions instead of direct client instantiation
- Consolidate embedding client instantiation points into single factory
- Update configuration schema to support independent LLM and embedding provider selection
- Migrate custom base URL configuration to new provider pattern
- Preserve all existing error handling, retry logic, and behavior
- Create migration guide for users with custom endpoints

## Out Of Scope

- Implementation of Anthropic, Ollama, HuggingFace, or Local providers (future releases)
- Provider-specific features (Anthropic thinking tokens, OpenAI function calling, etc.)
- Streaming or async provider operations
- Batch embedding operations
- Provider capability detection or feature negotiation
- Cost tracking or provider metrics
- Provider fallback or failover logic

## Non-Goals

- Support for multiple providers simultaneously (e.g., failover to backup provider)
- Provider-specific configuration options beyond API key and base URL
- Performance optimization for specific providers
- Provider comparison or benchmarking
- Deprecation of existing OpenAI-only code (all code migrates in one release)

## Users And Stakeholders

**Primary users:**
- Backend developers maintaining the 5 core services
- DevOps/infrastructure teams configuring the system
- Future developers adding new providers

**Secondary stakeholders:**
- End users who want to choose providers based on cost/performance
- QA teams testing with mock providers
- Security teams reviewing provider integrations

## User Stories And Key Scenarios

- **US-001:** As a developer, I want to switch from OpenAI to a different provider by changing configuration, so I don't need to modify code
- **US-002:** As a DevOps engineer, I want to configure LLM and embedding providers independently, so I can optimize cost and performance separately
- **US-003:** As a QA engineer, I want to test the system with mock providers, so I don't need API keys or external dependencies
- **US-004:** As a future developer, I want to add a new provider (Anthropic, Ollama, etc.), so I follow a clear pattern and don't break existing code

### Detailed Scenarios

**Scenario 1 (Happy Path - Configuration-Driven Provider Selection):**
- **Given:** The system is deployed with default OpenAI configuration
- **When:** An operator changes `LLM_PROVIDER=openai` to `LLM_PROVIDER=anthropic` in the configuration
- **Then:** The system loads the Anthropic provider (once implemented), and all services use it without code changes

**Scenario 2 (Independent Provider Selection):**
- **Given:** The system supports multiple embedding providers
- **When:** An operator configures `LLM_PROVIDER=openai` and `EMBEDDING_PROVIDER=huggingface`
- **Then:** LLM requests use OpenAI, embedding requests use HuggingFace, and both work seamlessly together

**Scenario 3 (Custom Base URL Migration):**
- **Given:** A user has `OPENAI_API_BASE=http://localhost:20128/v1` configured (running Ollama locally)
- **When:** The system is upgraded to use the new provider abstraction
- **Then:** The user updates configuration to `LLM_PROVIDER=openai-compatible` and `OPENAI_COMPATIBLE_BASE_URL=http://localhost:20128/v1`, and everything works identically

**Scenario 4 (Service Behavior Preservation):**
- **Given:** The generation service currently uses `LLMClient` to generate responses
- **When:** The service is migrated to use `LLMProviderFactory`
- **Then:** Response format, error handling, retry logic, and all behavior remain identical

**Scenario 5 (Testing with Mock Provider):**
- **Given:** A developer is writing tests for the retrieval service
- **When:** The developer configures `LLM_PROVIDER=mock` and `EMBEDDING_PROVIDER=mock`
- **Then:** Tests run without API keys, with predictable responses, and complete quickly

## Current Context

**Relevant current behavior:**
- `LLMClient` in `backend/llm/client.py` wraps OpenAI SDK
- `OpenAIEmbeddingClient` in `backend/embeddings/openai_client.py` wraps OpenAI SDK
- 5 services depend on these clients: generation, grounding, safety, retrieval, indexing
- Configuration uses environment variables: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `CHAT_MODEL`, `EMBEDDING_MODEL`
- Custom base URLs enable OpenAI-compatible endpoints (currently using `rag-combo` model)
- `LLMSettings.provider` field exists but is hardcoded to "openai" and unused

**Impacted boundaries:**
- Service factories: `get_llm_client()`, `get_retrieval_service()`, `get_generation_service()`, etc.
- Configuration schema: `LLMSettings`, `IngestionSettings`
- Client instantiation points: 4+ locations for embedding clients, 1 for LLM client

**Unchanged behavior that must be preserved:**
- All service APIs remain identical (same method signatures, return types, error handling)
- Error handling and retry logic work the same way
- Response formats are identical
- Configuration hierarchy (env vars → runtime settings → defaults) is preserved
- FastAPI dependency injection pattern continues to work
- Vector store abstraction is not affected

## Dependencies And External Touchpoints

- **DEP-001:** OpenAI Python SDK (currently required, will remain for OpenAI provider implementation)
- **DEP-002:** FastAPI dependency injection system (used for service factories)
- **DEP-003:** Configuration system (environment variables, settings schema)
- **DEP-004:** 5 core services that depend on LLM/embedding clients
- **DEP-005:** Existing tests that mock or test LLM/embedding behavior

## Functional Requirements

### REQ-001: Abstract LLM Provider Interface

**Requirement:** Define a `BaseLLMProvider` abstract base class that specifies the contract for LLM providers.

**Why it matters:** Enables multiple provider implementations to follow a consistent interface, making it easy to add new providers and switch between them.

**Impacted users or scenarios:** US-001, US-003, US-004; Scenario 1, Scenario 4

**Related success criteria:** SC-004

**Priority:** Must Have

**Acceptance notes:**
- Interface must include core LLM operations: `generate_response()`, `count_tokens()`, and any other methods currently used by services
- Interface must match or extend current `LLMClient` methods to avoid breaking services
- Error handling must be consistent across implementations
- Configuration (API key, base URL, model name) must be injectable

**Validation surface:** Code review, interface definition, method signatures

---

### REQ-002: Abstract Embedding Provider Interface

**Requirement:** Define a `BaseEmbeddingProvider` abstract base class that specifies the contract for embedding providers.

**Why it matters:** Enables multiple embedding provider implementations to follow a consistent interface.

**Impacted users or scenarios:** US-001, US-003, US-004; Scenario 2, Scenario 4

**Related success criteria:** SC-004

**Priority:** Must Have

**Acceptance notes:**
- Interface must include core embedding operations: `embed_text()`, `embed_batch()`, and any other methods currently used by services
- Interface must match or extend current `OpenAIEmbeddingClient` methods
- Error handling must be consistent across implementations
- Configuration must be injectable

**Validation surface:** Code review, interface definition, method signatures

---

### REQ-003: OpenAI LLM Provider Implementation

**Requirement:** Implement `OpenAILLMProvider` that wraps the existing OpenAI SDK logic and implements `BaseLLMProvider`.

**Why it matters:** Validates the abstraction pattern and ensures existing functionality continues to work.

**Impacted users or scenarios:** US-001, Scenario 3, Scenario 4

**Related success criteria:** SC-002, SC-003

**Priority:** Must Have

**Acceptance notes:**
- Must preserve all existing behavior from current `LLMClient`
- Must pass all existing tests without modification
- Must support custom base URLs for OpenAI-compatible endpoints
- Configuration must support `OPENAI_API_KEY`, `OPENAI_API_BASE`, `CHAT_MODEL`

**Validation surface:** Unit tests, integration tests, existing test suite

---

### REQ-004: OpenAI Embedding Provider Implementation

**Requirement:** Implement `OpenAIEmbeddingProvider` that wraps the existing embedding client logic and implements `BaseEmbeddingProvider`.

**Why it matters:** Validates the abstraction pattern for embeddings and ensures existing functionality continues to work.

**Impacted users or scenarios:** US-001, Scenario 3, Scenario 4

**Related success criteria:** SC-002, SC-003

**Priority:** Must Have

**Acceptance notes:**
- Must preserve all existing behavior from current `OpenAIEmbeddingClient`
- Must pass all existing tests without modification
- Must support custom base URLs for OpenAI-compatible endpoints
- Configuration must support `EMBEDDING_API_KEY`, `EMBEDDING_API_BASE`, `EMBEDDING_MODEL`

**Validation surface:** Unit tests, integration tests, existing test suite

---

### REQ-005: LLM Provider Factory

**Requirement:** Create `LLMProviderFactory` that selects and instantiates the appropriate LLM provider based on configuration.

**Why it matters:** Enables configuration-driven provider selection without code changes.

**Impacted users or scenarios:** US-001, US-002; Scenario 1, Scenario 3

**Related success criteria:** SC-001

**Priority:** Must Have

**Acceptance notes:**
- Factory must read `LLM_PROVIDER` configuration value
- Factory must support at least `openai` and `openai-compatible` provider types
- Factory must be injectable via FastAPI `Depends` pattern
- Factory must handle missing or invalid provider configuration gracefully
- Factory must be a single source of truth for provider instantiation

**Validation surface:** Code review, configuration tests, integration tests

---

### REQ-006: Embedding Provider Factory

**Requirement:** Create `EmbeddingProviderFactory` that selects and instantiates the appropriate embedding provider based on configuration.

**Why it matters:** Enables independent embedding provider selection without code changes.

**Impacted users or scenarios:** US-001, US-002; Scenario 2, Scenario 3

**Related success criteria:** SC-001

**Priority:** Must Have

**Acceptance notes:**
- Factory must read `EMBEDDING_PROVIDER` configuration value
- Factory must support at least `openai` and `openai-compatible` provider types
- Factory must be injectable via FastAPI `Depends` pattern
- Factory must handle missing or invalid provider configuration gracefully
- Factory must be independent from LLM provider factory (can use different providers)

**Validation surface:** Code review, configuration tests, integration tests

---

### REQ-007: Service Migration to Provider Factories

**Requirement:** Update all 5 services (generation, grounding, safety, retrieval, indexing) to use provider factories instead of direct client instantiation.

**Why it matters:** Ensures all services benefit from the abstraction and can switch providers via configuration.

**Impacted users or scenarios:** US-001; Scenario 4

**Related success criteria:** SC-002, SC-003

**Priority:** Must Have

**Acceptance notes:**
- Services must use `get_llm_provider()` instead of `get_llm_client()`
- Services must use `get_embedding_provider()` instead of direct `OpenAIEmbeddingClient` instantiation
- All service behavior must remain identical (same method calls, same responses, same error handling)
- No direct `import openai` statements in service code
- Consolidate embedding client instantiation from 4+ locations into single factory

**Validation surface:** Code review, existing test suite, integration tests

---

### REQ-008: Configuration Schema Update

**Requirement:** Update configuration schema to support independent LLM and embedding provider selection.

**Why it matters:** Enables users to configure providers without code changes.

**Impacted users or scenarios:** US-001, US-002; Scenario 1, Scenario 2, Scenario 3

**Related success criteria:** SC-001, SC-006

**Priority:** Must Have

**Acceptance notes:**
- Configuration must support `LLM_PROVIDER` environment variable
- Configuration must support `EMBEDDING_PROVIDER` environment variable
- Configuration must support provider-specific settings (API key, base URL, model name)
- Configuration must maintain backward compatibility with existing `OPENAI_API_BASE` (with deprecation path)
- Configuration schema must be documented

**Validation surface:** Configuration tests, documentation, migration guide

---

### REQ-009: Custom Base URL Migration Path

**Requirement:** Provide a clear migration path for users with custom base URLs (e.g., running Ollama locally).

**Why it matters:** Ensures existing users can upgrade without breaking their setup.

**Impacted users or scenarios:** US-001; Scenario 3

**Related success criteria:** SC-006

**Priority:** Must Have

**Acceptance notes:**
- Old configuration: `OPENAI_API_BASE=http://localhost:20128/v1`
- New configuration: `LLM_PROVIDER=openai-compatible` + `OPENAI_COMPATIBLE_BASE_URL=http://localhost:20128/v1`
- Migration guide must be clear and easy to follow
- System must support both old and new configuration during transition (or provide clear error message)

**Validation surface:** Migration guide, configuration tests, manual testing

---

### REQ-010: Behavior Preservation Validation

**Requirement:** Ensure all existing functionality works identically after migration to provider abstraction.

**Why it matters:** Prevents regressions and ensures users experience no behavior changes.

**Impacted users or scenarios:** US-001; Scenario 4

**Related success criteria:** SC-002

**Priority:** Must Have

**Acceptance notes:**
- All existing tests must pass without modification
- Response formats must be identical
- Error handling must be identical
- Retry logic must be identical
- Performance must be comparable (no significant overhead)

**Validation surface:** Existing test suite, integration tests, performance tests

## Non-Functional Requirements

- **NFR-001 Performance:** Provider abstraction must not introduce measurable latency overhead (< 1% increase in response time)
- **NFR-002 Reliability:** Provider instantiation must be deterministic; same configuration always produces same provider
- **NFR-003 Security:** Provider configuration must not expose API keys in logs or error messages
- **NFR-004 Accessibility:** Not applicable to this feature
- **NFR-005 Observability:** Provider selection must be logged for debugging; provider errors must be traceable
- **NFR-006 Compliance:** No new compliance requirements introduced

## Constraints

**Technical constraints:**
- Must use FastAPI dependency injection pattern (existing pattern in codebase)
- Must follow abstract base class pattern (existing pattern in codebase)
- Must not break existing service APIs
- Must support Python 3.8+ (current project requirement)

**Business constraints:**
- Big bang migration: all services must migrate in one release (no gradual rollout)
- Common interface only: provider-specific features are out of scope

**Delivery constraints:**
- Must be completed before adding new provider implementations
- Must not delay other feature work

## Assumptions

- **ASM-001:** All 5 services can be updated simultaneously without coordination delays
- **ASM-002:** Existing tests provide sufficient coverage to validate behavior preservation
- **ASM-003:** Users with custom base URLs will update their configuration as part of the upgrade
- **ASM-004:** Future provider implementations will follow the same abstract base class pattern

## Risks

- **RISK-001 Breaking Changes:** Updating 5 services simultaneously increases risk of breaking existing functionality
  - **Mitigation:** Comprehensive test suite validates behavior preservation; staged rollout in development/staging before production

- **RISK-002 Configuration Migration:** Users with custom endpoints must update their `.env` files
  - **Mitigation:** Clear migration guide; system provides helpful error message if old configuration is detected

- **RISK-003 Provider Parity:** Different providers may have different response formats or error handling
  - **Mitigation:** Abstraction enforces consistent interface; tests validate behavior across providers

- **RISK-004 Testing Complexity:** Must test with multiple providers and configurations
  - **Mitigation:** Mock provider implementation enables testing without external dependencies

## Open Questions

- **Q-001:** Should the system support a "mock" provider for testing?
  - **Type:** Non-blocking
  - **Owner:** Engineering team
  - **Next step:** Implement mock provider if needed for testing; can be added after initial release

- **Q-002:** Should provider configuration support environment variable interpolation (e.g., `${OPENAI_API_KEY}`)?
  - **Type:** Non-blocking
  - **Owner:** Engineering team
  - **Next step:** Defer to future release if needed

## Acceptance Criteria

- [ ] **AC-001** Linked requirement(s): REQ-001
  - Linked user story or scenario: US-004, Scenario 1
  - Linked success criteria: SC-004
  - Validation method: Code review
  - Proof target: `BaseLLMProvider` abstract base class exists with documented interface

- [ ] **AC-002** Linked requirement(s): REQ-002
  - Linked user story or scenario: US-004, Scenario 2
  - Linked success criteria: SC-004
  - Validation method: Code review
  - Proof target: `BaseEmbeddingProvider` abstract base class exists with documented interface

- [ ] **AC-003** Linked requirement(s): REQ-003
  - Linked user story or scenario: US-001, Scenario 4
  - Linked success criteria: SC-002, SC-003
  - Validation method: Test suite execution
  - Proof target: All existing LLM tests pass with `OpenAILLMProvider`

- [ ] **AC-004** Linked requirement(s): REQ-004
  - Linked user story or scenario: US-001, Scenario 4
  - Linked success criteria: SC-002, SC-003
  - Validation method: Test suite execution
  - Proof target: All existing embedding tests pass with `OpenAIEmbeddingProvider`

- [ ] **AC-005** Linked requirement(s): REQ-005
  - Linked user story or scenario: US-001, Scenario 1
  - Linked success criteria: SC-001
  - Validation method: Integration test
  - Proof target: `LLMProviderFactory` instantiates correct provider based on `LLM_PROVIDER` configuration

- [ ] **AC-006** Linked requirement(s): REQ-006
  - Linked user story or scenario: US-002, Scenario 2
  - Linked success criteria: SC-001
  - Validation method: Integration test
  - Proof target: `EmbeddingProviderFactory` instantiates correct provider based on `EMBEDDING_PROVIDER` configuration

- [ ] **AC-007** Linked requirement(s): REQ-007
  - Linked user story or scenario: US-001, Scenario 4
  - Linked success criteria: SC-002, SC-003
  - Validation method: Code review + test suite
  - Proof target: All 5 services use provider factories; no direct `import openai` in service code; all tests pass

- [ ] **AC-008** Linked requirement(s): REQ-008
  - Linked user story or scenario: US-001, US-002
  - Linked success criteria: SC-001
  - Validation method: Configuration tests
  - Proof target: Configuration schema supports `LLM_PROVIDER` and `EMBEDDING_PROVIDER` independently

- [ ] **AC-009** Linked requirement(s): REQ-009
  - Linked user story or scenario: US-001, Scenario 3
  - Linked success criteria: SC-006
  - Validation method: Manual testing + migration guide review
  - Proof target: User with custom base URL can upgrade and configure new provider pattern; system works identically

- [ ] **AC-010** Linked requirement(s): REQ-010
  - Linked user story or scenario: US-001, Scenario 4
  - Linked success criteria: SC-002
  - Validation method: Test suite execution + performance testing
  - Proof target: All existing tests pass; response formats identical; performance overhead < 1%

## Notes

**Related artifacts:**
- `artifacts/features/14.provider-abstraction-layer/analysis.md` - Research findings on current provider usage
- `artifacts/features/14.provider-abstraction-layer/proposal.md` - High-level proposal and alignment

**Reference patterns:**
- `backend/indexing/base.py` - `VectorStore` abstraction pattern to follow
- `backend/chunking/base.py` - `BaseChunker` abstraction pattern to follow

**Configuration reference:**
- Current: `backend/.env` - Example environment variables
- Current: `backend/config.py` - Configuration management
- Current: `backend/schemas/settings.py` - Settings schema

**Service dependencies:**
- `backend/chat/generation.py` - GenerationService
- `backend/chat/grounding.py` - GroundingService
- `backend/chat/safety.py` - SafetyService
- `backend/chat/retrieval.py` - RetrievalService
- `backend/indexing/indexing_service.py` - IndexingService
