# Design Document: Multi-Hop Reasoning Chain, Real Reranking & Collection Auto-Detection

## Metadata

- **Feature name:** Multi-Hop Reasoning Chain, Real Reranking & Collection Auto-Detection
- **Feature slug:** 15.retrieval-optimization
- **Related spec:** `spec.md`
- **Related requirements review:** `requirements-review.md`
- **Owner:** System Architect
- **Status:** Draft
- **Last updated:** 2026-05-20

---

## Design Summary

This feature adds three components to the retrieval pipeline:
1. **Sequential multi-hop reasoning** - Execute sub-questions iteratively with intermediate answers
2. **Real cross-encoder reranking** - Replace dummy reranking with actual relevance scoring
3. **LLM-based collection routing** - Automatically route queries to relevant collections

**Critical Design Decision:** Multi-hop reasoning requires a **separate execution path** from existing parallel decomposition to avoid breaking current functionality. The red-team analysis revealed that modifying the existing parallel path would break RRF merging and introduce state management issues.

---

## Red-Team Analysis Summary

The stress-test identified **3 critical risks** that inform this design:

1. **Sequential execution breaks parallel assumptions** - Current code assumes all sub-questions execute in parallel for RRF merging
2. **Schema extension could break serialization** - Frontend/API consumers expect fixed schema structure
3. **LLM failure cascade with no retry logic** - Multiple new LLM calls (intermediate answers, routing) have no error handling

**Design Approach:** Implement multi-hop as a **new execution mode** with comprehensive fallback behavior, not as a modification to existing decomposition logic.

---

## Architecture Overview

### Current Architecture (Preserved)

```
Query → QueryIntelligenceService (classify, decompose, expand)
     → AdvancedRetrievalService (parallel multi-query execution)
     → RRF Merging
     → RerankingService (dummy sort)
     → Return chunks
```

### New Architecture (Multi-Hop Mode)

```
Query → QueryIntelligenceService (classify, decompose)
     → MultiHopRetrievalOrchestrator (NEW)
        ├─ Execute sub-question 1
        ├─ Generate intermediate answer 1
        ├─ Execute sub-question 2 (with context from answer 1)
        ├─ Generate intermediate answer 2
        └─ Execute sub-question N
     → Merge all hop results
     → RealRerankingService (NEW - cross-encoder)
     → Return chunks + reasoning_chain
```

### Collection Routing Integration

```
ChatService.process_turn
  ↓
CollectionRoutingService.route_query (NEW)
  ├─ If session.collection_ids empty → LLM routing
  ├─ If confidence < threshold → fallback to all collections
  └─ Return routed collection_ids
  ↓
AdvancedRetrievalService.retrieve (with routed collections)
```

---

## Key Design Decisions

### Decision 1: Separate Multi-Hop Execution Path

**Problem:** Current code executes all sub-questions in parallel and merges with RRF. Sequential execution breaks this assumption.

**Options Considered:**
- **Option A:** Modify existing AdvancedRetrievalService to support both parallel and sequential
- **Option B:** Create new MultiHopRetrievalOrchestrator for sequential execution
- **Option C:** Add sequential mode as a flag in existing service

**Chosen:** **Option B - New MultiHopRetrievalOrchestrator**

**Rationale:**
- Preserves existing parallel decomposition behavior (no regression risk)
- Clear separation of concerns (parallel vs sequential)
- Easier to test and debug in isolation
- Can be feature-flagged independently

**Implementation:**
```python
class MultiHopRetrievalOrchestrator:
    def __init__(self, retrieval_service, llm_provider):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
    
    def execute_multi_hop(
        self,
        query: str,
        sub_questions: List[str],
        config: AdvancedRetrievalConfig,
        collection_ids: List[str]
    ) -> Tuple[List[Candidate], ReasoningChain]:
        reasoning_chain = ReasoningChain(hops=[])
        all_candidates = []
        
        for i, sub_q in enumerate(sub_questions[:config.max_hops]):
            # Execute retrieval for this hop
            candidates, trace = self.retrieval_service.retrieve(
                query_text=sub_q,
                config=config,
                collection_ids=collection_ids
            )
            
            # Generate intermediate answer
            intermediate_answer = self._generate_intermediate_answer(
                sub_question=sub_q,
                candidates=candidates
            )
            
            # Record hop
            reasoning_chain.hops.append(ReasoningHop(
                hop_number=i+1,
                sub_question=sub_q,
                retrieved_chunk_ids=[c.chunk_id for c in candidates],
                intermediate_answer=intermediate_answer,
                latency_ms=trace.total_latency_ms
            ))
            
            all_candidates.extend(candidates)
            
            # Inject intermediate answer into next sub-question
            if i < len(sub_questions) - 1:
                sub_questions[i+1] = self._contextualize_sub_question(
                    sub_questions[i+1],
                    intermediate_answer
                )
        
        return all_candidates, reasoning_chain
```

