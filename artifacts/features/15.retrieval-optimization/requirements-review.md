# Requirements Review: Multi-Hop Reasoning Chain & Real Reranking

## Metadata

- **Feature name:** Multi-Hop Reasoning Chain & Real Reranking
- **Feature slug:** 15.retrieval-optimization
- **Related spec:** `spec.md`
- **Reviewer:** System Architect
- **Status:** Completed
- **Last updated:** 2026-05-19

---

## Review Summary

**Verdict:** ✅ **READY** (with minor non-blocking improvements noted)

**Short summary:**

The specification is comprehensive, well-scoped, and ready for planning. It clearly defines the problem, desired outcomes, user scenarios, and functional requirements with testable acceptance criteria. The scope is appropriately bounded (multi-hop reasoning + reranking only), and brownfield concerns are explicitly addressed. All requirements are traceable to user scenarios and success criteria. Three open questions are identified but marked non-blocking for MVP.

---

## Readiness Assessment

### Strengths

1. **Clear Problem Definition:** The spec articulates exactly what's broken (multi-hop queries treated as independent, dummy reranking) and why it matters (missed reasoning chains, suboptimal chunk ranking).

2. **Well-Scoped:** The feature is tightly scoped to multi-hop reasoning + reranking. Out-of-scope items (caching, collection auto-detection, UI) are explicitly listed, preventing scope creep.

3. **User-Centric:** Four user stories and four detailed scenarios ground the requirements in real use cases. Every requirement traces back to a scenario or outcome.

4. **Testable Acceptance Criteria:** All 10 success criteria are observable and measurable (manual tests, performance tests, API inspection, trace inspection).

5. **Brownfield Protection:** Current context section explicitly lists unchanged behavior (query classification, decomposition, RRF, parent-child, hybrid search, safety checks, tracing). Integration boundaries are clear.

6. **Comprehensive Requirements:** 18 functional requirements cover multi-hop reasoning, reranking, configuration, observability, and backward compatibility. Each requirement includes validation surface.

7. **Risk Awareness:** Five risks identified with mitigation strategies. Open questions marked non-blocking for MVP.

8. **Configuration-First:** Multi-hop and reranking are configurable per request, enabling gradual rollout and A/B testing.

### Main Concerns

1. **Intermediate Answer Quality:** Generating intermediate answers in 1-3 sentences (ASM-002) may lose critical context for complex queries. Mitigation: Make intermediate answer length configurable in follow-up.

2. **Latency Sensitivity:** 2-3x latency increase (SC-004) may be unacceptable for some use cases. Mitigation: Make multi-hop opt-in for latency-sensitive scenarios; enforce timeout.

3. **Model Selection Deferred:** Cross-encoder model and intermediate answer model are deferred to follow-up (OQ-001, OQ-002). Mitigation: Spec defaults to reasonable choices (ms-marco-MiniLM-L-6-v2, GPT-4o-mini); can be optimized later.

4. **Cohere API Deferred:** Cohere Rerank API support deferred to follow-up (OQ-003). Mitigation: MVP uses local cross-encoder; API support is straightforward to add.

5. **Cost Impact:** Additional LLM calls for intermediate answers increase API costs. Mitigation: Use fast/cheap model; monitor and optimize if needed.

**Assessment:** These concerns are manageable and do not block planning. They are either mitigated by design choices or deferred to follow-up releases.

---

## Traceability Check

| Item | Status | Notes |
|------|--------|-------|
| Requirements covered clearly | ✅ Yes | 18 functional requirements, each with clear statement and rationale |
| Acceptance criteria testable | ✅ Yes | All 10 success criteria are observable (tests, manual evaluation, metrics) |
| Validation method named per AC | ✅ Yes | Each SC includes validation surface (manual test, performance test, API inspection, trace inspection) |
| Plan-readiness traceability present | ✅ Yes | Requirements trace to user stories, scenarios, and success criteria |
| Scope boundaries explicit | ✅ Yes | In Scope, Out Of Scope, and Non-Goals sections clearly delineate boundaries |
| Non-goals explicit | ✅ Yes | Five non-goals listed (general reasoning engine, arbitrary depths, streaming, etc.) |
| Risks and open questions visible | ✅ Yes | Five risks with mitigations; three open questions marked non-blocking |

**Verdict:** ✅ All traceability checks pass. Spec is plan-ready.

---

## Blocking Issues

**None identified.** All concerns are either mitigated by design or deferred to follow-up releases without blocking MVP.

---

## Non-Blocking Improvements

### NI-001: Intermediate Answer Length Configuration

**Related spec section:** REQ-002 (Intermediate Answer Generation)

**Improvement:** Make intermediate answer length configurable (default: 1-3 sentences, range: 1-5 sentences) to balance context preservation with latency.

**Why it helps:** Some queries may need longer intermediate answers to preserve critical context. Configurability enables tuning per use case.

**Priority:** Low; can be added in follow-up release.

---

### NI-002: Reranking Model Benchmarking

**Related spec section:** OQ-002 (Cross-Encoder Model Selection)

**Improvement:** Before MVP launch, benchmark multiple cross-encoder models (ms-marco-MiniLM-L-6-v2, ms-marco-MiniLM-L-12-v2, etc.) to validate quality/latency tradeoff.

**Why it helps:** Ensures model choice is optimal for the system's use cases.

