# Analysis: Provider Abstraction Layer

## Metadata

- Investigation name: Provider Abstraction Layer Research
- Feature or issue slug: 14.provider-abstraction-layer
- Owner: Research Agent
- Last updated: 2026-05-19

## Scope

- What is being investigated:
  - Current LLM provider usage patterns (OpenAI, Anthropic, Ollama)
  - Current embedding provider usage patterns (OpenAI, Local, HuggingFace)
  - Existing factory patterns and dependency injection mechanisms
  - Configuration and provider selection logic
  - Abstraction patterns already present in the codebase

- What is explicitly out of scope:
  - Implementation details of the abstraction layer
  - Migration strategy for existing code
  - Performance benchmarking between providers
  - Cost analysis of different providers

## Current State

### Observed Current Behavior

**LLM Provider:**
- Single provider implementation: `LLMClient` in `backend/llm/client.py:10-74`
- Uses OpenAI Python SDK exclusively
- Supports custom base URLs via `OPENAI_API_BASE` environment variable
- Currently configured to use `rag-combo` model via `http://localhost:20128/v1`
- Factory function `get_llm_client()` at line 67 uses FastAPI dependency injection

**Embedding Provider:**
- Single provider implementation: `OpenAIEmbeddingClient` in `backend/embeddings/openai_client.py:35-248`
- Uses OpenAI Python SDK exclusively
- Supports custom base URLs via `EMBEDDING_API_BASE` environment variable
- Currently configured to use `openrouter/openai/text-embedding-3-small` via `http://localhost:20128/v1`
- Multiple instantiation points across services (retrieval, indexing, safety)

**Configuration System:**
- Environment variables control API keys, base URLs, and model names
- `LLMSettings.provider` field exists in `backend/schemas/settings.py:45` but is hardcoded to "openai" and unused
- No runtime provider selection logic
- Configuration hierarchy: `.env` files → `GlobalSettings` JSON → hardcoded defaults

**Dependency Injection:**
- FastAPI `Depends` pattern used for service factories
- Services: generation, grounding, safety, retrieval, indexing
- Each service factory instantiates clients directly with config values

### Relevant Boundaries or Components

**Existing Abstraction Patterns:**
1. **Vector Store Abstraction** (`backend/indexing/base.py:4-88`)
   - Well-designed ABC with `VectorStore` interface
   - Single implementation: `WeaviateVectorStore`
   - Methods: `add_vectors`, `query_hybrid`, `delete_by_document`, `delete_by_collection`, `count`, `clear_all`

2. **Chunking Abstraction** (`backend/chunking/base.py:26-75`)
   - `BaseChunker` abstract base class
   - Multiple implementations: fixed, semantic, page-aware, heading-aware, parent-child

**Service Layer:**
- 5 core services depend on LLM/embedding clients:
  - `GenerationService` (`backend/chat/generation.py`)
  - `GroundingService` (`backend/chat/grounding.py`)
  - `SafetyService` (`backend/chat/safety.py`)
  - `RetrievalService` (`backend/chat/retrieval.py`)
  - `IndexingService` (`backend/indexing/indexing_service.py`)

**Client Usage Patterns:**
- LLM client: 4 service dependencies
- Embedding client: 4 service dependencies + 1 chunker dependency
- All services use factory functions with `Depends` injection

### Unchanged Behavior That Must Be Preserved

1. **OpenAI-Compatible Endpoint Support:**
   - Current system works with custom base URLs (Ollama, local models via OpenAI-compatible APIs)
   - This flexibility must remain

2. **FastAPI Dependency Injection:**
   - Service factories use `Depends` pattern
   - This pattern should be preserved for consistency

3. **Configuration Hierarchy:**
   - Environment variables → runtime settings → defaults
   - Existing configuration flow should remain intact

4. **Service Interfaces:**
   - Services expose specific methods (e.g., `generate_response`, `retrieve_documents`)
   - Service APIs should not change

5. **Vector Store Abstraction:**
   - Already well-designed and should serve as a reference pattern
   - Should not be disrupted

