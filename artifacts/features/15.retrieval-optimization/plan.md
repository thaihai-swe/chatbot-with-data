# Implementation Plan: Multi-Hop Reasoning Chain, Real Reranking & Collection Auto-Detection

## Metadata

- **Feature name:** Multi-Hop Reasoning Chain, Real Reranking & Collection Auto-Detection
- **Feature slug:** 15.retrieval-optimization
- **Related spec:** `spec.md`
- **Related design:** `design.md`
- **Owner:** System Architect
- **Status:** Draft
- **Last updated:** 2026-05-20

---

## Plan Summary

This plan executes three retrieval enhancements in a phased, risk-reducing sequence:

1. **Phase 1 (Days 1-2):** Real Reranking - Replace dummy implementation with cross-encoder model
2. **Phase 2 (Days 3-4):** Collection Auto-Detection - Add LLM-based collection routing
3. **Phase 3 (Days 5-7):** Multi-Hop Reasoning - Implement sequential iterative retrieval

**Rationale for Sequencing:**
- Reranking is lowest risk (isolated service, no state management)
- Collection routing is medium risk (new LLM calls, but independent)
- Multi-hop is highest risk (new execution path, state management, latency)
- Each phase can be feature-flagged independently for safe rollout

**Total Effort:** 7-10 days (including testing and validation)

---

## Execution Context

**Design Reference:** See `design.md` for:
- Separate MultiHopRetrievalOrchestrator (not modifying existing parallel path)
- Backward-compatible schema extension strategy
- Comprehensive error handling with fallback at each stage
- Configuration flag hierarchy

**Repository Patterns:**
- Service-based architecture (QueryIntelligenceService, RetrievalService, etc.)
- Pydantic schemas for type safety
- Comprehensive tracing infrastructure
- Feature flags via AdvancedRetrievalConfig

**Brownfield Constraints:**
- Cannot modify existing parallel decomposition logic (risk of regression)
- Must preserve RetrievalTrace schema compatibility
- Must maintain existing error handling patterns
- Must not break existing API contracts

**Unchanged Behavior to Preserve:**
- Query classification (5-category system)
- Query decomposition logic
- RRF merging for parallel queries
- Parent-child retrieval
- Hybrid search with configurable alpha
- Safety checks and injection detection

---

## First Delivery Slice

**Smallest Useful Slice:** Phase 1 (Real Reranking)

**Why This Slice Goes First:**
- Lowest risk (isolated service, no state management)
- Immediate quality improvement (20%+ relevance boost)
- Can be deployed independently
- Validates cross-encoder model loading and inference patterns
- Unblocks Phase 2 and 3 (they depend on reranking infrastructure)

**What Proof Should Exist When Done:**
- Cross-encoder model loads successfully on first request
- Reranking improves top-5 chunk relevance by >20% (manual evaluation)
- Reranking adds <200ms latency (performance test)
- Fallback to dummy behavior works when model unavailable
- No regression in existing queries (regression test suite passes)

---

## Technical Approach

### Architecture Overview

**Phase 1: Real Reranking**
- Replace `RerankingService` dummy with real cross-encoder
- Lazy load model on first use
- Implement fallback to dummy behavior on failure
- Extend `RerankingTrace` with pre/post-rerank ordering

**Phase 2: Collection Auto-Detection**
- Create new `CollectionRoutingService`
- Implement LLM-based routing with confidence scoring
- Add confidence-based fallback to all collections
- Integrate with ChatService before retrieval

**Phase 3: Multi-Hop Reasoning**
- Create new `MultiHopRetrievalOrchestrator`
- Implement sequential sub-question execution
- Generate intermediate answers between hops
- Extend `RetrievalTrace` with `reasoning_chain` field
- Update dynamic routing to enable multi-hop for classified queries

### Key Interfaces

**RealRerankingService:**
```python
def rerank(query: str, candidates: List[Candidate]) -> List[Candidate]
```

**CollectionRoutingService:**
```python
def route_query(
    query: str,
    session_collection_ids: List[str],
    threshold: float
) -> Tuple[List[str], CollectionRoutingTrace]
```

**MultiHopRetrievalOrchestrator:**
```python
def execute_multi_hop(
    query: str,
    sub_questions: List[str],
    config: AdvancedRetrievalConfig,
    collection_ids: List[str]
) -> Tuple[List[Candidate], ReasoningChain]
```

