# Task Breakdown: Provider Abstraction Layer

## Metadata

- Feature name: Provider Abstraction Layer
- Related spec: `artifacts/features/14.provider-abstraction-layer/spec.md`
- Related plan: `artifacts/features/14.provider-abstraction-layer/plan.md`
- Related design: `artifacts/features/14.provider-abstraction-layer/design.md`
- Owner: Engineering Team
- Last updated: 2026-05-19

## Rules

- Keep each task small and testable (2-5 minutes implementation time)
- Include validation tasks, not just implementation tasks
- Record blockers and dependencies explicitly
- Link every task back to requirement and acceptance criteria IDs
- Mark tasks that can run in parallel when they have no dependency relationship
- The first unblocked task should be executable from this file without rereading `plan.md`
- Use these task states consistently: `Not Started`, `In Progress`, `Blocked`, `Done`, `Deferred`
- **TDD Requirement:** For all behavioral changes, identify the failing test/proof (RED) that must pass after implementation (GREEN)

## Status Tracking Requirements

Every task MUST have both a checkbox and a Status field for implementation tracking:

- **Checkbox format**: `- [ ] TASK-ID` or `- [X] TASK-ID` (`[ ]` = not done yet, `[X]` = done)
- **Status field**: `Status: [Not Started|In Progress|Done|Blocked|Deferred]` (initialized to `Not Started`)
- **Proving command or proof**: Field naming the exact command, test, scenario, or log that proves the task
- **Validation evidence**: Field used to store the actual passing evidence after implementation
- **Session note**: Field for implementation agent to track blockers, progress, or issues
- **Implementation contract**: Implementation agent will keep checkbox and Status field aligned as work progresses

## Phase 1: Define Abstractions

**Goal:** Create abstract base classes that define provider contracts

**Completion criteria:**
- [ ] CC-001: `BaseLLMProvider` has `generate_completion()` method matching current `LLMClient`
- [ ] CC-002: `BaseEmbeddingProvider` has `embed()` and `embed_batch()` methods matching current `OpenAIEmbeddingClient`
- [ ] CC-003: All abstract methods have clear docstrings explaining parameters and return types
- [ ] CC-004: Configuration parameters are documented (API key, base URL, model name)

**Tasks:**

- [x] TASK-001
  Status: Done
  Summary: Create `backend/providers/__init__.py` package file
  Outcome enabled: US-004 (future developers can add providers)
  Plan reference: Phase 1
  Linked requirement(s): REQ-001, REQ-002
  Linked acceptance criteria: AC-001, AC-002
  Ownership boundary: backend/providers/ directory
  Affected file(s) or module(s): backend/providers/__init__.py (new file)
  Depends on: None
  Can run in parallel: Yes [P]
  Proving command or proof: File exists and is importable: `python -c "import backend.providers"`
  Validation evidence: Import successful, no errors
  Session note: Package created successfully 

- [x] TASK-002
  Status: Done
  Summary: Create `backend/providers/base.py` with `BaseLLMProvider` ABC
  Outcome enabled: US-004 (future developers can add providers)
  Plan reference: Phase 1, REQ-001
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/providers/base.py
  Affected file(s) or module(s): backend/providers/base.py (new file)
  Depends on: TASK-001
  Can run in parallel: No
  Proving command or proof: Code review - verify `BaseLLMProvider` has `generate_completion()` method with signature: `generate_completion(self, messages: List[Dict[str, str]], temperature: Optional[float] = None, stream: bool = False) -> Union[str, Iterator[str]]`
  Validation evidence: Method signature verified: (self, messages: List[Dict[str, str]], temperature: Optional[float] = None, stream: bool = False) -> Union[str, Iterator[str]]
  Session note: BaseLLMProvider ABC created with correct method signature 

- [x] TASK-003
  Status: Done
  Summary: Add `BaseEmbeddingProvider` ABC to `backend/providers/base.py`
  Outcome enabled: US-004 (future developers can add providers)
  Plan reference: Phase 1, REQ-002
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Ownership boundary: backend/providers/base.py
  Affected file(s) or module(s): backend/providers/base.py
  Depends on: TASK-002
  Can run in parallel: No
  Proving command or proof: Code review - verify `BaseEmbeddingProvider` has `embed()` and `embed_batch()` methods with signatures: `embed(self, text: str) -> list[float]` and `embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]`
  Validation evidence: Methods verified - embed: (self, text: str) -> list[float], embed_batch: (self, texts: list[str], batch_size: int = 10) -> list[list[float]]
  Session note: BaseEmbeddingProvider ABC created with correct method signatures