**Priority:** Medium; should be done before MVP launch.

---

### NI-003: Multi-Hop Query Classification Validation

**Related spec section:** REQ-001 (Sequential Sub-Question Execution)

**Improvement:** Validate that existing query classification accurately identifies multi-hop queries. If classification is inaccurate, multi-hop reasoning may be applied to wrong queries.

**Why it helps:** Ensures multi-hop logic is applied to the right queries.

**Priority:** Medium; should be validated before MVP launch.

---

### NI-004: Fallback Strategy Testing

**Related spec section:** REQ-005 (Failure Handling with Fallback)

**Improvement:** Comprehensive testing of fallback strategy with various failure scenarios (no chunks retrieved, all chunks below threshold, timeout, etc.).

**Why it helps:** Ensures graceful degradation works as expected.

**Priority:** Medium; should be included in test plan.

---

### NI-005: Cost Analysis

**Related spec section:** RISK-002 (Cost Increase)

**Improvement:** Estimate additional LLM API costs for intermediate answers. Compare cost/benefit of using cheaper model vs. quality impact.

**Why it helps:** Enables informed decision on model selection and cost optimization.

**Priority:** Low; can be done during implementation.

---

## Brownfield Observations

### Current Context Quality

✅ **Excellent.** The spec clearly identifies:
- Existing components that will be modified (AdvancedRetrievalService, RerankingService)
- Existing components that will be extended (RetrievalTrace, RerankingTrace)
- Existing components that remain unchanged (query classification, decomposition, RRF, parent-child, hybrid search, safety checks)

### Unchanged Behavior Captured

✅ **Complete.** Seven items explicitly listed as unchanged:
1. Query Classification
2. Query Decomposition
3. RRF Merging
4. Parent-Child Expansion
5. Hybrid Search
6. Safety Checks
7. Tracing Infrastructure

### Integration Boundaries Captured

✅ **Clear.** Integration points identified:
- `backend/chat/retrieval.py:278-496` - AdvancedRetrievalService (modified)
- `backend/chat/retrieval.py:250-276` - RerankingService (replaced)
- `backend/schemas/chat.py` - RetrievalTrace and RerankingTrace (extended)
- `backend/chat/service.py:43-237` - Chat orchestration (unchanged)

### Regression Concerns Visible

✅ **Addressed.** REQ-009 explicitly requires no regression for simple queries. SC-005 measures regression. Regression test suite mentioned in validation surface.

---

## Questions To Resolve

### Q1: Intermediate Answer Model Selection

**Question:** Which LLM model should be used for generating intermediate answers?

**Owner:** Implementation team (during planning phase)

**Why it matters:** Affects cost, latency, and quality of intermediate answers. Wrong choice could degrade performance or increase costs.

**Status:** Non-blocking for MVP. Spec defaults to GPT-4o-mini (fast, cheap). Can be optimized in follow-up.

**Resolution:** Use GPT-4o-mini for MVP; make configurable in follow-up.

---

### Q2: Cross-Encoder Model Selection

**Question:** Which cross-encoder model should be used for reranking?

**Owner:** Implementation team (during planning phase)

**Why it matters:** Affects latency vs. quality tradeoff. Larger models are slower but higher quality.

**Status:** Non-blocking for MVP. Spec defaults to ms-marco-MiniLM-L-6-v2 (fast, good quality). Can be optimized in follow-up.

**Resolution:** Use ms-marco-MiniLM-L-6-v2 for MVP; benchmark alternatives before launch.

---

### Q3: Cohere Rerank API Priority

**Question:** Should Cohere Rerank API support be included in MVP or deferred to follow-up?

**Owner:** Product team

**Why it matters:** Affects scope and timeline. Cohere API is optional but could provide better quality.

**Status:** Non-blocking for MVP. Spec defers to follow-up. MVP uses local cross-encoder only.

**Resolution:** Defer Cohere API to follow-up release. MVP uses local cross-encoder.

---

## Recommendation

### Next Step

✅ **PROCEED TO PLANNING PHASE**

The specification is comprehensive, well-scoped, and ready for the planning phase. All requirements are clear, testable, and traceable to user scenarios. Brownfield concerns are explicitly addressed. Open questions are non-blocking for MVP.

### Planning Phase Deliverables

1. **Architecture Design:** How will sequential iterative retrieval be implemented? How will intermediate answers be generated and stored?

2. **Task Breakdown:** Decompose 18 functional requirements into implementation tasks with dependencies and effort estimates.

3. **Integration Plan:** How will multi-hop reasoning and reranking integrate with existing retrieval pipeline?

4. **Testing Strategy:** Unit tests, integration tests, performance tests, manual evaluation plan.

5. **Rollout Plan:** How will features be rolled out? Gradual rollout? A/B testing?

### Success Criteria for Planning Phase

- [ ] Architecture design approved by team
- [ ] Task breakdown complete with effort estimates
- [ ] Testing strategy defined
- [ ] Rollout plan defined
- [ ] Timeline and resource allocation confirmed

---

## Sign-Off

**Specification Status:** ✅ **APPROVED FOR PLANNING**

**Reviewer:** System Architect  
**Date:** 2026-05-19  
**Confidence Level:** High (all traceability checks pass, scope is clear, requirements are testable)

---

**Next Action:** Proceed to `/aiddk-plan` to design implementation approach and break down tasks.