### Operational Considerations

- **Model Loading:** Cross-encoder model (~300MB) lazy-loaded on first request
- **LLM Calls:** Intermediate answers and routing use fast/cheap model (GPT-4o-mini)
- **Timeouts:** Multi-hop queries have 30s timeout, individual hops have 10s timeout
- **Monitoring:** Log all LLM calls, model loads, and fallback events
- **Feature Flags:** All features opt-in via configuration

---

## Requirements And Constraints

### Phase 1: Real Reranking

**REQ-010:** Cross-Encoder Reranking
- Implementation note: Lazy load `cross-encoder/ms-marco-MiniLM-L-6-v2` on first use
- Planned validation: Unit test for model loading and inference
- Linked scenario: Scenario 4 (Reranking Improves Relevance)

**REQ-011:** Reranking Score Normalization
- Implementation note: Min-max normalization to [0, 1] range
- Planned validation: Unit test for normalized scores in [0, 1]
- Linked scenario: Scenario 4

**REQ-012:** Reranking Threshold Filtering
- Implementation note: Filter candidates below threshold (default: 0.3)
- Planned validation: Unit test for threshold filtering
- Linked scenario: Scenario 4

**REQ-013:** Reranking Latency Constraint
- Implementation note: Measure latency for 50 candidates, target <200ms
- Planned validation: Performance test
- Linked scenario: Scenario 4

**REQ-014:** Reranking Top-N Configuration
- Implementation note: Configurable via `rerank_top_n` (default: 50)
- Planned validation: Unit test for top-N selection
- Linked scenario: Scenario 4

**REQ-015:** Reranking Trace
- Implementation note: Extend `RerankingTrace` with pre/post-rerank ordering
- Planned validation: Trace inspection test
- Linked scenario: Scenario 4

**REQ-017:** Reranking Configuration
- Implementation note: Add `enable_reranking` flag (default: True)
- Planned validation: Unit test for flag behavior
- Linked scenario: Scenario 4

### Phase 2: Collection Auto-Detection

**REQ-019:** Collection Auto-Detection
- Implementation note: LLM-based routing when session has no collections
- Planned validation: Manual evaluation of routing accuracy (>80%)
- Linked scenario: Scenario 5 (Collection Auto-Detection Happy Path)

**REQ-020:** Collection Routing Confidence Scoring
- Implementation note: Confidence score with threshold (default: 0.7)
- Planned validation: Manual test for fallback behavior
- Linked scenario: Scenario 6 (Collection Auto-Detection Low Confidence Fallback)

**REQ-021:** Collection Routing Trace
- Implementation note: Extend trace with routing decisions and reasoning
- Planned validation: Trace inspection test
- Linked scenario: Scenario 5, 6

**REQ-022:** Collection Routing Configuration
- Implementation note: Add `enable_collection_routing` flag (default: False)
- Planned validation: Unit test for flag behavior
- Linked scenario: Scenario 5, 6

**REQ-023:** Collection Routing Latency Constraint
- Implementation note: Measure routing latency, target <500ms
- Planned validation: Performance test
- Linked scenario: Scenario 5, 6

**REQ-024:** Collection Descriptions for Routing
- Implementation note: Retrieve collection metadata from database
- Planned validation: Unit test for metadata retrieval
- Linked scenario: Scenario 5, 6

### Phase 3: Multi-Hop Reasoning

**REQ-001:** Sequential Sub-Question Execution
- Implementation note: Execute sub-questions sequentially in MultiHopRetrievalOrchestrator
- Planned validation: Manual test with multi-hop query
- Linked scenario: Scenario 1 (Multi-Hop Query Happy Path)

**REQ-002:** Intermediate Answer Generation
- Implementation note: Generate concise intermediate answer after each hop
- Planned validation: Manual test for intermediate answer quality
- Linked scenario: Scenario 1

**REQ-003:** Reasoning Chain Tracking
- Implementation note: Track sub-questions, chunks, intermediate answers, timing
- Planned validation: Trace inspection test
- Linked scenario: Scenario 1

**REQ-004:** Reasoning Chain API Exposure
- Implementation note: Add `reasoning_chain` field to API response
- Planned validation: API response inspection test
- Linked scenario: Scenario 1