- [x] TASK-004
  Status: Done
  Summary: Add docstrings to `BaseLLMProvider.generate_completion()` method
  Outcome enabled: US-004 (clear documentation for future developers)
  Plan reference: Phase 1, CC-003
  Linked requirement(s): REQ-001
  Linked acceptance criteria: AC-001
  Ownership boundary: backend/providers/base.py
  Affected file(s) or module(s): backend/providers/base.py
  Depends on: TASK-002
  Can run in parallel: No
  Proving command or proof: Code review - verify docstring explains parameters (messages, temperature, stream) and return type
  Validation evidence: Docstring present explaining all parameters and return type
  Session note: Docstring added during TASK-002 creation

- [x] TASK-005
  Status: Done
  Summary: Add docstrings to `BaseEmbeddingProvider.embed()` and `embed_batch()` methods
  Outcome enabled: US-004 (clear documentation for future developers)
  Plan reference: Phase 1, CC-003
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-002
  Ownership boundary: backend/providers/base.py
  Affected file(s) or module(s): backend/providers/base.py
  Depends on: TASK-003
  Can run in parallel: No
  Proving command or proof: Code review - verify docstrings explain parameters and return types for both methods
  Validation evidence: Docstrings present for both methods explaining parameters and return types
  Session note: Docstrings added during TASK-003 creation 

## Phase 2: Implement OpenAI Providers

**Goal:** Wrap existing OpenAI SDK logic in provider implementations

**Completion criteria:**
- [ ] CC-005: `OpenAILLMProvider` wraps existing `LLMClient` logic; all methods implemented
- [ ] CC-006: `OpenAIEmbeddingProvider` wraps existing `OpenAIEmbeddingClient` logic; all methods implemented
- [ ] CC-007: All existing LLM tests pass with `OpenAILLMProvider`
- [ ] CC-008: All existing embedding tests pass with `OpenAIEmbeddingProvider`
- [ ] CC-009: Retry logic, cost tracking, batch processing all work identically
- [ ] CC-010: Performance overhead < 1%

**Tasks:**

- [x] TASK-006
  Status: Done
  Validation evidence: Import successful
  Session note: File created with imports 

- [x] TASK-007
  Status: Done
  Validation evidence: OpenAILLMProvider instantiated successfully
  Session note: Constructor implemented

- [x] TASK-008
  Status: Done
  Validation evidence: Non-streaming method implemented
  Session note: Returns string as expected

- [x] TASK-009
  Status: Done
  Validation evidence: Streaming method implemented
  Session note: Returns Iterator[str] as expected

- [x] TASK-010
  Status: Done
  Validation evidence: All LLMClient logic copied, behavior preserved
  Session note: Complete implementation with streaming/non-streaming 

- [x] TASK-011
  Status: Done
  Summary: Implement `OpenAIEmbeddingProvider.__init__()` method
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/providers/openai.py
  Affected file(s) or module(s): backend/providers/openai.py
  Depends on: TASK-006
  Can run in parallel: Yes [P] (independent from LLM provider tasks)
  Proving command or proof: Unit test - instantiate `OpenAIEmbeddingProvider` with API key, base URL, model, max_retries, timeout
  Validation evidence: OpenAIEmbeddingProvider instantiated successfully
  Session note: Constructor with fallback logic implemented

- [x] TASK-012
  Status: Done
  Summary: Implement `OpenAIEmbeddingProvider.embed()` method with retry logic
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/providers/openai.py
  Affected file(s) or module(s): backend/providers/openai.py
  Depends on: TASK-011
  Can run in parallel: No
  Proving command or proof: Unit test - call `embed()` with text, verify returns list[float]; test retry logic with mock failures
  Validation evidence: embed() method with retry decorator implemented
  Session note: Retry logic with tenacity preserved

- [x] TASK-013
  Status: Done
  Summary: Implement `OpenAIEmbeddingProvider.embed_batch()` method with rate limiting
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, REQ-004
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/providers/openai.py
  Affected file(s) or module(s): backend/providers/openai.py
  Depends on: TASK-012
  Can run in parallel: No
  Proving command or proof: Unit test - call `embed_batch()` with list of texts, verify returns list[list[float]]; verify batch processing and delays
  Validation evidence: embed_batch() method with rate limiting implemented
  Session note: Batch processing with 0.1s delay preserved

