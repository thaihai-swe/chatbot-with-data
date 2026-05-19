# Implementation Plan: Provider Abstraction Layer

## Metadata

- Feature name: Provider Abstraction Layer
- Related spec: `artifacts/features/14.provider-abstraction-layer/spec.md`
- Related requirements review: `artifacts/features/14.provider-abstraction-layer/requirements-review.md`
- Related design: `artifacts/features/14.provider-abstraction-layer/design.md`
- Owner: Engineering Team
- Status: Draft
- Last updated: 2026-05-19

## Plan Summary

Create abstract provider interfaces and wrap existing OpenAI SDK logic in concrete implementations, then migrate all 5 services to use providers via dependency injection. The approach prioritizes behavior preservation by wrapping existing code rather than rewriting. Execution happens in 4 phases: (1) define abstractions, (2) implement OpenAI providers, (3) create factories, (4) migrate services. All existing tests must pass without modification. See `design.md` for technical approach.

## Execution Context

**Design reference:** `design.md` - Adapter pattern wrapping existing clients, separate factories for LLM and embedding providers

**Relevant repository patterns:**
- Abstract base classes: `VectorStore` (backend/indexing/base.py), `BaseChunker` (backend/chunking/base.py)
- FastAPI dependency injection: `Depends(get_llm_client)`, `Depends(get_retrieval_service)`
- Factory functions: `get_llm_client()`, `get_retrieval_service()`, etc.
- Configuration: Dual system (legacy Settings + GlobalSettings)

**Brownfield execution constraints:**
- Must preserve all existing behavior (response formats, error handling, retry logic)
- Must maintain FastAPI dependency injection pattern
- Cannot break existing tests
- Must support dual configuration system during migration
- 5 services must be updated simultaneously (big bang migration)

**Unchanged behavior that must be preserved:**
- LLMClient: streaming/non-streaming modes, temperature handling, timeout behavior, response stripping
- OpenAIEmbeddingClient: retry logic with exponential backoff, cost tracking, batch processing, rate limiting
- Service APIs: method signatures, return types, error propagation
- Configuration hierarchy and precedence

## First Delivery Slice

**Smallest useful slice:**
- Define `BaseLLMProvider` and `BaseEmbeddingProvider` abstract base classes
- Implement `OpenAILLMProvider` and `OpenAIEmbeddingProvider` wrapping existing logic
- Create `get_llm_provider()` and `get_embedding_provider()` factories
- Update configuration schema to support `LLM_PROVIDER` and `EMBEDDING_PROVIDER`
- Migrate all 5 services to use factories
- All existing tests pass without modification

**Why this slice goes first:**
- Validates the abstraction pattern with minimal risk
- Enables configuration-driven provider selection
- Preserves all existing behavior
- Provides foundation for future provider implementations

**What proof should exist when this slice is done:**
- All existing tests pass (unit, integration, end-to-end)
- No direct `import openai` in service code
- Configuration changes switch providers without code changes
- Response formats and behavior identical to before
- Performance overhead < 1%

## Technical Approach

**Chosen approach:** Adapter pattern wrapping existing clients

**Architectural shape:**
```
Services (generation, grounding, safety, retrieval, indexing)
    ↓ (depend on via Depends)
Factories (get_llm_provider, get_embedding_provider)
    ↓ (instantiate)
Concrete Providers (OpenAILLMProvider, OpenAIEmbeddingProvider)
    ↓ (implement)
Abstract Providers (BaseLLMProvider, BaseEmbeddingProvider)
    ↓ (define contract)
External APIs (OpenAI SDK)
```

**Key interfaces:**
```python
# BaseLLMProvider
class BaseLLMProvider(ABC):
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        pass

# BaseEmbeddingProvider
class BaseEmbeddingProvider(ABC):
    def embed(self, text: str) -> list[float]:
        pass
    
    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        pass
```

**Operational considerations:**
- Provider instantiation happens per request (FastAPI lifecycle)
- Configuration read at startup and cached
- Errors from providers propagate to services unchanged
- Logging includes provider name for debugging