**REQ-005:** Failure Handling with Fallback
- Implementation note: Fall back to original query + remaining sub-questions on failure
- Planned validation: Manual test with failing intermediate retrieval
- Linked scenario: Scenario 2 (Intermediate Failure Fallback)

**REQ-006:** Multi-Hop Latency Constraint
- Implementation note: Enforce 2-3x baseline latency (e.g., 3-6s for 2s baseline)
- Planned validation: Performance test
- Linked scenario: Scenario 1

**REQ-007:** Max Hops Limit
- Implementation note: Enforce max hops (default: 3)
- Planned validation: Unit test for max hops enforcement
- Linked scenario: Scenario 1

**REQ-008:** Multi-Hop Timeout
- Implementation note: Enforce timeout (default: 30s)
- Planned validation: Unit test for timeout behavior
- Linked scenario: Scenario 1

**REQ-009:** No Regression for Simple Queries
- Implementation note: Simple queries skip multi-hop logic
- Planned validation: Regression test suite
- Linked scenario: Scenario 3 (Simple Query No Multi-Hop)

**REQ-016:** Multi-Hop Configuration
- Implementation note: Add `enable_multi_hop` flag (default: False)
- Planned validation: Unit test for flag behavior
- Linked scenario: Scenario 1

### Non-Functional Requirements

**NFR-001: Backward Compatibility**
- Implementation note: All new fields optional in schemas
- Planned validation: Existing API tests pass without modification

**NFR-002: Error Handling**
- Implementation note: Comprehensive try/except with fallback at each stage
- Planned validation: Error scenario tests

**NFR-003: Observability**
- Implementation note: Log all LLM calls, model loads, fallback events
- Planned validation: Log inspection tests

---

## Impacted Areas

**Services or Modules:**
- `backend/chat/retrieval.py` - AdvancedRetrievalService (add multi-hop routing)
- `backend/chat/service.py` - ChatService (add collection routing integration)
- `backend/schemas/chat.py` - Trace schemas (extend with new fields)
- `backend/providers/openai.py` - LLM provider (used for intermediate answers, routing)

**APIs or Interfaces:**
- Chat API response schema (add `reasoning_chain` and `collection_routing` fields)
- AdvancedRetrievalConfig (add new configuration flags)
- RetrievalTrace schema (extend with new fields)

**Data Model or Storage:**
- No database schema changes required (new fields are optional)
- Optional: Add `retrieval_trace_json` column for persistence (deferred)

**UI or UX:**
- API contract only (UI implementation deferred)
- Frontend can display `reasoning_chain` in expandable section

**Infrastructure or Deployment:**
- Cross-encoder model (~300MB) needs to be available at runtime
- No additional infrastructure required

**Documentation:**
- Update API documentation with new response fields
- Document configuration flags and precedence rules
- Add troubleshooting guide for model loading failures

---

## Protected Behavior

**Behavior that must not regress:**

1. **Query Classification:** 5-category classification (simple/multi_hop/comparative/conversational/out_of_domain) must remain unchanged
   - Protection approach: No changes to QueryIntelligenceService.classify_query()

2. **Query Decomposition:** Existing decomposition logic must remain unchanged
   - Protection approach: No changes to QueryIntelligenceService.decompose_query()

3. **Parallel Decomposition:** Existing parallel multi-query execution must remain unchanged
   - Protection approach: Create new MultiHopRetrievalOrchestrator, don't modify existing path

4. **RRF Merging:** Reciprocal Rank Fusion with k=60 must remain unchanged
   - Protection approach: No changes to CandidateMerger

5. **Parent-Child Retrieval:** Existing parent-child expansion must remain unchanged
   - Protection approach: No changes to parent-child logic

6. **Hybrid Search:** Alpha parameter configuration must remain unchanged
   - Protection approach: No changes to hybrid search logic

7. **Safety Checks:** Query injection detection and chunk safety filtering must remain unchanged
   - Protection approach: No changes to safety check logic

**Regression Test Suite:**
- Run existing test suite for all retrieval scenarios
- Verify simple queries maintain baseline latency
- Verify parallel decomposition still works
- Verify RRF merging still works

---

## Affected Files

**Phase 1: Real Reranking**

- `backend/chat/retrieval.py` - Replace RerankingService dummy with real implementation
- `backend/schemas/chat.py` - Extend RerankingTrace with rerank_scores field
- `backend/chat/service.py` - No changes (reranking called from retrieval service)