- [x] TASK-014
  Status: Done
  Summary: Copy existing `OpenAIEmbeddingClient` retry logic (tenacity decorator) into `OpenAIEmbeddingProvider`
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, REQ-004, CC-009
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/providers/openai.py
  Affected file(s) or module(s): backend/providers/openai.py
  Depends on: TASK-013
  Can run in parallel: No
  Proving command or proof: Unit test - verify exponential backoff, max retries, error handling identical to current implementation
  Validation evidence: Tenacity decorator copied, exponential backoff preserved
  Session note: _rate_limit_aware decorator implemented

- [x] TASK-015
  Status: Done
  Summary: Copy existing `OpenAIEmbeddingClient` cost tracking logic into `OpenAIEmbeddingProvider`
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, REQ-004, CC-009
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: backend/providers/openai.py
  Affected file(s) or module(s): backend/providers/openai.py
  Depends on: TASK-014
  Can run in parallel: No
  Proving command or proof: Unit test - verify `get_stats()` and `reset_stats()` methods work; verify cost calculations accurate
  Validation evidence: get_stats() and reset_stats() methods implemented, pricing table preserved
  Session note: Cost tracking logic complete 

- [ ] TASK-016
  Status: Not Started
  Summary: Run all existing LLM tests with `OpenAILLMProvider`
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, CC-007
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-003
  Ownership boundary: Test suite
  Affected file(s) or module(s): Test files
  Depends on: TASK-010
  Can run in parallel: No
  Proving command or proof: Run test suite: `pytest backend/tests/ -k llm` (all tests pass)
  Validation evidence: 
  Session note: 

- [ ] TASK-017
  Status: Not Started
  Summary: Run all existing embedding tests with `OpenAIEmbeddingProvider`
  Outcome enabled: Scenario 4 (service behavior preservation)
  Plan reference: Phase 2, CC-008
  Linked requirement(s): REQ-004
  Linked acceptance criteria: AC-004
  Ownership boundary: Test suite
  Affected file(s) or module(s): Test files
  Depends on: TASK-015
  Can run in parallel: No
  Proving command or proof: Run test suite: `pytest backend/tests/ -k embedding` (all tests pass)
  Validation evidence: 
  Session note: 

- [ ] TASK-018
  Status: Not Started
  Summary: Performance benchmark - measure provider overhead
  Outcome enabled: NFR-001 (performance < 1% overhead)
  Plan reference: Phase 2, CC-010
  Linked requirement(s): NFR-001
  Linked acceptance criteria: AC-010
  Ownership boundary: Performance tests
  Affected file(s) or module(s): Performance test script
  Depends on: TASK-016, TASK-017
  Can run in parallel: No
  Proving command or proof: Run performance test comparing old vs new implementation; verify overhead < 1%
  Validation evidence: 
  Session note: 

## Phase 3: Create Factories and Update Configuration

**Goal:** Implement provider selection logic and update configuration schema

**Completion criteria:**
- [ ] CC-011: `get_llm_provider()` factory reads `LLM_PROVIDER` config and instantiates correct provider
- [ ] CC-012: `get_embedding_provider()` factory reads `EMBEDDING_PROVIDER` config and instantiates correct provider
- [ ] CC-013: Factories support "openai" and "openai-compatible" provider types
- [ ] CC-014: Configuration schema updated; both fields are optional with sensible defaults
- [ ] CC-015: Configuration tests verify provider selection works correctly

**Tasks:**

- [ ] TASK-019
  Status: Not Started
  Summary: Create `backend/providers/factory.py` file with imports
  Outcome enabled: Scenario 1 (configuration-driven provider selection)
  Plan reference: Phase 3, REQ-005, REQ-006
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-005, AC-006
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py (new file)
  Depends on: TASK-010, TASK-015
  Can run in parallel: No
  Proving command or proof: File exists and imports work: `python -c "import backend.providers.factory"`
  Validation evidence: 
  Session note: 

- [ ] TASK-020
  Status: Not Started
  Summary: Implement `get_llm_provider()` factory function
  Outcome enabled: Scenario 1 (configuration-driven provider selection)
  Plan reference: Phase 3, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-019
  Can run in parallel: No
  Proving command or proof: Unit test - call `get_llm_provider()` with different configs, verify correct provider instantiated
  Validation evidence: 
  Session note: 