## Requirements And Constraints

**REQ-001: Abstract LLM Provider Interface**
- Implementation note: Define `BaseLLMProvider` ABC with `generate_completion()` method
- Planned validation: Code review of interface definition; verify all services can use it
- Linked scenario: Scenario 1 (configuration-driven provider selection)

**REQ-002: Abstract Embedding Provider Interface**
- Implementation note: Define `BaseEmbeddingProvider` ABC with `embed()` and `embed_batch()` methods
- Planned validation: Code review of interface definition; verify all services can use it
- Linked scenario: Scenario 2 (independent provider selection)

**REQ-003: OpenAI LLM Provider Implementation**
- Implementation note: Wrap existing `LLMClient` logic in `OpenAILLMProvider` class
- Planned validation: All existing LLM tests pass; behavior identical to before
- Linked scenario: Scenario 4 (service behavior preservation)

**REQ-004: OpenAI Embedding Provider Implementation**
- Implementation note: Wrap existing `OpenAIEmbeddingClient` logic in `OpenAIEmbeddingProvider` class
- Planned validation: All existing embedding tests pass; retry logic preserved; cost tracking works
- Linked scenario: Scenario 4 (service behavior preservation)

**REQ-005: LLM Provider Factory**
- Implementation note: Create `get_llm_provider()` factory that reads `LLM_PROVIDER` config
- Planned validation: Factory instantiates correct provider based on config; injectable via Depends
- Linked scenario: Scenario 1 (configuration-driven selection)

**REQ-006: Embedding Provider Factory**
- Implementation note: Create `get_embedding_provider()` factory that reads `EMBEDDING_PROVIDER` config
- Planned validation: Factory instantiates correct provider; independent from LLM factory
- Linked scenario: Scenario 2 (independent provider selection)

**REQ-007: Service Migration**
- Implementation note: Update all 5 services to use factories instead of direct client instantiation
- Planned validation: All services use `Depends(get_llm_provider)` or `Depends(get_embedding_provider)`
- Linked scenario: Scenario 4 (service behavior preservation)

**REQ-008: Configuration Schema Update**
- Implementation note: Add `LLM_PROVIDER` and `EMBEDDING_PROVIDER` fields to settings
- Planned validation: Configuration tests verify provider selection works
- Linked scenario: Scenario 1, Scenario 2 (configuration-driven selection)

**REQ-009: Custom Base URL Migration**
- Implementation note: Support `openai-compatible` provider type with custom base URL
- Planned validation: Manual testing with custom base URL; migration guide provided
- Linked scenario: Scenario 3 (custom base URL migration)

**REQ-010: Behavior Preservation**
- Implementation note: All existing tests must pass without modification
- Planned validation: Full test suite execution; performance benchmarking
- Linked scenario: Scenario 4 (service behavior preservation)

**NFR-001: Performance**
- Implementation note: Provider abstraction must not introduce measurable latency
- Planned validation: Performance tests comparing before/after response times

**CON-001: Big Bang Migration**
- Impact on plan: All 5 services must be updated in one release; increases coordination complexity
- Mitigation: Comprehensive test suite validates behavior preservation; staged rollout in dev/staging

## Impacted Areas

**Services or modules:**
- `backend/chat/generation.py` - GenerationService
- `backend/chat/grounding.py` - GroundingService
- `backend/chat/safety.py` - SafetyService
- `backend/chat/retrieval.py` - RetrievalService, QueryIntelligenceService
- `backend/indexing/indexing_service.py` - IndexingService

**APIs or interfaces:**
- `backend/llm/client.py` - LLMClient (deprecated, replaced by BaseLLMProvider)
- `backend/embeddings/openai_client.py` - OpenAIEmbeddingClient (deprecated, replaced by BaseEmbeddingProvider)
- Service factory functions: `get_generation_service()`, `get_retrieval_service()`, etc.

**Data model or storage:**
- Configuration schema: Add `LLM_PROVIDER` and `EMBEDDING_PROVIDER` fields

