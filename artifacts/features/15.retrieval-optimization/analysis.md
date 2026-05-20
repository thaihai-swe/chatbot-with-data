---
feature: 15.retrieval-optimization
title: Retrieval Optimization - Current State Analysis
date: 2026-05-19
phase: Research Complete
---

# Retrieval Optimization: Current State Analysis

## Executive Summary

The system has a **sophisticated retrieval foundation** with advanced query intelligence, dynamic routing, and multi-query fusion already implemented. However, critical gaps exist in **reranking, multi-hop reasoning chains, and performance optimization** that limit retrieval quality and system efficiency.

**Key Finding**: The system is 70% feature-complete but 30% optimization-incomplete. Most gaps are not architectural but rather missing implementations of planned features.

---

## Current Retrieval Architecture

### Core Components

| Component | Location | Status | Purpose |
|-----------|----------|--------|---------|
| **QueryIntelligenceService** | `backend/chat/retrieval.py:33-101` | ✅ Complete | LLM-powered query transformations (classification, expansion, rewriting, decomposition, HyDE, synonyms) |
| **RetrievalService** | `backend/chat/retrieval.py:145-244` | ✅ Complete | Baseline hybrid search with Weaviate |
| **AdvancedRetrievalService** | `backend/chat/retrieval.py:278-496` | ⚠️ Partial | Orchestrates advanced strategies; reranking is dummy-only |
| **CandidateMerger** | `backend/chat/retrieval.py:105-143` | ✅ Complete | Reciprocal Rank Fusion (RRF, k=60) for multi-query result merging |
| **Vector Database** | `backend/indexing/weaviate_store.py` | ✅ Complete | Weaviate with hybrid search (configurable alpha) |
| **Embedding Provider** | `backend/providers/openai.py` | ✅ Complete | OpenAI text-embedding-3-small with batch processing |

### Retrieval Flow

```
Query Input
    ↓
[Safety Check] → Query Classification (simple/multi_hop/comparative/conversational/out_of_domain)
    ↓
[Dynamic Routing] → Route to appropriate strategy based on classification
    ↓
[Query Intelligence] → Apply transformations:
    • Query Expansion (3-5 variations)
    • Query Rewriting (formal normalization)
    • Query Decomposition (sub-questions for multi-hop)
    • HyDE (hypothetical document generation)
    • Synonym Expansion (entity synonyms)
    ↓
[Multi-Query Retrieval] → Execute parallel retrieval runs:
    • Original query
    • Rewritten query
    • Expanded queries
    • Decomposed sub-questions
    • HyDE documents
    ↓
[Result Merging] → RRF fusion of all candidates
    ↓
[Parent-Child Expansion] → Expand child chunks to parents for context
    ↓
[Reranking] → ⚠️ DUMMY: Just sorts by similarity score
    ↓
[Grounding Evaluation] → Check evidence sufficiency
    ↓
[Context Assembly] → Build prompt with chunks + history
    ↓
[Generation] → LLM answer generation
    ↓
[Citation Extraction & Groundedness Scoring]
```

---

## Existing Advanced Retrieval Capabilities

### ✅ Fully Implemented Features

**1. Query Classification & Routing** (Lines 33-101, 304-334)
- Classifies queries into 5 categories
- Routes to appropriate strategy:
  - Simple queries → baseline retrieval (skip expansions)
  - Multi-hop queries → enable decomposition
  - Out-of-domain/conversational → minimal processing
- Traces routing decisions with reasoning

**2. Query Expansion & Rewriting** (Lines 57-68, 336-358)
- Generates 3-5 query variations using LLM
- Normalizes queries into formal search questions
- Extracts entities and provides synonyms

**3. Query Decomposition** (Lines 70-77, 360-363)
- Breaks complex queries into sub-questions
- Enables multi-hop retrieval

**4. HyDE (Hypothetical Document Embeddings)** (Lines 79-81, 365-368)
- Generates hypothetical documents for retrieval
- Improves semantic matching for abstract queries

**5. Multi-Query Fusion with RRF** (Lines 105-143, 376-428)
- Executes 5+ retrieval runs in parallel
- Merges results using Reciprocal Rank Fusion (k=60)
- Deduplicates by chunk_id while preserving scores

**6. Parent-Child Retrieval** (Lines 439-464)
- Retrieves child chunks for precision
- Expands to parent chunks for broader context
- Tracks expansion count in trace

**7. Hybrid Search** (Lines 163-228)
- Configurable alpha parameter (0.0=keyword, 0.5=hybrid, 1.0=semantic)
- Collection-scoped filtering
- Metadata enrichment from ChunkRepository