---

### Decision 2: Configuration Flag Hierarchy

**Problem:** `enable_decomposition` currently triggers parallel execution. Adding `enable_multi_hop` creates ambiguity.

**Chosen:** **Explicit flag hierarchy with precedence rules**

**Configuration Schema:**
```python
class AdvancedRetrievalConfig:
    # Existing flags (unchanged)
    enable_expansion: bool = True
    enable_rewriting: bool = True
    enable_decomposition: bool = True  # Parallel decomposition
    enable_hyde: bool = False
    enable_synonyms: bool = False
    enable_parent_child: bool = True
    
    # New flags
    enable_multi_hop: bool = False  # Sequential multi-hop (opt-in)
    max_hops: int = 3
    multi_hop_timeout_ms: int = 30000
    
    enable_reranking: bool = True
    rerank_top_n: int = 50
    rerank_threshold: float = 0.3
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    enable_collection_routing: bool = False  # Opt-in
    collection_routing_threshold: float = 0.7
    collection_routing_max_collections: int = 3
```

**Precedence Rules:**
1. If `enable_multi_hop=True` → Use MultiHopRetrievalOrchestrator (sequential)
2. Else if `enable_decomposition=True` → Use existing parallel decomposition
3. Else → Use baseline retrieval

**Dynamic Routing Update:**
```python
# retrieval.py:310-314 (UPDATED)
elif trace.classification == "multi_hop":
    config.enable_multi_hop = True  # Changed from enable_decomposition
    config.enable_decomposition = False  # Disable parallel
    config.enable_expansion = False
    trace.routing.selected_strategy = "multi_hop_reasoning"
```

---

### Decision 3: Schema Extension Strategy

**Problem:** Adding `reasoning_chain` and `collection_routing` to `RetrievalTrace` could break existing consumers.

**Chosen:** **Backward-compatible optional fields with versioning**

**Implementation:**
```python
# schemas/chat.py (UPDATED)
class ReasoningHop(BaseModel):
    hop_number: int
    sub_question: str
    retrieved_chunk_ids: List[str]
    intermediate_answer: str
    latency_ms: float
    failure: Optional[str] = None

class ReasoningChain(BaseModel):
    hops: List[ReasoningHop]
    total_hops: int
    fallback_triggered: bool = False
    fallback_reason: Optional[str] = None
    total_latency_ms: float

class CollectionRoutingTrace(BaseModel):
    detected_collections: Optional[List[str]] = None
    confidence_scores: Dict[str, float] = {}
    reasoning: str = ""
    fallback_triggered: bool = False
    routing_latency_ms: float = 0.0
    available_collections: List[Dict[str, str]] = []

class RetrievalTrace(BaseModel):
    # Existing fields (unchanged)
    classification: str
    routing: RoutingDecision
    transformations: QueryTransformations
    execution_time_ms: Dict[str, int]
    total_latency_ms: float
    
    # New optional fields (backward compatible)
    reasoning_chain: Optional[ReasoningChain] = None
    collection_routing: Optional[CollectionRoutingTrace] = None
    trace_version: str = "2.0"  # Version indicator
```

**Backward Compatibility:**
- All new fields use `Optional` with `None` default
- Existing consumers ignore unknown fields (Pydantic behavior)
- `trace_version` allows consumers to detect new schema

---

### Decision 4: Error Handling & Fallback Strategy

**Problem:** Multiple new LLM calls (intermediate answers, collection routing) have no error handling. Failures could cascade.

**Chosen:** **Comprehensive try/except with graceful fallback at each stage**

**Fallback Hierarchy:**

| Component | Failure Scenario | Fallback Behavior |
|-----------|------------------|-------------------|
| **Collection Routing** | LLM call fails | Use session.collection_ids or all collections |
| **Collection Routing** | Confidence < threshold | Fall back to all collections |
| **Multi-Hop** | Intermediate LLM call fails | Use retrieved chunks as context (no intermediate answer) |
| **Multi-Hop** | Intermediate retrieval returns 0 chunks | Fall back to original query + remaining sub-questions |
| **Multi-Hop** | All sub-questions fail | Fall back to baseline retrieval with original query |
| **Reranking** | Model load fails | Fall back to similarity score sorting (dummy behavior) |
| **Reranking** | Inference fails | Fall back to similarity score sorting |

**Implementation Pattern:**
```python
def _generate_intermediate_answer(self, sub_question: str, candidates: List[Candidate]) -> str:
    try:
        # Attempt LLM call
        answer = self.llm_provider.generate_completion(...)
        return answer
    except Exception as e:
        logger.warning(f"Intermediate answer generation failed: {e}")
        # Fallback: use chunk text as context
        if candidates:
            return " ".join([c.text[:100] for c in candidates[:3]])
        return ""  # Empty context if no candidates
```