**UI or UX:**
- Not applicable (backend-only feature)

**Infrastructure or deployment:**
- No infrastructure changes required
- Configuration changes needed for custom base URLs

**Documentation:**
- Migration guide for users with custom endpoints
- Provider abstraction documentation for future developers

## Protected Behavior

**Behavior that must not regress:**
- LLMClient streaming: Iterator protocol, chunk delivery, error handling
- LLMClient non-streaming: Response stripping, timeout behavior
- OpenAIEmbeddingClient retry logic: Exponential backoff, max retries, error handling
- OpenAIEmbeddingClient cost tracking: Usage statistics, pricing calculations
- OpenAIEmbeddingClient batch processing: Rate limiting, batch size handling
- Service APIs: Method signatures, return types, error propagation
- Configuration hierarchy: Env vars → GlobalSettings → defaults

**Protection approach:**
- All existing tests must pass without modification
- Performance tests validate < 1% overhead
- Manual testing of streaming, batch processing, error scenarios
- Code review of provider implementations to ensure behavior preservation

## Affected Files

**New files:**
- `backend/providers/__init__.py` - Package initialization
- `backend/providers/base.py` - Abstract base classes (BaseLLMProvider, BaseEmbeddingProvider)
- `backend/providers/openai.py` - OpenAI provider implementations
- `backend/providers/factory.py` - Provider factory functions

**Modified files:**
- `backend/chat/generation.py` - Update to use `get_llm_provider()`
- `backend/chat/grounding.py` - Update to use `get_llm_provider()`
- `backend/chat/safety.py` - Update to use `get_llm_provider()` and `get_embedding_provider()`
- `backend/chat/retrieval.py` - Update to use `get_embedding_provider()`
- `backend/indexing/indexing_service.py` - Update to use `get_embedding_provider()`
- `backend/schemas/settings.py` - Add `LLM_PROVIDER` and `EMBEDDING_PROVIDER` fields
- `backend/config.py` - Update configuration loading if needed
- `backend/llm/client.py` - Keep for backward compatibility, mark as deprecated
- `backend/embeddings/openai_client.py` - Keep for backward compatibility, mark as deprecated

**Deprecated files (keep for now, remove in future release):**
- `backend/llm/client.py` - LLMClient (replaced by OpenAILLMProvider)
- `backend/embeddings/openai_client.py` - OpenAIEmbeddingClient (replaced by OpenAIEmbeddingProvider)

## Dependencies

**DEP-001: OpenAI Python SDK**
- Why it matters: Required for OpenAI provider implementation; already in requirements.txt
- No new dependencies needed

**DEP-002: FastAPI dependency injection**
- Why it matters: Services use `Depends()` pattern; factories must integrate with it
- No changes needed; existing pattern continues to work

**DEP-003: Configuration system**
- Why it matters: Provider selection driven by configuration
- Must support dual system (legacy Settings + GlobalSettings) during migration

**DEP-004: Existing tests**
- Why it matters: All tests must pass without modification
- No changes to test code; only implementation changes

## Implementation Prerequisites

- PREREQ-001: Understand current LLMClient and OpenAIEmbeddingClient implementations
- PREREQ-002: Understand FastAPI dependency injection pattern used in services
- PREREQ-003: Understand configuration hierarchy (env vars → GlobalSettings → defaults)
- PREREQ-004: Understand existing test structure and coverage

## Execution Phases

### Phase 1: Define Abstractions

**Goal:** Create abstract base classes that define provider contracts

**Enabled user scenario(s) or outcome(s):**
- US-004: Future developers can add new providers following a clear pattern

**Entry proof:**
- Codebase is in clean state with no uncommitted changes

**Exit proof:**
- `backend/providers/base.py` exists with `BaseLLMProvider` and `BaseEmbeddingProvider` ABCs
- All abstract methods documented with signatures and docstrings
- Code review approved

