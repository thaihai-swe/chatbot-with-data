# Technical Design: Provider Abstraction Layer

## Metadata

- Feature name: Provider Abstraction Layer
- Feature slug: 14.provider-abstraction-layer
- Related spec: `artifacts/features/14.provider-abstraction-layer/spec.md`
- Related requirements review: `artifacts/features/14.provider-abstraction-layer/requirements-review.md`
- Owner: Engineering Team
- Status: Draft
- Last updated: 2026-05-19

## Design Summary

Create abstract base classes (`BaseLLMProvider`, `BaseEmbeddingProvider`) following the existing `VectorStore` pattern. Wrap current OpenAI SDK logic in concrete implementations (`OpenAILLMProvider`, `OpenAIEmbeddingProvider`) that preserve all existing behavior. Introduce factory functions that select providers based on configuration. Migrate all 5 services to use factories via FastAPI dependency injection. The design prioritizes behavior preservation and follows existing repository patterns.

## Current State And Context

**Existing system baseline:**
- `LLMClient` (75 lines) in `backend/llm/client.py` - Simple wrapper around OpenAI SDK
  - Methods: `generate_completion()`, `_generate_non_stream()`, `_generate_stream()`
  - No retry logic, no error handling, no cost tracking
- `OpenAIEmbeddingClient` (248 lines) in `backend/embeddings/openai_client.py` - Comprehensive wrapper
  - Methods: `embed()`, `embed_batch()`, `get_stats()`, `reset_stats()`, `validate_embedding_dimension()`
  - Retry logic with tenacity (exponential backoff, 3 retries)
  - Cost tracking and usage statistics
  - Batch processing with rate limiting
- 5 services depend on these clients: GenerationService, GroundingService, SafetyService, RetrievalService, IndexingService
- Configuration uses dual system: legacy `Settings` + new `GlobalSettings`

**Relevant repository patterns:**
- Abstract base classes: `VectorStore` (backend/indexing/base.py), `BaseChunker` (backend/chunking/base.py)
- FastAPI dependency injection: `Depends(get_llm_client)`, `Depends(get_retrieval_service)`
- Factory functions: `get_llm_client()`, `get_retrieval_service()`, etc.
- Configuration hierarchy: env vars → GlobalSettings JSON → hardcoded defaults

**Brownfield constraints:**
- Must preserve all existing behavior (response formats, error handling, retry logic)
- Must maintain FastAPI dependency injection pattern
- Must support dual configuration system during migration
- Cannot break existing tests

**Unchanged behavior that must be preserved:**
- LLMClient: streaming/non-streaming modes, temperature handling, timeout behavior
- OpenAIEmbeddingClient: retry logic, cost tracking, batch processing, rate limiting
- Service APIs: method signatures, return types, error propagation
- Configuration hierarchy and precedence

## Design Drivers

**REQ-001: Abstract LLM Provider Interface**
- Design implication: Define `BaseLLMProvider` ABC with methods matching current `LLMClient`
- Must include: `generate_completion(messages, temperature, stream)` → `Union[str, Iterator[str]]`
- Configuration must be injectable via constructor

**REQ-002: Abstract Embedding Provider Interface**
- Design implication: Define `BaseEmbeddingProvider` ABC with methods matching current `OpenAIEmbeddingClient`
- Must include: `embed(text)` → `list[float]`, `embed_batch(texts, batch_size)` → `list[list[float]]`
- Optional methods: `get_stats()`, `reset_stats()` (for providers that support tracking)

**REQ-003: OpenAI LLM Provider Implementation**
- Design implication: Wrap existing `LLMClient` logic in `OpenAILLMProvider` class
- Preserve all behavior: streaming, temperature, timeout, response stripping
- Support custom base URLs for OpenAI-compatible endpoints

**REQ-004: OpenAI Embedding Provider Implementation**
- Design implication: Wrap existing `OpenAIEmbeddingClient` logic in `OpenAIEmbeddingProvider` class
- Preserve all behavior: retry logic, cost tracking, batch processing, rate limiting
- Keep tenacity decorator and error handling patterns