---

### Decision 5: Reranking Service Architecture

**Problem:** Current RerankingService is dummy. Real cross-encoder requires model loading, which could fail.

**Chosen:** **Lazy loading with fallback to dummy behavior**

**Implementation:**
```python
class RealRerankingService:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None  # Lazy load
        self._model_load_failed = False
    
    def _load_model(self):
        if self._model is not None or self._model_load_failed:
            return
        
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            logger.info(f"Loaded reranking model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load reranking model: {e}")
            self._model_load_failed = True
    
    def rerank(self, query: str, candidates: List[Candidate]) -> List[Candidate]:
        self._load_model()
        
        if self._model is None:
            # Fallback to dummy behavior
            logger.warning("Reranking model unavailable, using similarity scores")
            return sorted(candidates, key=lambda c: c.score, reverse=True)
        
        try:
            # Real reranking
            pairs = [(query, c.text) for c in candidates]
            scores = self._model.predict(pairs)
            
            # Normalize scores to [0, 1]
            min_score, max_score = min(scores), max(scores)
            normalized_scores = [(s - min_score) / (max_score - min_score) if max_score > min_score else 0.5 for s in scores]
            
            # Update candidate scores and sort
            for i, candidate in enumerate(candidates):
                candidate.rerank_score = normalized_scores[i]
            
            return sorted(candidates, key=lambda c: c.rerank_score, reverse=True)
        
        except Exception as e:
            logger.error(f"Reranking inference failed: {e}")
            # Fallback to dummy behavior
            return sorted(candidates, key=lambda c: c.score, reverse=True)
```

---

### Decision 6: Collection Routing Service Architecture

**Problem:** LLM-based routing could fail or return low-confidence results.

**Chosen:** **Confidence-based routing with fallback to all collections**

**Implementation:**
```python
class CollectionRoutingService:
    def __init__(self, llm_provider, collection_repository):
        self.llm_provider = llm_provider
        self.collection_repository = collection_repository
    
    def route_query(
        self,
        query: str,
        session_collection_ids: List[str],
        threshold: float = 0.7
    ) -> Tuple[List[str], CollectionRoutingTrace]:
        trace = CollectionRoutingTrace()
        
        # If session has explicit collections, use them (no routing)
        if session_collection_ids:
            trace.detected_collections = session_collection_ids
            trace.reasoning = "Using session-specified collections"
            return session_collection_ids, trace
        
        # Fetch available collections
        collections = self.collection_repository.get_all()
        trace.available_collections = [
            {"id": c.id, "name": c.name, "description": c.description or ""}
            for c in collections
        ]
        
        try:
            # LLM-based routing
            prompt = self._build_routing_prompt(query, collections)
            response = self.llm_provider.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            # Parse response (expected format: JSON with collections and confidence)
            routing_result = json.loads(response)
            detected_collections = routing_result.get("collections", [])
            confidence = routing_result.get("confidence", 0.0)
            reasoning = routing_result.get("reasoning", "")
            
            trace.confidence_scores = {c: confidence for c in detected_collections}
            trace.reasoning = reasoning
            
            # Confidence-based fallback
            if confidence < threshold:
                trace.fallback_triggered = True
                trace.detected_collections = None  # None = all collections
                logger.info(f"Collection routing confidence {confidence} < {threshold}, falling back to all collections")
                return [], trace  # Empty list = all collections
            
            trace.detected_collections = detected_collections
            return detected_collections, trace
        
        except Exception as e:
            logger.error(f"Collection routing failed: {e}")
            trace.fallback_triggered = True
            trace.detected_collections = None
            trace.reasoning = f"Routing failed: {str(e)}"
            return [], trace  # Fallback to all collections
```

---

## Integration Points

### 1. ChatService Integration

**Location:** `backend/chat/service.py:102-106`

**Current:**
```python
retrieved_chunks, trace = self.advanced_retrieval_service.retrieve(
    query_text=query_text,
    config=advanced_config,
    collection_ids=session.collection_ids,
)
```

**Updated:**
```python
# Collection routing (if enabled and session has no collections)
routed_collection_ids = session.collection_ids
collection_routing_trace = None

if advanced_config.enable_collection_routing and not session.collection_ids:
    routed_collection_ids, collection_routing_trace = self.collection_routing_service.route_query(
        query=query_text,
        session_collection_ids=session.collection_ids,
        threshold=advanced_config.collection_routing_threshold
    )

# Retrieval (with multi-hop support)
retrieved_chunks, trace = self.advanced_retrieval_service.retrieve(
    query_text=query_text,
    config=advanced_config,
    collection_ids=routed_collection_ids,
)

# Attach collection routing trace
if collection_routing_trace:
    trace.collection_routing = collection_routing_trace
```