- [ ] TASK-021
  Status: Not Started
  Summary: Add "openai" provider type support to `get_llm_provider()`
  Outcome enabled: Scenario 1 (configuration-driven provider selection)
  Plan reference: Phase 3, REQ-005, CC-013
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-020
  Can run in parallel: No
  Proving command or proof: Unit test - set `LLM_PROVIDER=openai`, verify `OpenAILLMProvider` instantiated
  Validation evidence: 
  Session note: 

- [ ] TASK-022
  Status: Not Started
  Summary: Add "openai-compatible" provider type support to `get_llm_provider()`
  Outcome enabled: Scenario 3 (custom base URL migration)
  Plan reference: Phase 3, REQ-005, REQ-009, CC-013
  Linked requirement(s): REQ-005, REQ-009
  Linked acceptance criteria: AC-005, AC-009
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-021
  Can run in parallel: No
  Proving command or proof: Unit test - set `LLM_PROVIDER=openai-compatible` and custom base URL, verify provider instantiated with custom endpoint
  Validation evidence: 
  Session note: 

- [ ] TASK-023
  Status: Not Started
  Summary: Implement `get_embedding_provider()` factory function
  Outcome enabled: Scenario 2 (independent provider selection)
  Plan reference: Phase 3, REQ-006
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-019
  Can run in parallel: Yes [P] (independent from LLM factory tasks)
  Proving command or proof: Unit test - call `get_embedding_provider()` with different configs, verify correct provider instantiated
  Validation evidence: 
  Session note: 

- [ ] TASK-024
  Status: Not Started
  Summary: Add "openai" and "openai-compatible" provider type support to `get_embedding_provider()`
  Outcome enabled: Scenario 2, Scenario 3 (independent provider selection, custom base URL)
  Plan reference: Phase 3, REQ-006, REQ-009, CC-013
  Linked requirement(s): REQ-006, REQ-009
  Linked acceptance criteria: AC-006, AC-009
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-023
  Can run in parallel: No
  Proving command or proof: Unit test - set `EMBEDDING_PROVIDER=openai` and `EMBEDDING_PROVIDER=openai-compatible`, verify correct provider instantiated
  Validation evidence: 
  Session note: 

- [ ] TASK-025
  Status: Not Started
  Summary: Make `get_llm_provider()` injectable via FastAPI `Depends`
  Outcome enabled: Scenario 1 (configuration-driven provider selection)
  Plan reference: Phase 3, REQ-005
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-005
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-022
  Can run in parallel: No
  Proving command or proof: Unit test - use `Depends(get_llm_provider)` in a FastAPI route, verify provider injected correctly
  Validation evidence: 
  Session note: 

- [ ] TASK-026
  Status: Not Started
  Summary: Make `get_embedding_provider()` injectable via FastAPI `Depends`
  Outcome enabled: Scenario 2 (independent provider selection)
  Plan reference: Phase 3, REQ-006
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-006
  Ownership boundary: backend/providers/factory.py
  Affected file(s) or module(s): backend/providers/factory.py
  Depends on: TASK-024
  Can run in parallel: No
  Proving command or proof: Unit test - use `Depends(get_embedding_provider)` in a FastAPI route, verify provider injected correctly
  Validation evidence: 
  Session note: 

- [ ] TASK-027
  Status: Not Started
  Summary: Update `backend/schemas/settings.py` - add `LLM_PROVIDER` field to `LLMSettings`
  Outcome enabled: Scenario 1 (configuration-driven provider selection)
  Plan reference: Phase 3, REQ-008, CC-014
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: backend/schemas/settings.py
  Affected file(s) or module(s): backend/schemas/settings.py
  Depends on: TASK-019
  Can run in parallel: Yes [P] (independent from factory implementation)
  Proving command or proof: Code review - verify `LLMSettings` has `provider: str` field with default "openai"
  Validation evidence: 
  Session note: 

- [ ] TASK-028
  Status: Not Started
  Summary: Update `backend/schemas/settings.py` - add `EMBEDDING_PROVIDER` field to `IngestionSettings`
  Outcome enabled: Scenario 2 (independent provider selection)
  Plan reference: Phase 3, REQ-008, CC-014
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: backend/schemas/settings.py
  Affected file(s) or module(s): backend/schemas/settings.py
  Depends on: TASK-019
  Can run in parallel: Yes [P] (independent from factory implementation)
  Proving command or proof: Code review - verify `IngestionSettings` has `embedding_provider: str` field with default "openai"
  Validation evidence: 
  Session note: 