**Completion criteria:**
- CC-001: `BaseLLMProvider` has `generate_completion()` method matching current `LLMClient`
- CC-002: `BaseEmbeddingProvider` has `embed()` and `embed_batch()` methods matching current `OpenAIEmbeddingClient`
- CC-003: All abstract methods have clear docstrings explaining parameters and return types
- CC-004: Configuration parameters are documented (API key, base URL, model name)

### Phase 2: Implement OpenAI Providers

**Goal:** Wrap existing OpenAI SDK logic in provider implementations

**Enabled user scenario(s) or outcome(s):**
- Scenario 4: Service behavior preservation - all existing functionality continues to work

**Entry proof:**
- Phase 1 complete; abstract base classes exist and are approved

**Exit proof:**
- `backend/providers/openai.py` exists with `OpenAILLMProvider` and `OpenAIEmbeddingProvider`
- All existing tests pass without modification
- Behavior identical to current implementations

**Completion criteria:**
- CC-005: `OpenAILLMProvider` wraps existing `LLMClient` logic; all methods implemented
- CC-006: `OpenAIEmbeddingProvider` wraps existing `OpenAIEmbeddingClient` logic; all methods implemented
- CC-007: All existing LLM tests pass with `OpenAILLMProvider`
- CC-008: All existing embedding tests pass with `OpenAIEmbeddingProvider`
- CC-009: Retry logic, cost tracking, batch processing all work identically
- CC-010: Performance overhead < 1%

### Phase 3: Create Factories and Update Configuration

**Goal:** Implement provider selection logic and update configuration schema

**Enabled user scenario(s) or outcome(s):**
- Scenario 1: Configuration-driven provider selection
- Scenario 2: Independent LLM and embedding provider selection

**Entry proof:**
- Phase 2 complete; OpenAI providers exist and all tests pass

**Exit proof:**
- `backend/providers/factory.py` exists with `get_llm_provider()` and `get_embedding_provider()`
- Configuration schema updated with `LLM_PROVIDER` and `EMBEDDING_PROVIDER` fields
- Factories are injectable via FastAPI `Depends`

**Completion criteria:**
- CC-011: `get_llm_provider()` factory reads `LLM_PROVIDER` config and instantiates correct provider
- CC-012: `get_embedding_provider()` factory reads `EMBEDDING_PROVIDER` config and instantiates correct provider
- CC-013: Factories support "openai" and "openai-compatible" provider types
- CC-014: Configuration schema updated; both fields are optional with sensible defaults
- CC-015: Configuration tests verify provider selection works correctly

### Phase 4: Migrate Services

**Goal:** Update all 5 services to use provider factories instead of direct client instantiation

**Enabled user scenario(s) or outcome(s):**
- Scenario 1: Configuration-driven provider selection works end-to-end
- Scenario 4: Service behavior preservation - all services work identically

**Entry proof:**
- Phase 3 complete; factories exist and configuration is updated

**Exit proof:**
- All 5 services updated to use factories
- All existing tests pass without modification
- No direct `import openai` in service code

**Completion criteria:**
- CC-016: GenerationService uses `Depends(get_llm_provider)`
- CC-017: GroundingService uses `Depends(get_llm_provider)`
- CC-018: SafetyService uses `Depends(get_llm_provider)` and `Depends(get_embedding_provider)`
- CC-019: RetrievalService uses `Depends(get_embedding_provider)`
- CC-020: IndexingService uses `Depends(get_embedding_provider)`
- CC-021: All existing tests pass without modification
- CC-022: No direct `import openai` statements in service code
- CC-023: Custom base URL configuration migrates cleanly to new provider pattern

## Validation Strategy

**TEST-001: Unit tests**
- Test each provider implementation in isolation
- Verify method signatures match abstract interfaces
- Test error handling and edge cases
- Validate configuration parsing

**TEST-002: Integration tests**
- Test provider factories with different configurations
- Test services using providers via dependency injection
- Verify provider selection based on configuration
- Test error propagation from providers to services

**TEST-003: End-to-end tests**
- Test full request flow through services with different providers
- Verify response formats and behavior identical to before
- Test streaming and non-streaming modes
- Test batch processing and rate limiting