### 2. AdvancedRetrievalService Integration

**Location:** `backend/chat/retrieval.py:278-496`

**Current:** Parallel multi-query execution with RRF merging

**Updated:** Route to multi-hop orchestrator if enabled

```python
def retrieve(
    self,
    query_text: str,
    config: AdvancedRetrievalConfig,
    collection_ids: Optional[List[str]] = None
) -> Tuple[List[Candidate], RetrievalTrace]:
    # ... existing classification and routing logic ...
    
    # NEW: Multi-hop routing
    if config.enable_multi_hop and trace.transformations.sub_questions:
        # Use MultiHopRetrievalOrchestrator
        candidates, reasoning_chain = self.multi_hop_orchestrator.execute_multi_hop(
            query=query_text,
            sub_questions=trace.transformations.sub_questions,
            config=config,
            collection_ids=collection_ids
        )
        trace.reasoning_chain = reasoning_chain
    else:
        # Existing parallel execution path (unchanged)
        candidates = self._execute_parallel_retrieval(...)
    
    # Reranking (updated to use real reranker)
    if config.enable_reranking:
        candidates = self.reranking_service.rerank(query_text, candidates)
    
    return candidates, trace
```

---

## Performance Considerations

### Latency Budget

| Component | Current | With Feature | Budget |
|-----------|---------|--------------|--------|
| Classification | 50ms | 50ms | 100ms |
| Collection Routing | 0ms | 100ms | 500ms |
| Multi-Hop (3 hops) | 200ms (parallel) | 900ms (sequential) | 3000ms |
| Reranking | 0ms (dummy) | 150ms | 200ms |
| **Total** | **250ms** | **1200ms** | **3800ms** |

**Mitigation:**
- Add `multi_hop_timeout_ms` (default: 30000ms)
- Add `max_hops` limit (default: 3)
- Make multi-hop opt-in (default: False)
- Cache intermediate LLM results where possible

### Memory Considerations

- Cross-encoder model: ~100MB-500MB RAM
- Intermediate answers: ~1KB per hop
- Reasoning chain trace: ~5KB per query
- Collection metadata: ~10KB total

**Total additional memory:** ~500MB (mostly model)

---

## Rollback Strategy

### Feature Flags

All new features are opt-in via configuration flags:
- `enable_multi_hop`: False (default)
- `enable_collection_routing`: False (default)
- `enable_reranking`: True (but with fallback to dummy)

### Rollback Steps

1. **Immediate rollback:** Set all flags to False via configuration
2. **Partial rollback:** Disable specific component (e.g., multi-hop only)
3. **Full rollback:** Revert code changes (new services are isolated, easy to remove)

### Data Rollback

- New trace fields are optional - no database migration needed
- If database migration added `retrieval_trace_json` column, it can remain (unused)

---

## Testing Strategy

### Unit Tests

- `test_multi_hop_orchestrator.py` - Sequential execution, intermediate answers, fallback
- `test_real_reranking_service.py` - Model loading, inference, fallback to dummy
- `test_collection_routing_service.py` - LLM routing, confidence scoring, fallback

### Integration Tests

- `test_multi_hop_integration.py` - End-to-end multi-hop query flow
- `test_reranking_integration.py` - Reranking in full retrieval pipeline
- `test_collection_routing_integration.py` - Routing + retrieval flow

### Performance Tests

- Measure latency for multi-hop queries (target: <3s for 3 hops)
- Measure reranking latency (target: <200ms for 50 candidates)
- Measure collection routing latency (target: <500ms)

### Edge Case Tests

- 0 sub-questions → fall back to baseline
- All sub-questions fail → fall back to original query
- Collection routing returns 0 collections → search all
- Cross-encoder model fails to load → fall back to dummy
- LLM calls timeout → graceful degradation

---

## Open Questions

**Q1:** Should intermediate answers be cached to avoid redundant LLM calls for similar queries?
- **Answer:** Defer to post-MVP optimization. Add TODO for caching layer.

**Q2:** Should multi-hop be automatically enabled for all "multi_hop" classified queries, or require explicit opt-in?
- **Answer:** Automatic for classified queries, but can be overridden via config flag.

**Q3:** Should collection routing use embedding similarity as a fallback if LLM routing fails?
- **Answer:** Defer to post-MVP. Current fallback (all collections) is safe.

---

## Design Approval Checklist

- [x] Red-team analysis completed and risks addressed
- [x] Separate execution path for multi-hop (no modification to parallel path)
- [x] Backward-compatible schema extension strategy
- [x] Comprehensive error handling with fallback at each stage
- [x] Configuration flag hierarchy and precedence rules defined
- [x] Integration points identified and approach documented
- [x] Performance budget defined with mitigation strategies
- [x] Rollback strategy defined
- [x] Testing strategy defined

**Status:** Ready for planning phase