**Phase 2: Collection Auto-Detection**

- `backend/chat/collection_routing.py` - NEW service for collection routing
- `backend/chat/service.py` - Add collection routing integration before retrieval
- `backend/schemas/chat.py` - Add CollectionRoutingTrace schema

**Phase 3: Multi-Hop Reasoning**

- `backend/chat/multi_hop_orchestrator.py` - NEW service for sequential multi-hop
- `backend/chat/retrieval.py` - Add multi-hop routing logic
- `backend/schemas/chat.py` - Add ReasoningChain and ReasoningHop schemas
- `backend/chat/service.py` - No changes (multi-hop called from retrieval service)

---

## Dependencies

**DEP-001: Cross-Encoder Model**
- Dependency: Hugging Face `sentence-transformers` library
- Why it matters: Required for real reranking
- Mitigation: Lazy load on first use, fallback to dummy if unavailable

**DEP-002: LLM Provider for Intermediate Answers**
- Dependency: Existing LLM provider (OpenAI, Anthropic, etc.)
- Why it matters: Required for generating intermediate answers in multi-hop
- Mitigation: Use fast/cheap model (GPT-4o-mini), comprehensive error handling

**DEP-003: LLM Provider for Collection Routing**
- Dependency: Existing LLM provider
- Why it matters: Required for LLM-based collection routing
- Mitigation: Use fast/cheap model, confidence-based fallback

**DEP-004: Existing Retrieval Infrastructure**
- Dependency: Weaviate, embedding provider, chunk repository
- Why it matters: Multi-hop and collection routing depend on existing retrieval
- Mitigation: No changes to existing infrastructure

**DEP-005: Tracing Infrastructure**
- Dependency: Existing RetrievalTrace and RerankingTrace schemas
- Why it matters: New features extend tracing
- Mitigation: Backward-compatible optional fields

---

## Implementation Prerequisites

**PREREQ-001:** Design approved and documented
- Status: ✅ Complete (design.md created)

**PREREQ-002:** Red-team analysis completed
- Status: ✅ Complete (identified critical risks and mitigations)

**PREREQ-003:** Test environment setup
- Status: Required before Phase 1
- Action: Set up test database, mock LLM provider, performance testing tools

**PREREQ-004:** Cross-encoder model availability
- Status: Required before Phase 1
- Action: Verify model can be downloaded and loaded in test environment

**PREREQ-005:** Feature flag infrastructure
- Status: ✅ Exists (AdvancedRetrievalConfig already supports flags)

---

## Execution Phases

### Phase 1: Real Reranking (Days 1-2)

**Goal:** Replace dummy reranking with real cross-encoder model, improving chunk relevance by 20%+

**Enabled User Scenario(s):**
- Scenario 4: Reranking Improves Relevance

**Entry Proof:**
- Design approved
- Test environment ready
- Cross-encoder model can be downloaded

**Exit Proof:**
- Cross-encoder model loads successfully
- Reranking improves top-5 chunk relevance by >20% (manual evaluation)
- Reranking adds <200ms latency (performance test)
- Fallback to dummy behavior works
- No regression in existing queries

**Completion Criteria:**

- **CC-001:** RealRerankingService implemented with lazy loading
- **CC-002:** Score normalization to [0, 1] range implemented
- **CC-003:** Threshold filtering implemented (default: 0.3)
- **CC-004:** RerankingTrace extended with pre/post-rerank ordering
- **CC-005:** Error handling with fallback to dummy behavior
- **CC-006:** Unit tests for model loading, inference, fallback
- **CC-007:** Performance tests for reranking latency
- **CC-008:** Manual evaluation of reranking quality (10 test queries)
- **CC-009:** Regression test suite passes

### Phase 2: Collection Auto-Detection (Days 3-4)

**Goal:** Automatically route queries to relevant collections, improving performance and relevance

**Enabled User Scenario(s):**
- Scenario 5: Collection Auto-Detection (Happy Path)
- Scenario 6: Collection Auto-Detection (Low Confidence Fallback)

**Entry Proof:**
- Phase 1 complete and tested
- Collection metadata available in database

**Exit Proof:**
- Collection routing correctly identifies relevant collections (>80% accuracy)
- Confidence-based fallback works for ambiguous queries
- Routing adds <500ms latency
- No regression in existing queries