**TEST-004: Manual verification**
- Test custom base URL configuration (Scenario 3)
- Test configuration changes switching providers (Scenario 1)
- Test independent provider selection (Scenario 2)
- Test error scenarios and recovery

**TEST-005: Observability checks**
- Verify provider selection logged at startup
- Verify provider errors include provider name
- Verify usage statistics tracked correctly
- Verify cost calculations accurate

## Traceability Matrix

| Requirement | Phase | Tasks |
|---|---|---|
| REQ-001 (LLM interface) | Phase 1 | T-001 |
| REQ-002 (Embedding interface) | Phase 1 | T-002 |
| REQ-003 (OpenAI LLM provider) | Phase 2 | T-003, T-004, T-005 |
| REQ-004 (OpenAI embedding provider) | Phase 2 | T-006, T-007, T-008 |
| REQ-005 (LLM factory) | Phase 3 | T-009, T-010 |
| REQ-006 (Embedding factory) | Phase 3 | T-011, T-012 |
| REQ-007 (Service migration) | Phase 4 | T-013 through T-022 |
| REQ-008 (Configuration schema) | Phase 3 | T-023, T-024 |
| REQ-009 (Custom base URL migration) | Phase 4 | T-025, T-026 |
| REQ-010 (Behavior preservation) | All phases | T-027 (validation) |

| Scenario | Phase | Validation |
|---|---|---|
| Scenario 1 (Config-driven selection) | Phase 3, 4 | Integration tests, manual testing |
| Scenario 2 (Independent providers) | Phase 3, 4 | Integration tests, manual testing |
| Scenario 3 (Custom base URL) | Phase 4 | Manual testing, migration guide |
| Scenario 4 (Behavior preservation) | All phases | All existing tests pass |
| Scenario 5 (Testing with mock) | Future | Out of scope for this release |

## Rollout Plan

**Release approach:**
- Single release with all phases completed
- Big bang migration: all services updated simultaneously
- No feature flags needed (configuration-driven)

**Feature flags:**
- Not needed; provider selection via configuration

**Migration needs:**
- Users with custom base URLs must update configuration
- Migration guide provided with clear examples
- Old configuration still works during transition (if supported)

**Backward compatibility notes:**
- Old `LLMClient` and `OpenAIEmbeddingClient` kept for now (marked deprecated)
- Can be removed in future release after migration period
- Configuration hierarchy preserved (env vars → GlobalSettings → defaults)

## Rollback Plan

**How to revert:**
1. Revert all code changes to services, factories, and providers
2. Restore old `get_llm_client()` and direct `OpenAIEmbeddingClient` instantiation
3. Revert configuration schema changes
4. Redeploy with previous version

**Rollback triggers:**
- Critical regression in existing functionality
- Performance degradation > 5%
- Configuration migration issues affecting users

**Rollback time estimate:** < 30 minutes (straightforward git revert + redeploy)

## Risks And Mitigations

**RISK-001: Big Bang Migration Complexity**
- Mitigation: Comprehensive test suite validates behavior preservation; staged rollout in dev/staging before production

**RISK-002: Configuration Migration Confusion**
- Mitigation: Clear migration guide with examples; helpful error messages if old config detected

**RISK-003: Retry Logic Regression**
- Mitigation: Preserve existing tenacity decorator and error handling in OpenAIEmbeddingProvider; all tests must pass

**RISK-004: Performance Overhead**
- Mitigation: Provider abstraction is thin wrapper; performance tests validate < 1% overhead

**RISK-005: Streaming Mode Breakage**
- Mitigation: Preserve streaming behavior and iterator protocol in OpenAILLMProvider; streaming tests must pass

## Open Questions

**Q-001: Should we implement a mock provider for testing?**
- Next step: Defer to implementation phase; can be added after initial release if needed

**Q-002: Should provider factories cache instances or create new instances per request?**
- Next step: Follow FastAPI's default behavior (new instance per request); optimize later if needed