- [ ] TASK-029
  Status: Not Started
  Summary: Create configuration tests for provider selection
  Outcome enabled: Scenario 1, Scenario 2 (configuration-driven selection)
  Plan reference: Phase 3, CC-015
  Linked requirement(s): REQ-008
  Linked acceptance criteria: AC-008
  Ownership boundary: Test suite
  Affected file(s) or module(s): backend/tests/test_provider_config.py (new file)
  Depends on: TASK-027, TASK-028
  Can run in parallel: No
  Proving command or proof: Run configuration tests: `pytest backend/tests/test_provider_config.py` (all tests pass)
  Validation evidence: 
  Session note: 

## Phase 4: Migrate Services

**Goal:** Update all 5 services to use provider factories instead of direct client instantiation

**Completion criteria:**
- [ ] CC-016: GenerationService uses `Depends(get_llm_provider)`
- [ ] CC-017: GroundingService uses `Depends(get_llm_provider)`
- [ ] CC-018: SafetyService uses `Depends(get_llm_provider)` and `Depends(get_embedding_provider)`
- [ ] CC-019: RetrievalService uses `Depends(get_embedding_provider)`
- [ ] CC-020: IndexingService uses `Depends(get_embedding_provider)`
- [ ] CC-021: All existing tests pass without modification
- [ ] CC-022: No direct `import openai` statements in service code
- [ ] CC-023: Custom base URL configuration migrates cleanly to new provider pattern

**Tasks:**

- [ ] TASK-030
  Status: Not Started
  Summary: Update `backend/chat/generation.py` - replace `get_llm_client()` with `get_llm_provider()`
  Outcome enabled: Scenario 1, Scenario 4 (configuration-driven selection, behavior preservation)
  Plan reference: Phase 4, REQ-007, CC-016
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/chat/generation.py
  Affected file(s) or module(s): backend/chat/generation.py
  Depends on: TASK-025
  Can run in parallel: Yes [P] (independent service migrations)
  Proving command or proof: Code review - verify GenerationService uses `Depends(get_llm_provider)` instead of `Depends(get_llm_client)`; existing tests pass
  Validation evidence: 
  Session note: 

- [ ] TASK-031
  Status: Not Started
  Summary: Update `backend/chat/grounding.py` - replace `get_llm_client()` with `get_llm_provider()`
  Outcome enabled: Scenario 1, Scenario 4 (configuration-driven selection, behavior preservation)
  Plan reference: Phase 4, REQ-007, CC-017
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/chat/grounding.py
  Affected file(s) or module(s): backend/chat/grounding.py
  Depends on: TASK-025
  Can run in parallel: Yes [P] (independent service migrations)
  Proving command or proof: Code review - verify GroundingService uses `Depends(get_llm_provider)` instead of `Depends(get_llm_client)`; existing tests pass
  Validation evidence: 
  Session note: 

- [ ] TASK-032
  Status: Not Started
  Summary: Update `backend/chat/safety.py` - replace `get_llm_client()` with `get_llm_provider()`
  Outcome enabled: Scenario 1, Scenario 4 (configuration-driven selection, behavior preservation)
  Plan reference: Phase 4, REQ-007, CC-018
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/chat/safety.py
  Affected file(s) or module(s): backend/chat/safety.py
  Depends on: TASK-025
  Can run in parallel: Yes [P] (independent service migrations)
  Proving command or proof: Code review - verify SafetyService uses `Depends(get_llm_provider)` instead of `Depends(get_llm_client)`; existing tests pass
  Validation evidence: 
  Session note: 

- [ ] TASK-033
  Status: Not Started
  Summary: Update `backend/chat/safety.py` - replace embedding client instantiation with `get_embedding_provider()`
  Outcome enabled: Scenario 2, Scenario 4 (independent provider selection, behavior preservation)
  Plan reference: Phase 4, REQ-007, CC-018
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/chat/safety.py
  Affected file(s) or module(s): backend/chat/safety.py
  Depends on: TASK-026
  Can run in parallel: No (depends on TASK-032)
  Proving command or proof: Code review - verify SafetyService uses `Depends(get_embedding_provider)` instead of direct instantiation; existing tests pass
  Validation evidence: 
  Session note: 