**Completion Criteria:**

- **CC-010:** CollectionRoutingService implemented with LLM-based routing
- **CC-011:** Confidence scoring with threshold (default: 0.7)
- **CC-012:** Confidence-based fallback to all collections
- **CC-013:** CollectionRoutingTrace schema added
- **CC-014:** Integration with ChatService before retrieval
- **CC-015:** Error handling with fallback to all collections
- **CC-016:** Unit tests for routing logic, confidence scoring, fallback
- **CC-017:** Manual evaluation of routing accuracy (20 test queries)
- **CC-018:** Performance tests for routing latency
- **CC-019:** Regression test suite passes

### Phase 3: Multi-Hop Reasoning (Days 5-7)

**Goal:** Enable sequential iterative retrieval for complex multi-hop queries

**Enabled User Scenario(s):**
- Scenario 1: Multi-Hop Query (Happy Path)
- Scenario 2: Intermediate Failure (Fallback)
- Scenario 3: Simple Query (No Multi-Hop)

**Entry Proof:**
- Phase 1 and 2 complete and tested
- Design approved for multi-hop orchestrator

**Exit Proof:**
- Sequential sub-question execution works correctly
- Reasoning chain is exposed in API response
- Failure handling with fallback works
- Multi-hop queries complete within 2-3x baseline latency
- No regression in simple queries

**Completion Criteria:**

- **CC-020:** MultiHopRetrievalOrchestrator implemented with sequential execution
- **CC-021:** Intermediate answer generation implemented
- **CC-022:** Reasoning chain tracking implemented
- **CC-023:** ReasoningChain and ReasoningHop schemas added
- **CC-024:** Failure handling with fallback to original query
- **CC-025:** Max hops limit (default: 3) enforced
- **CC-026:** Timeout (default: 30s) enforced
- **CC-027:** Dynamic routing updated to enable multi-hop for classified queries
- **CC-028:** Unit tests for sequential execution, intermediate answers, fallback
- **CC-029:** Integration tests for end-to-end multi-hop flow
- **CC-030:** Performance tests for multi-hop latency
- **CC-031:** Manual evaluation of multi-hop quality (10 test queries)
- **CC-032:** Regression test suite passes (simple queries unaffected)

---

## Validation Strategy

**TEST-001: Unit Tests**
- RealRerankingService: model loading, inference, fallback, score normalization
- CollectionRoutingService: LLM routing, confidence scoring, fallback
- MultiHopRetrievalOrchestrator: sequential execution, intermediate answers, fallback
- Configuration flags: enable/disable behavior

**TEST-002: Integration Tests**
- Reranking in full retrieval pipeline
- Collection routing + retrieval flow
- Multi-hop + reranking + collection routing together
- Error scenarios (LLM failures, model load failures, etc.)

**TEST-003: End-to-End Tests**
- Chat API with multi-hop queries
- Chat API with collection routing
- Chat API with reranking
- Streaming responses with new trace fields

**TEST-004: Manual Verification**
- Reranking quality: Compare top-5 chunks before/after for 10 queries
- Collection routing accuracy: Test 20 queries with known correct collections
- Multi-hop quality: Test 10 complex multi-hop queries
- Fallback behavior: Verify graceful degradation on failures

**TEST-005: Observability Checks**
- Log all LLM calls (intermediate answers, routing)
- Log model loads and failures
- Log fallback events
- Verify trace fields are populated correctly

**TEST-006: Performance Tests**
- Reranking latency: <200ms for 50 candidates
- Collection routing latency: <500ms
- Multi-hop latency: <3s for 3 hops (2-3x baseline)
- No regression in simple query latency

**TEST-007: Regression Tests**
- Existing test suite passes without modification
- Simple queries maintain baseline latency
- Parallel decomposition still works
- RRF merging still works

---

## Traceability Matrix

| Scenario | Plan Phase | Tasks |
|----------|-----------|-------|
| Scenario 1: Multi-Hop Query (Happy Path) | Phase 3 | T-3.1 through T-3.8 |
| Scenario 2: Intermediate Failure (Fallback) | Phase 3 | T-3.5, T-3.6, T-3.9 |
| Scenario 3: Simple Query (No Multi-Hop) | Phase 3 | T-3.10 |
| Scenario 4: Reranking Improves Relevance | Phase 1 | T-1.1 through T-1.7 |
| Scenario 5: Collection Auto-Detection (Happy Path) | Phase 2 | T-2.1 through T-2.7 |
| Scenario 6: Collection Auto-Detection (Low Confidence) | Phase 2 | T-2.5, T-2.8 |