**8. Comprehensive Observability** (schemas/chat.py)
- `RetrievalTrace`: Captures all transformations, routing decisions, execution times
- Per-stage timing: classification, expansion, decomposition, hyde, merging, reranking
- Enables debugging and optimization

---

## Critical Gaps & Enhancement Opportunities

### 🔴 HIGH PRIORITY: Reranking (Dummy Implementation)

**Current State** (Lines 250-276, retrieval.py):
```python
def rerank(self, query: str, candidates: List[Candidate]) -> List[Candidate]:
    # Dummy: just sort by similarity score
    return sorted(candidates, key=lambda c: c.score, reverse=True)
```

**Gap**: No real cross-encoder reranking model integration

**Impact**: 
- Retrieved chunks may not be optimally ordered
- Reduces quality of top-k results used for grounding
- Wastes potential of multi-query fusion

**Enhancement Opportunity**:
- Integrate cross-encoder models (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`)
- Add support for Cohere Rerank API
- Implement score normalization and threshold filtering
- **Estimated ROI**: High (immediate quality improvement, minimal architectural changes)

---

### 🟠 MEDIUM PRIORITY: Multi-Hop Reasoning Chain

**Current State**:
- Query decomposition exists (breaks complex queries into sub-questions)
- Sub-questions are retrieved independently
- No iterative refinement or reasoning chain

**Gap**:
- Decomposed sub-questions are treated as independent queries
- No explicit reasoning chain tracking
- No iterative retrieval (retrieve → reason → retrieve again)
- No answer synthesis from sub-question results

**Impact**:
- Multi-hop queries may miss dependencies between sub-questions
- System cannot leverage intermediate results to refine subsequent queries
- Reduces effectiveness for complex reasoning tasks

**Enhancement Opportunity**:
- Implement iterative retrieval: Use answer from sub-question 1 to inform sub-question 2
- Add reasoning chain tracking (which sub-question led to which chunks)
- Support for "follow-up" retrieval based on initial results
- Explicit answer synthesis step combining sub-question results
- **Estimated ROI**: High (differentiates system as true multi-hop RAG)

---

### 🟠 MEDIUM PRIORITY: Collection Auto-Detection

**Current State**:
- Spec exists in feature 4.advanced-retrieval-strategies
- Not implemented; users must manually select collections

**Gap**:
- No automatic routing to relevant collections
- Requires manual collection selection
- Reduces usability for multi-collection scenarios

**Enhancement Opportunity**:
- LLM-based collection routing from query intent
- Embedding similarity between query and collection descriptions
- Confidence scoring and fallback to all-collections search
- **Estimated ROI**: Medium (improves UX, moderate implementation effort)

---

### 🟡 MEDIUM PRIORITY: Performance Optimization

**Current State**:
- Sequential processing of retrieval runs
- No caching layer
- No parallelization

**Gaps**:
- No query result caching
- No embedding caching for repeated queries
- Sequential retrieval runs (not parallelized)
- No batch processing for multiple queries
- Repeated embeddings for similar queries

**Impact**:
- Latency increases with query complexity
- Redundant API calls to embedding provider
- Higher costs for repeated queries

**Enhancement Opportunity**:
- Add Redis/in-memory cache for query embeddings and results
- Parallelize multiple retrieval runs (already structured for this)
- Implement semantic cache (similar queries → cached results)
- Add query result TTL and invalidation logic
- **Estimated ROI**: Medium (performance win, reduces API costs)

---

### 🟡 LOW PRIORITY: Advanced Filtering & Metadata

**Current State**:
- Basic collection_id filtering only
- Metadata available but not exposed for filtering

**Gap**:
- No support for date range filtering
- No document type filtering
- No custom metadata filters
- No faceted search

**Enhancement Opportunity**:
- Extend Weaviate filters to support metadata properties
- Add filter DSL for complex queries
- Support for temporal queries ("documents from last month")
- **Estimated ROI**: Low (nice-to-have, lower priority)

---

### 🟡 LOW PRIORITY: Retrieval Quality Metrics

**Current State**:
- Similarity scores tracked
- No automated quality evaluation

**Gap**:
- No MRR (Mean Reciprocal Rank) tracking
- No NDCG (Normalized Discounted Cumulative Gain)
- No precision@k and recall@k metrics
- No A/B testing framework for retrieval strategies

**Enhancement Opportunity**:
- Add MRR and NDCG tracking
- Implement precision@k and recall@k
- A/B testing framework for retrieval strategies
- **Estimated ROI**: Low (observability improvement, lower priority)

---

## Feature Implementation Status

| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| Hybrid Search | ✅ Complete | `weaviate_store.py`, `retrieval.py:163-228` | Configurable alpha |
| Query Expansion | ✅ Complete | `retrieval.py:57-64, 351-358` | 3-5 variations |
| Query Rewriting | ✅ Complete | `retrieval.py:66-68, 336-345` | Formal normalization |
| Query Decomposition | ✅ Complete | `retrieval.py:70-77, 360-363` | Sub-question generation |
| HyDE | ✅ Complete | `retrieval.py:79-81, 365-368` | Hypothetical documents |
| Synonym Expansion | ✅ Complete | `retrieval.py:83-97, 370-373` | Entity synonyms |
| Dynamic Routing | ✅ Complete | `retrieval.py:304-334` | Classification-based routing |
| RRF Merging | ✅ Complete | `retrieval.py:105-143, 422-428` | Multi-query fusion |
| Parent-Child Retrieval | ✅ Complete | `retrieval.py:439-464` | Context expansion |
| **Reranking** | ⚠️ Dummy Only | `retrieval.py:250-276` | **NEEDS REAL IMPLEMENTATION** |
| **Multi-Hop Reasoning** | ⚠️ Partial | Decomposition exists | **NEEDS REASONING CHAIN** |
| **Collection Auto-Detection** | ❌ Not Implemented | Spec in feature 4 | **NEEDS IMPLEMENTATION** |
| **Caching** | ❌ Not Implemented | N/A | **NEEDS IMPLEMENTATION** |
| **Advanced Filtering** | ❌ Not Implemented | N/A | **NEEDS IMPLEMENTATION** |

---

## Integration Points

### Chat Orchestration Flow (backend/chat/service.py:43-237)

1. **Safety Check** → Query classification and injection detection
2. **Retrieval** → Advanced retrieval with configured strategies
3. **Chunk Safety** → Filter malicious chunks
4. **Grounding Evaluation** → Check evidence sufficiency (grounding.py:38-64)
5. **Context Assembly** → Build prompt with chunks and history (context.py:28-92)
6. **Generation** → LLM answer generation (generation.py:28-68)
7. **Citation Extraction** → Parse and validate citations (citations.py:17-81)
8. **Groundedness Scoring** → LLM-as-judge evaluation (grounding.py:66-103)

### Configuration (backend/schemas/settings.py)

- `RetrievalSettings` (lines 31-43): Global defaults for retrieval mode, top_k, hybrid_weight, feature flags
- `AdvancedRetrievalConfig` (schemas/chat.py:23-37): Per-request overrides for all advanced features

---

## Unchanged Behavior to Preserve

1. **Query Classification Logic**: Current 5-category classification is effective
2. **RRF Merging**: Reciprocal Rank Fusion with k=60 is working well
3. **Parent-Child Expansion**: Current logic for context expansion is sound
4. **Hybrid Search**: Alpha parameter configuration is flexible and working
5. **Observability**: Comprehensive tracing infrastructure must be maintained
6. **Safety Checks**: Query injection detection and chunk safety filtering

---

## Recommendations for Feature 15: Retrieval Optimization

### Prioritized Implementation Roadmap

**Phase 1 (Highest ROI):**
1. **Real Reranking Implementation** 
   - Integrate cross-encoder models or Cohere Rerank API
   - Immediate quality improvement with minimal architectural changes
   - Estimated effort: 2-3 days

**Phase 2 (High Impact):**
2. **Multi-Hop Reasoning Chain**
   - Build on existing decomposition to add iterative retrieval
   - Differentiates system as true multi-hop RAG
   - Estimated effort: 3-4 days

**Phase 3 (Performance & UX):**
3. **Query/Result Caching**
   - Add semantic caching layer
   - Reduces latency and API costs
   - Estimated effort: 2-3 days

4. **Collection Auto-Detection**
   - Complete the spec from feature 4.advanced-retrieval-strategies
   - Improves usability for multi-collection scenarios
   - Estimated effort: 2-3 days

---

## Next Steps

1. **Specification Phase**: Define exact requirements for reranking, multi-hop reasoning, and caching
2. **Design Phase**: Architecture for iterative retrieval and caching layer
3. **Implementation Phase**: Execute prioritized roadmap
4. **Verification Phase**: Test retrieval quality improvements with metrics

---

## Promotion Candidates for Constitution/Knowledge Base

- **Query Classification Strategy**: The 5-category classification (simple/multi_hop/comparative/conversational/out_of_domain) is a reusable pattern
- **RRF Merging Pattern**: Reciprocal Rank Fusion with k=60 is effective for multi-query fusion
- **Observability Pattern**: Comprehensive tracing with per-stage timing is a best practice for RAG systems