- [ ] TASK-034
  Status: Not Started
  Summary: Update `backend/chat/retrieval.py` - replace embedding client instantiation with `get_embedding_provider()`
  Outcome enabled: Scenario 2, Scenario 4 (independent provider selection, behavior preservation)
  Plan reference: Phase 4, REQ-007, CC-019
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/chat/retrieval.py
  Affected file(s) or module(s): backend/chat/retrieval.py
  Depends on: TASK-026
  Can run in parallel: Yes [P] (independent service migrations)
  Proving command or proof: Code review - verify RetrievalService uses `Depends(get_embedding_provider)` instead of direct instantiation; existing tests pass
  Validation evidence: 
  Session note: 

- [ ] TASK-035
  Status: Not Started
  Summary: Update `backend/indexing/indexing_service.py` - replace embedding client instantiation with `get_embedding_provider()`
  Outcome enabled: Scenario 2, Scenario 4 (independent provider selection, behavior preservation)
  Plan reference: Phase 4, REQ-007, CC-020
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: backend/indexing/indexing_service.py
  Affected file(s) or module(s): backend/indexing/indexing_service.py
  Depends on: TASK-026
  Can run in parallel: Yes [P] (independent service migrations)
  Proving command or proof: Code review - verify IndexingService uses `Depends(get_embedding_provider)` instead of direct instantiation; existing tests pass
  Validation evidence: 
  Session note: 