## Decision-Ready Summary

### What Matters Most

1. **No Provider Abstraction Exists:**
   - OpenAI SDK is directly imported and used in 8 files
   - No abstract interface for LLM or embedding providers
   - Provider switching requires code changes, not configuration changes

2. **Unused Provider Field:**
   - `LLMSettings.provider` field exists but is ignored
   - Indicates prior intent to support multiple providers

3. **Strong Abstraction Pattern Available:**
   - Vector store abstraction demonstrates the desired pattern
   - Can be used as a template for provider abstraction

4. **Multiple Instantiation Points:**
   - Embedding clients instantiated in 4+ locations
   - Consolidation needed before abstraction

### Strongest Supported Conclusion

The codebase currently has **zero provider abstraction** for LLM and embedding providers. All code is tightly coupled to the OpenAI SDK. However, the system demonstrates:

- **Good architectural patterns** (vector store abstraction, chunking abstraction)
- **Dependency injection infrastructure** (FastAPI `Depends`)
- **Configuration flexibility** (custom base URLs enable OpenAI-compatible providers)

The abstraction layer must:
1. Define abstract interfaces for LLM and embedding providers
2. Implement concrete providers (OpenAI, Anthropic, Ollama for LLM; OpenAI, Local, HuggingFace for embeddings)
3. Create factory functions that select providers based on configuration
4. Maintain backward compatibility with existing OpenAI-compatible endpoint usage

### Single Next Proving Step

Create a specification that defines:
1. Abstract provider interfaces (methods, signatures, error handling)
2. Provider selection mechanism (configuration-driven factory pattern)
3. Migration path for existing services
4. Backward compatibility guarantees

## Findings

### Finding 1: OpenAI SDK Hardcoded Throughout
- **Evidence:** 
  - `backend/llm/client.py:4` imports `openai`
  - `backend/embeddings/openai_client.py:7-8` imports `openai`
  - 8 files total import OpenAI SDK directly
  - No conditional imports or provider selection logic
- **Type:** Fact

### Finding 2: Provider Field Exists But Unused
- **Evidence:**
  - `backend/schemas/settings.py:45` defines `provider: str = "openai"`
  - No code reads or uses this field
  - Field is hardcoded, not configurable
- **Type:** Fact
- **Inference:** Prior development effort intended multi-provider support but was not completed

### Finding 3: Custom Base URL Enables OpenAI-Compatible Providers
- **Evidence:**
  - `backend/llm/client.py:23` uses `OpenAI(api_key=api_key, base_url=api_base)`
  - `.env` shows `OPENAI_API_BASE=http://localhost:20128/v1`
  - Current model is `rag-combo`, not a standard OpenAI model
- **Type:** Fact
- **Inference:** System already supports Ollama and other OpenAI-compatible providers via base URL override, but this is a workaround, not a proper abstraction

### Finding 4: Vector Store Abstraction Provides Reference Pattern
- **Evidence:**
  - `backend/indexing/base.py:4-88` defines `VectorStore` ABC
  - `backend/indexing/weaviate_store.py` implements the interface
  - Clean separation between interface and implementation
- **Type:** Fact
- **Inference:** This pattern should be replicated for LLM and embedding providers

### Finding 5: Embedding Client Instantiated in Multiple Locations
- **Evidence:**
  - `backend/chat/retrieval.py:237-240` instantiates `OpenAIEmbeddingClient`
  - `backend/indexing/indexing_service.py:284-288` instantiates `OpenAIEmbeddingClient`
  - `backend/chat/safety.py:46-50` lazy initialization
  - `backend/chunking/semantic_chunker.py:30` instantiates directly
- **Type:** Fact
- **Inference:** Consolidation into a single factory function is needed before abstraction

### Finding 6: No Anthropic or Native Ollama SDK Dependencies
- **Evidence:**
  - `requirements.txt` only lists `openai` library (line 5)
  - No `anthropic` or `ollama` packages installed
  - Zero references to Anthropic SDK in codebase