**REQ-005: LLM Provider Factory**
- Design implication: Create `get_llm_provider()` factory that reads `LLM_PROVIDER` config
- Must support: "openai", "openai-compatible" provider types
- Must be injectable via FastAPI `Depends`

**REQ-006: Embedding Provider Factory**
- Design implication: Create `get_embedding_provider()` factory that reads `EMBEDDING_PROVIDER` config
- Must support: "openai", "openai-compatible" provider types
- Must be independent from LLM provider factory

**AC-010: Behavior Preservation Validation**
- Verification impact: All existing tests must pass without modification
- Performance overhead must be < 1%
- Response formats must be identical

**NFR-001: Performance**
- Design implication: Provider abstraction must not introduce measurable latency
- Factory instantiation should be lightweight (no heavy initialization)

**NFR-005: Observability**
- Design implication: Provider selection must be logged for debugging
- Provider errors must be traceable to specific provider implementation

## Proposed Architecture

**Major components:**

1. **Abstract Base Classes** (`backend/providers/base.py`)
   - `BaseLLMProvider` - Abstract interface for LLM providers
   - `BaseEmbeddingProvider` - Abstract interface for embedding providers

2. **OpenAI Provider Implementations** (`backend/providers/openai.py`)
   - `OpenAILLMProvider` - Wraps OpenAI SDK for LLM operations
   - `OpenAIEmbeddingProvider` - Wraps OpenAI SDK for embedding operations

3. **Provider Factories** (`backend/providers/factory.py`)
   - `get_llm_provider()` - Selects and instantiates LLM provider based on config
   - `get_embedding_provider()` - Selects and instantiates embedding provider based on config

4. **Configuration Schema Updates** (`backend/schemas/settings.py`)
   - Add `LLM_PROVIDER` and `EMBEDDING_PROVIDER` fields
   - Add provider-specific configuration sections

**Responsibilities:**

- **BaseLLMProvider**: Define contract for LLM operations (generate_completion)
- **BaseEmbeddingProvider**: Define contract for embedding operations (embed, embed_batch)
- **OpenAILLMProvider**: Implement LLM operations using OpenAI SDK
- **OpenAIEmbeddingProvider**: Implement embedding operations using OpenAI SDK
- **Factories**: Read configuration, instantiate correct provider, handle errors
- **Services**: Use providers via dependency injection, remain provider-agnostic

**Interaction model:**

```
Service (e.g., GenerationService)
    ↓ (depends on)
Factory (get_llm_provider)
    ↓ (instantiates)
Concrete Provider (OpenAILLMProvider)
    ↓ (implements)
Abstract Provider (BaseLLMProvider)
```

**Key boundaries:**

- Services interact only with abstract provider interfaces
- Factories handle provider selection and instantiation
- Concrete providers encapsulate provider-specific logic
- Configuration system provides provider selection parameters

## Data Flow And Interfaces

**Inputs and entry points:**

1. **Configuration** (environment variables or GlobalSettings JSON)
   - `LLM_PROVIDER` → "openai" | "openai-compatible"
   - `EMBEDDING_PROVIDER` → "openai" | "openai-compatible"
   - Provider-specific: `OPENAI_API_KEY`, `OPENAI_API_BASE`, `CHAT_MODEL`, `EMBEDDING_MODEL`

2. **Service requests**
   - GenerationService.generate_answer() → calls provider.generate_completion()
   - RetrievalService.retrieve_relevant_chunks() → calls provider.embed()

**Internal interfaces:**

```python
# BaseLLMProvider interface
class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        pass

# BaseEmbeddingProvider interface
class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass
    
    @abstractmethod
    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        pass
```

**Data transformations:**

- No data transformation required - providers return same formats as current clients
- LLM: `Union[str, Iterator[str]]` (unchanged)
- Embedding: `list[float]` or `list[list[float]]` (unchanged)

**External systems:**

- OpenAI API (via OpenAI Python SDK)
- Future: Anthropic API, Ollama API, HuggingFace API (out of scope for this release)

## Design Decisions And Tradeoffs