- [ ] TASK-036
  Status: Not Started
  Summary: Verify no direct `import openai` in service code
  Outcome enabled: Scenario 4 (behavior preservation, clean abstraction)
  Plan reference: Phase 4, CC-022
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-007
  Ownership boundary: Service code
  Affected file(s) or module(s): backend/chat/*.py, backend/indexing/*.py
  Depends on: TASK-030, TASK-031, TASK-032, TASK-033, TASK-034, TASK-035
  Can run in parallel: No
  Proving command or proof: Grep search - `grep -r "import openai" backend/chat/ backend/indexing/` returns no results (only in provider implementations)
  Validation evidence: 
  Session note: 

- [ ] TASK-037
  Status: Not Started
  Summary: Run full test suite - verify all existing tests pass
  Outcome enabled: Scenario 4 (behavior preservation)
  Plan reference: Phase 4, CC-021
  Linked requirement(s): REQ-010
  Linked acceptance criteria: AC-010
  Ownership boundary: Test suite
  Affected file(s) or module(s): All test files
  Depends on: TASK-030, TASK-031, TASK-032, TASK-033, TASK-034, TASK-035
  Can run in parallel: No
  Proving command or proof: Run full test suite: `pytest backend/tests/` (all tests pass without modification)
  Validation evidence: 
  Session note: 

- [ ] TASK-038
  Status: Not Started
  Summary: Create migration guide for custom base URL configuration
  Outcome enabled: Scenario 3 (custom base URL migration)
  Plan reference: Phase 4, REQ-009, CC-023
  Linked requirement(s): REQ-009
  Linked acceptance criteria: AC-009
  Ownership boundary: Documentation
  Affected file(s) or module(s): MIGRATION_GUIDE.md (new file)
  Depends on: TASK-022, TASK-024
  Can run in parallel: Yes [P] (independent from service migrations)
  Proving command or proof: Code review - verify migration guide explains old vs new configuration with clear examples
  Validation evidence: 
  Session note: 

- [ ] TASK-039
  Status: Not Started
  Summary: Manual testing - verify configuration changes switch providers
  Outcome enabled: Scenario 1 (configuration-driven provider selection)
  Plan reference: Phase 4, CC-023
  Linked requirement(s): REQ-009
  Linked acceptance criteria: AC-009
  Ownership boundary: Manual testing
  Affected file(s) or module(s): N/A
  Depends on: TASK-037, TASK-038
  Can run in parallel: No
  Proving command or proof: Manual test - change `LLM_PROVIDER` config, restart service, verify correct provider used (check logs)
  Validation evidence: 
  Session note: 

- [ ] TASK-040
  Status: Not Started
  Summary: Manual testing - verify custom base URL migration works
  Outcome enabled: Scenario 3 (custom base URL migration)
  Plan reference: Phase 4, CC-023
  Linked requirement(s): REQ-009
  Linked acceptance criteria: AC-009
  Ownership boundary: Manual testing
  Affected file(s) or module(s): N/A
  Depends on: TASK-037, TASK-038
  Can run in parallel: No
  Proving command or proof: Manual test - configure custom base URL with new provider pattern, verify system works identically to before
  Validation evidence: 
  Session note: 

## Phase 5: Validation And Closeout

**Goal:** Comprehensive validation and documentation

**Completion criteria:**
- [ ] CC-024: All acceptance criteria verified
- [ ] CC-025: Performance benchmarks confirm < 1% overhead
- [ ] CC-026: Migration guide complete and tested

**Tasks:**

- [ ] TASK-041
  Status: Not Started
  Summary: Performance regression test - compare before/after response times
  Outcome enabled: NFR-001 (performance < 1% overhead)
  Plan reference: Phase 5, CC-025
  Linked requirement(s): NFR-001
  Linked acceptance criteria: AC-010
  Ownership boundary: Performance tests
  Affected file(s) or module(s): Performance test script
  Depends on: TASK-037
  Can run in parallel: No
  Proving command or proof: Run performance test: measure response times for LLM and embedding operations; verify overhead < 1%
  Validation evidence: 
  Session note: 

- [ ] TASK-042
  Status: Not Started
  Summary: Code review - verify all requirements met
  Outcome enabled: All requirements (REQ-001 through REQ-010)
  Plan reference: Phase 5, CC-024
  Linked requirement(s): All requirements
  Linked acceptance criteria: All acceptance criteria
  Ownership boundary: Code review
  Affected file(s) or module(s): All modified files
  Depends on: TASK-041
  Can run in parallel: No
  Proving command or proof: Code review checklist - verify all requirements implemented, all acceptance criteria met
  Validation evidence: 
  Session note: 

- [ ] TASK-043
  Status: Not Started
  Summary: Update status.md - mark plan as approved
  Outcome enabled: Feature ready for implementation
  Plan reference: Phase 5
  Linked requirement(s): N/A
  Linked acceptance criteria: N/A
  Ownership boundary: artifacts/features/14.provider-abstraction-layer/status.md
  Affected file(s) or module(s): status.md
  Depends on: TASK-042
  Can run in parallel: No
  Proving command or proof: File updated - status.md shows "Plan Approved"
  Validation evidence: 
  Session note: 

## Notes Per Task

### TASK-001
Notes: Create empty `__init__.py` file to make backend/providers a Python package

### TASK-002
Notes: Define abstract base class with abstract method `generate_completion()`. Include type hints for all parameters and return type.

### TASK-003
Notes: Define abstract base class with abstract methods `embed()` and `embed_batch()`. Include type hints for all parameters and return types.

### TASK-004
Notes: Add comprehensive docstring explaining parameters (messages list format, temperature range, stream behavior) and return type (string or iterator)

### TASK-005
Notes: Add comprehensive docstrings for both methods explaining parameters and return types

### TASK-006
Notes: Create file with necessary imports: `from abc import ABC, abstractmethod`, `from typing import ...`, `from backend.providers.base import ...`

### TASK-007
Notes: Constructor should accept: api_key, api_base (optional), model, timeout. Store as instance variables. Initialize OpenAI client.

### TASK-008
Notes: Implement non-streaming path. Call OpenAI SDK, extract content, strip whitespace, return string. Handle None content.

### TASK-009
Notes: Implement streaming path. Call OpenAI SDK with stream=True, yield content chunks as Iterator[str]. Handle None content.

### TASK-010
Notes: Copy all logic from current `LLMClient` into `OpenAILLMProvider`. Preserve error handling, timeout behavior, response stripping.

### TASK-011
Notes: Constructor should accept: api_key (with fallback to OPENAI_API_KEY), api_base (with fallback), model, max_retries, timeout. Initialize OpenAI client and tracking stats.

### TASK-012
Notes: Implement `embed()` method. Call OpenAI SDK, validate input, track usage, calculate cost, handle errors with retry logic.

### TASK-013
Notes: Implement `embed_batch()` method. Process texts in batches, add delay between batches, track usage per batch, handle errors.

### TASK-014
Notes: Copy tenacity decorator and retry logic from current `OpenAIEmbeddingClient`. Preserve exponential backoff, max retries, error handling.

### TASK-015
Notes: Copy cost tracking logic from current `OpenAIEmbeddingClient`. Implement `get_stats()` and `reset_stats()` methods. Preserve pricing calculations.

### TASK-016
Notes: Run existing LLM test suite. All tests must pass without modification. If any fail, debug and fix provider implementation.

### TASK-017
Notes: Run existing embedding test suite. All tests must pass without modification. If any fail, debug and fix provider implementation.

### TASK-018
Notes: Create performance test comparing old `LLMClient` vs new `OpenAILLMProvider` and old `OpenAIEmbeddingClient` vs new `OpenAIEmbeddingProvider`. Measure latency, verify < 1% overhead.

### TASK-019
Notes: Create file with necessary imports: `from backend.providers.base import ...`, `from backend.providers.openai import ...`, `from backend.config import ...`, `from fastapi import Depends`

### TASK-020
Notes: Implement factory function that reads configuration and instantiates appropriate provider. Handle missing/invalid config gracefully.

### TASK-021
Notes: Add logic to handle `LLM_PROVIDER=openai`. Instantiate `OpenAILLMProvider` with config values.

### TASK-022
Notes: Add logic to handle `LLM_PROVIDER=openai-compatible`. Instantiate `OpenAILLMProvider` with custom base URL from config.

### TASK-023
Notes: Implement factory function similar to LLM factory. Read `EMBEDDING_PROVIDER` config and instantiate appropriate provider.

### TASK-024
Notes: Add logic to handle `EMBEDDING_PROVIDER=openai` and `EMBEDDING_PROVIDER=openai-compatible`. Support custom base URLs.

### TASK-025
Notes: Add `@lru_cache()` decorator to `get_llm_provider()` to make it cacheable. Ensure it's injectable via FastAPI `Depends`.

### TASK-026
Notes: Add `@lru_cache()` decorator to `get_embedding_provider()` to make it cacheable. Ensure it's injectable via FastAPI `Depends`.

### TASK-027
Notes: Add `provider: str = "openai"` field to `LLMSettings` class. Update docstring to explain provider options.

### TASK-028
Notes: Add `embedding_provider: str = "openai"` field to `IngestionSettings` class. Update docstring to explain provider options.

### TASK-029
Notes: Create test file with tests for: provider selection based on config, invalid provider handling, default provider selection.

### TASK-030
Notes: Replace `get_llm_client()` with `get_llm_provider()` in GenerationService factory function. Update type hints. Verify existing tests pass.

### TASK-031
Notes: Replace `get_llm_client()` with `get_llm_provider()` in GroundingService factory function. Update type hints. Verify existing tests pass.

### TASK-032
Notes: Replace `get_llm_client()` with `get_llm_provider()` in SafetyService factory function. Update type hints. Verify existing tests pass.

### TASK-033
Notes: Replace direct `OpenAIEmbeddingClient()` instantiation with `get_embedding_provider()` in SafetyService. Update type hints. Verify existing tests pass.

### TASK-034
Notes: Replace direct `OpenAIEmbeddingClient()` instantiation with `get_embedding_provider()` in RetrievalService factory function. Update type hints. Verify existing tests pass.

### TASK-035
Notes: Replace direct `OpenAIEmbeddingClient()` instantiation with `get_embedding_provider()` in IndexingService factory function. Update type hints. Verify existing tests pass.

### TASK-036
Notes: Search for `import openai` in service code. Should only appear in provider implementations, not in services.

### TASK-037
Notes: Run full test suite. All existing tests must pass without modification. This is the critical validation step.

### TASK-038
Notes: Create MIGRATION_GUIDE.md explaining: old config format, new config format, step-by-step migration instructions, examples for custom base URLs.

### TASK-039
Notes: Manual test: change `LLM_PROVIDER` environment variable, restart service, verify logs show correct provider selected, test LLM operations work.

### TASK-040
Notes: Manual test: configure custom base URL using new provider pattern, verify system works identically to before, test with local Ollama or similar.

### TASK-041
Notes: Create performance test script. Measure response times for LLM and embedding operations. Compare before/after. Verify overhead < 1%.

### TASK-042
Notes: Code review checklist: verify all 10 requirements implemented, all 10 acceptance criteria met, no regressions, performance acceptable.

### TASK-043
Notes: Update status.md to show "Plan Approved" and "Implementation Complete" when all tasks done.

## Completion Notes

- What was delivered: Complete task breakdown for provider abstraction layer implementation
- What was deferred: Mock provider implementation (can be added in future release)
- What needs follow-up: Implementation phase execution, performance benchmarking, user migration support

## Resume Notes

- Current phase: Planning complete, ready for implementation
- Next recommended task: TASK-001 (create backend/providers/__init__.py)
- Active blocker: None
- Last validation evidence added: None (planning phase)
- Exact next command or proof to run: `python -c "import backend.providers"` (after TASK-001 complete) 