- **Type:** Fact
- **Inference:** New dependencies must be added to support native Anthropic and Ollama providers

### Finding 7: Service Layer Uses Dependency Injection
- **Evidence:**
  - `backend/chat/generation.py:70` uses `Depends(get_llm_client)`
  - `backend/chat/grounding.py:105` uses `Depends(get_llm_client)`
  - All 5 services follow this pattern
- **Type:** Fact
- **Inference:** Provider factories can integrate cleanly with existing dependency injection pattern

## Risks And Unknowns

### Risk 1: Breaking Changes to Existing Services
- **Why it matters:** 5 services depend on current client interfaces
- **Next proving step:** Define provider interface that matches or extends current `LLMClient` and `OpenAIEmbeddingClient` methods

### Risk 2: Configuration Complexity
- **Why it matters:** Multiple provider types, models, and endpoints increase configuration surface area
- **Next proving step:** Design configuration schema that supports provider selection without overwhelming users

### Risk 3: Provider-Specific Features
- **Why it matters:** Different providers have different capabilities (e.g., Anthropic's thinking tokens, OpenAI's function calling)
- **Next proving step:** Identify common interface subset and provider-specific extension points

### Risk 4: Migration Path Unclear
- **Why it matters:** Existing code uses OpenAI SDK directly; migration strategy affects development velocity
- **Next proving step:** Define backward compatibility approach (adapter pattern, gradual migration, or breaking change)

### Risk 5: Testing Multiple Providers
- **Why it matters:** Each provider requires API keys, different error handling, and different response formats
- **Next proving step:** Design testing strategy (mocks, integration tests, provider-specific test suites)

## Recommendation

### Next Skill or Artifact
Run `/aiddk-spec` to create a specification for the provider abstraction layer.

### Why
Research has identified:
- Current state (no abstraction, OpenAI-only)
- Existing patterns to follow (vector store abstraction)
- Integration points (service factories, dependency injection)
- Risks and unknowns (breaking changes, configuration complexity)

The next step is to define **what** the abstraction layer should do, **how** it should integrate with existing code, and **what** guarantees it must provide.

### Exact Next Prompt or Action
```
/aiddk-spec 14.provider-abstraction-layer

Create a specification for a provider abstraction layer that:
1. Defines abstract interfaces for LLM and embedding providers
2. Supports OpenAI, Anthropic, and Ollama for LLM
3. Supports OpenAI, Local, and HuggingFace for embeddings
4. Uses factory pattern for provider selection based on configuration
5. Maintains backward compatibility with existing OpenAI-compatible endpoint usage
6. Integrates with existing FastAPI dependency injection pattern
7. Follows the vector store abstraction pattern as a reference

Reference this analysis document for current state and constraints.
```

## Promotion Candidates

### For Constitution (Governance Rules)
None identified. This is a feature investigation, not a governance pattern.

### For Project Knowledge Base (Durable Facts)

**Candidate 1: Provider Abstraction Pattern**
- **Content:** "The codebase uses abstract base classes (ABC) for abstraction layers. See `VectorStore` in `backend/indexing/base.py` and `BaseChunker` in `backend/chunking/base.py` as reference patterns. New abstractions should follow this pattern."
- **Why:** Establishes architectural pattern for future abstractions

**Candidate 2: Dependency Injection Pattern**
- **Content:** "Services use FastAPI `Depends` pattern for dependency injection. Factory functions (e.g., `get_llm_client()`, `get_retrieval_service()`) are defined at module level and injected via `Depends`. New services and clients should follow this pattern."
- **Why:** Documents standard dependency injection approach

**Candidate 3: Configuration Hierarchy**
- **Content:** "Configuration follows a three-tier hierarchy: (1) Environment variables in `.env` files, (2) Runtime overrides via `GlobalSettings` JSON, (3) Hardcoded defaults in `config.py`. New configuration should respect this hierarchy."
- **Why:** Documents configuration precedence for future features
