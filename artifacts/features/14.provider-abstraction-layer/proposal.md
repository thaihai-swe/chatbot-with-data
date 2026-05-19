# Proposal: Provider Abstraction Layer

## 💡 The Problem

The codebase is tightly coupled to the OpenAI SDK. All LLM and embedding functionality directly imports and uses OpenAI's Python library, making it impossible to switch providers without code changes. This creates several pain points:

1. **Vendor Lock-In:** Cannot switch to Anthropic, Ollama, or other providers without modifying service code
2. **No Provider Choice:** Users cannot choose providers based on cost, performance, or feature requirements
3. **Testing Limitations:** Cannot mock or test provider interactions without OpenAI API access
4. **Configuration Rigidity:** The existing `LLMSettings.provider` field exists but is unused—indicating prior intent that was never completed

Current workaround: Custom base URLs enable OpenAI-compatible endpoints (like Ollama), but this is a hack, not a proper abstraction.

## 🎯 Objectives

Success means:

1. **Configuration-Driven Provider Selection:** Users can switch LLM and embedding providers via configuration without code changes
2. **Clean Abstraction:** Abstract interfaces define provider contracts, concrete implementations handle provider-specific details
3. **Seamless Migration:** All 5 existing services (generation, grounding, safety, retrieval, indexing) use the new abstraction with no behavior changes

## 🛠 High-Level Approach

**Phase 1: Define Abstractions**
- Create `BaseLLMProvider` abstract base class defining common LLM operations (generate, stream, count tokens)
- Create `BaseEmbeddingProvider` abstract base class defining common embedding operations (embed text, embed batch)
- Follow the existing `VectorStore` abstraction pattern as a reference

**Phase 2: Implement OpenAI Provider**
- Implement `OpenAILLMProvider` wrapping the existing OpenAI SDK logic
- Implement `OpenAIEmbeddingProvider` wrapping the existing embedding client logic
- Preserve all current behavior—this is a refactor, not a feature change

**Phase 3: Factory Pattern**
- Create `LLMProviderFactory` that selects provider based on configuration
- Create `EmbeddingProviderFactory` that selects provider based on configuration
- Support independent provider selection (e.g., OpenAI for LLM, different provider for embeddings)

**Phase 4: Big Bang Migration**
- Update all 5 services to use factory functions instead of direct OpenAI client instantiation
- Replace `get_llm_client()` with `get_llm_provider()`
- Consolidate embedding client instantiation points into single factory
- Update configuration to use new provider selection pattern

**Configuration Migration:**
- Old: `OPENAI_API_BASE=http://localhost:20128/v1` (custom endpoint)
- New: `LLM_PROVIDER=openai-compatible` + `OPENAI_COMPATIBLE_BASE_URL=http://localhost:20128/v1`

## ⚠️ Known Constraints / Risks

**Constraints:**
- **Common Interface Only:** Provider-specific features (Anthropic thinking tokens, OpenAI function calling) are out of scope. Abstraction exposes only the lowest common denominator.
- **Big Bang Migration:** All services must migrate in one release. No gradual rollout.
- **Breaking Configuration Change:** Existing custom base URL configuration will require updates.

**Risks:**
1. **Service Disruption:** Updating 5 services simultaneously increases risk of breaking existing functionality
2. **Testing Complexity:** Must verify OpenAI provider behavior matches current implementation exactly
3. **Configuration Migration:** Users with custom endpoints must update their `.env` files
4. **Provider Parity:** Different providers may have different response formats, error handling, and rate limits

**Mitigation:**
- Comprehensive integration tests comparing old vs new behavior
- Adapter pattern wraps existing OpenAI client to minimize logic changes
- Clear migration guide for configuration updates
- Preserve existing error handling and retry logic

## ✅ Success Criteria

- [ ] `BaseLLMProvider` and `BaseEmbeddingProvider` abstract base classes exist with clear contracts
- [ ] `OpenAILLMProvider` and `OpenAIEmbeddingProvider` implementations pass all existing tests
- [ ] `LLMProviderFactory` and `EmbeddingProviderFactory` select providers based on configuration
- [ ] All 5 services use factory functions instead of direct OpenAI SDK imports
- [ ] Configuration supports independent LLM and embedding provider selection
- [ ] Existing functionality (generation, retrieval, safety, grounding, indexing) works identically to before
- [ ] No direct `import openai` statements remain in service code (only in provider implementations)
- [ ] Migration guide documents configuration changes for users with custom endpoints

---
**Status:** 🟡 Awaiting Alignment
*(Move to 🟢 Aligned once user approves this proposal)*