| Requirement | Plan Phase | Tasks |
|-------------|-----------|-------|
| REQ-001 through REQ-009 | Phase 3 | T-3.1 through T-3.10 |
| REQ-010 through REQ-018 | Phase 1 | T-1.1 through T-1.7 |
| REQ-019 through REQ-024 | Phase 2 | T-2.1 through T-2.8 |
| REQ-025 | All Phases | Backward compatibility maintained throughout |

| Success Criteria | Validation Step |
|------------------|-----------------|
| SC-001 through SC-005 | Phase 3 tests (T-3.9, T-3.10) |
| SC-006 through SC-010 | Phase 1 tests (T-1.6, T-1.7) |
| SC-011 through SC-014 | Phase 2 tests (T-2.7, T-2.8) |

---

## Rollout Plan

**Release Approach:** Phased rollout with feature flags

**Phase 1 Rollout:**
- Deploy RealRerankingService with `enable_reranking=True` (default)
- Fallback to dummy behavior if model unavailable
- Monitor reranking latency and quality metrics

**Phase 2 Rollout:**
- Deploy CollectionRoutingService with `enable_collection_routing=False` (default)
- Enable for subset of users (10% → 50% → 100%)
- Monitor routing accuracy and latency

**Phase 3 Rollout:**
- Deploy MultiHopRetrievalOrchestrator with `enable_multi_hop=False` (default)
- Enable for multi_hop classified queries only
- Monitor multi-hop latency and quality

**Feature Flags:**
- `enable_reranking`: True (default) - can be disabled if issues arise
- `enable_collection_routing`: False (default) - opt-in
- `enable_multi_hop`: False (default) - opt-in

**Migration Needs:** None (backward compatible)

**Backward Compatibility Notes:**
- All new trace fields are optional
- Existing API consumers ignore unknown fields
- No database schema changes required
- Existing queries unaffected

---

## Rollback Plan

**Immediate Rollback (Minutes):**
- Set `enable_reranking=False` → Revert to dummy reranking
- Set `enable_collection_routing=False` → Disable collection routing
- Set `enable_multi_hop=False` → Disable multi-hop reasoning

**Partial Rollback (Hours):**
- Disable specific component (e.g., multi-hop only)
- Keep other components enabled

**Full Rollback (Hours):**
- Revert code changes
- New services are isolated and easy to remove
- No database migrations to revert

**Rollback Triggers:**
- Latency increase >50% for any query type
- Error rate increase >1%
- Model load failures affecting >10% of requests
- Routing accuracy <70%

---

## Risks And Mitigations

**RISK-001: Sequential Execution Breaks Parallel Assumptions**
- Mitigation: Create separate MultiHopRetrievalOrchestrator, don't modify existing path

**RISK-002: Schema Extension Breaks Serialization**
- Mitigation: Use optional fields with None defaults, add trace_version field

**RISK-003: LLM Failure Cascade**
- Mitigation: Comprehensive try/except with fallback at each stage

**RISK-004: Latency Explosion from Sequential Execution**
- Mitigation: Add max_hops limit (3), timeout (30s), make multi-hop opt-in

**RISK-005: Configuration Flag Conflicts**
- Mitigation: Clear flag hierarchy and precedence rules

**RISK-006: Reranking Model Load Failure**
- Mitigation: Lazy load with fallback to dummy behavior

**RISK-007: Collection Routing Accuracy**
- Mitigation: Confidence-based fallback to all collections

**RISK-008: Performance Regression**
- Mitigation: Comprehensive performance tests, monitoring, rollback plan

---

## Open Questions

**Q-001:** Should intermediate answers be cached?
- **Next step:** Defer to post-MVP optimization, add TODO

**Q-002:** Should multi-hop be automatic or opt-in?
- **Next step:** Automatic for classified queries, can be overridden

**Q-003:** Should collection routing use embedding similarity as fallback?
- **Next step:** Defer to post-MVP, current fallback (all collections) is safe

---

**Status:** Ready for tasking phase