**Decision 1: Adapter Pattern vs. Full Rewrite**
- **Why chosen:** Wrap existing `LLMClient` and `OpenAIEmbeddingClient` logic in provider classes
- **Tradeoff:** Slightly more code duplication, but preserves all existing behavior and reduces risk
- **Alternative rejected:** Rewrite from scratch - higher risk of introducing bugs

**Decision 2: Separate Factory Functions vs. Single Factory**
- **Why chosen:** Independent `get_llm_provider()` and `get_embedding_provider()` factories
- **Tradeoff:** Two factory functions instead of one, but enables independent provider selection
- **Benefit:** Users can mix providers (e.g., OpenAI for LLM, HuggingFace for embeddings)

**Decision 3: Keep Retry Logic in Provider Implementation**
- **Why chosen:** Preserve existing retry logic in `OpenAIEmbeddingProvider`
- **Tradeoff:** Retry logic is provider-specific, not abstracted
- **Rationale:** Different providers have different rate limits and error patterns; abstraction would be premature

**Decision 4: Optional Methods in Base Classes**
- **Why chosen:** Make `get_stats()` and `reset_stats()` optional (not in base class)
- **Tradeoff:** Not all providers will support statistics tracking
- **Rationale:** Statistics are OpenAI-specific; forcing all providers to implement would be artificial

**Decision 5: Configuration-Driven Provider Selection**
- **Why chosen:** Use environment variables (`LLM_PROVIDER`, `EMBEDDING_PROVIDER`) for provider selection
- **Tradeoff:** Requires configuration changes to switch providers
- **Benefit:** No code changes required, aligns with existing configuration patterns

## Alternatives Considered

**Alternative 1: Plugin System with Dynamic Loading**
- **Reason not chosen:** Over-engineered for current needs; adds complexity without clear benefit
- **Tradeoff:** Would enable third-party providers, but not required for initial release

**Alternative 2: Single Unified Provider Interface**
- **Reason not chosen:** LLM and embedding operations are fundamentally different
- **Tradeoff:** Would force artificial abstraction; separate interfaces are cleaner

**Alternative 3: Gradual Migration (Parallel Systems)**
- **Reason not chosen:** User decision was big bang migration
- **Tradeoff:** Lower risk but temporary inconsistency in codebase

**Alternative 4: Provider Registry Pattern**
- **Reason not chosen:** Adds complexity; simple factory functions are sufficient
- **Tradeoff:** Would enable runtime provider registration, but not needed

## Brownfield Integration Notes

**Existing boundary to respect:**
- FastAPI dependency injection: All services use `Depends()` pattern
- Configuration system: Dual system (legacy Settings + GlobalSettings) must be supported
- Service APIs: Method signatures cannot change

**Migration concerns:**
- 5 services must be updated simultaneously (big bang migration)
- Existing tests must pass without modification
- Custom base URL configuration must migrate cleanly

**Regression hotspots:**
- OpenAIEmbeddingClient retry logic: Must preserve exponential backoff and error handling
- LLMClient streaming: Must preserve streaming behavior and iterator protocol
- Cost tracking: Must preserve usage statistics in OpenAIEmbeddingProvider

## Non-Functional Design Considerations

**Performance:**
- Factory instantiation must be lightweight (< 1ms)
- Provider abstraction must not add measurable latency
- No caching or pooling required (FastAPI handles request lifecycle)

**Reliability:**
- Preserve existing retry logic in OpenAIEmbeddingProvider
- Provider instantiation errors must be clear and actionable
- Configuration errors must fail fast with helpful messages

**Security:**
- API keys must not be logged or exposed in error messages
- Provider configuration must follow existing security patterns
- No new security vulnerabilities introduced

**Observability:**
- Log provider selection at startup: "Using LLM provider: openai"
- Log provider errors with provider name: "OpenAILLMProvider error: ..."
- Preserve existing usage statistics in OpenAIEmbeddingProvider

**Accessibility or UX consistency:**
- Not applicable (backend-only feature)

## Open Questions

**Q-001: Should we implement a mock provider for testing?**
- **Next step:** Defer to implementation phase; can be added after initial release if needed

**Q-002: Should provider factories cache instances or create new instances per request?**
- **Next step:** Follow FastAPI's default behavior (new instance per request); optimize later if needed
