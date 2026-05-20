# Sample Documents - Upload & Testing Guide

**Purpose:** Test retrieval optimization features (reranking, collection routing, multi-hop reasoning)

---

## Documents Included

### 1. Q3 2024 Earnings Report
- **File:** `Q3_2024_Earnings.md`
- **Collection:** `earnings` or `financial-reports`
- **Key Content:** CEO statements about authentication product, financial metrics, product launches
- **Use Case:** Multi-hop queries, collection routing

### 2. Product Authentication Documentation
- **File:** `Product_Authentication_Docs.md`
- **Collection:** `product-docs` or `technical-docs`
- **Key Content:** Technical specs, API integration, features, troubleshooting
- **Use Case:** Reranking, product queries, technical questions

### 3. CEO Blog Post
- **File:** `CEO_Blog_Authentication.md`
- **Collection:** `blog` or `executive-insights`
- **Key Content:** CEO perspective on authentication, industry insights, future roadmap
- **Use Case:** Multi-hop reasoning, CEO statements

### 4. Company Policies
- **File:** `Company_Policies.md`
- **Collection:** `policies` or `hr-policies`
- **Key Content:** Return policy, remote work, vacation, code of conduct
- **Use Case:** Collection routing (different domain), policy queries

---

## Setup Instructions

### Step 1: Create Collections

Create 4 collections in your RAG system:

```bash
# Collection 1: Financial/Earnings
POST /api/collections
{
  "name": "earnings",
  "description": "Q3 2024 earnings reports, financial statements, and investor relations materials"
}

# Collection 2: Product Documentation
POST /api/collections
{
  "name": "product-docs",
  "description": "Technical documentation for TechCorp products including authentication system, APIs, and integration guides"
}

# Collection 3: Executive Insights
POST /api/collections
{
  "name": "blog",
  "description": "CEO blog posts, executive insights, and strategic announcements"
}

# Collection 4: Company Policies
POST /api/collections
{
  "name": "policies",
  "description": "Company policies including HR, return policy, remote work, and code of conduct"
}
```

### Step 2: Upload Documents

Upload each document to its respective collection:

```bash
# Upload Q3 Earnings
POST /api/collections/earnings/documents
{
  "file": "Q3_2024_Earnings.md",
  "title": "Q3 2024 Earnings Report",
  "metadata": {
    "date": "2024-10-15",
    "type": "earnings-report"
  }
}

# Upload Product Docs
POST /api/collections/product-docs/documents
{
  "file": "Product_Authentication_Docs.md",
  "title": "AI-Enhanced Authentication System - Product Documentation",
  "metadata": {
    "product": "authentication",
    "version": "2.0"
  }
}

# Upload CEO Blog
POST /api/collections/blog/documents
{
  "file": "CEO_Blog_Authentication.md",
  "title": "CEO Blog: The Future of Authentication is Here",
  "metadata": {
    "author": "John Smith",
    "date": "2024-09-15"
  }
}

# Upload Policies
POST /api/collections/policies/documents
{
  "file": "Company_Policies.md",
  "title": "TechCorp Company Policies",
  "metadata": {
    "effective_date": "2024-01-01",
    "version": "3.2"
  }
}
```

### Step 3: Index Documents

Wait for documents to be chunked and indexed (typically 1-5 minutes per document).

Verify indexing:
```bash
GET /api/collections/earnings/status
GET /api/collections/product-docs/status
GET /api/collections/blog/status
GET /api/collections/policies/status
```

---

## Test Scenarios

### Test 1: Reranking Feature

**Query:** "How does the authentication system work?"

**Config:**
```json
{
  "advanced_config": {
    "enable_reranking": true,
    "rerank_threshold": 0.3,
    "enable_collection_routing": false,
    "enable_multi_hop": false
  }
}
```

**Expected Results:**
- Top chunks from `Product_Authentication_Docs.md`
- `retrieval_trace.reranking` shows:
  - `pre_order_ids` vs `post_order_ids` (different order)
  - `latency_ms` <200ms
  - `model`: "cross-encoder/ms-marco-MiniLM-L-6-v2"

**Verification:**
- Reranked chunks more relevant than original order
- Latency acceptable

---

### Test 2: Collection Routing

**Query:** "What is the return policy?"

**Config:**
```json
{
  "collection_ids": [],  // Empty = auto-detect
  "advanced_config": {
    "enable_collection_routing": true,
    "collection_routing_threshold": 0.7,
    "enable_reranking": false,
    "enable_multi_hop": false
  }
}
```

**Expected Results:**
- Routes to `policies` collection
- `retrieval_trace.collection_routing`:
  - `routing_decision`: ["policies"]
  - `confidence`: >0.7
  - `reasoning`: "Query about return policy is in company policies"

**Verification:**
- Correct collection selected
- Confidence score reasonable
- Reasoning explains decision

---

### Test 3: Collection Routing - Ambiguous Query

**Query:** "What happened last quarter?"

**Config:**
```json
{
  "collection_ids": [],
  "advanced_config": {
    "enable_collection_routing": true,
    "collection_routing_threshold": 0.7,
    "enable_reranking": false,
    "enable_multi_hop": false
  }
}
```

**Expected Results:**
- Low confidence (<0.7)
- Falls back to all collections
- `retrieval_trace.collection_routing`:
  - `routing_decision`: [] (empty = all collections)
  - `confidence`: <0.7
  - `fallback_reason`: "Confidence below threshold"

**Verification:**
- Fallback triggered for ambiguous query
- Searches all collections

---

### Test 4: Multi-Hop Reasoning

**Query:** "What did the CEO say about the product mentioned in Q3 earnings?"

**Config:**
```json
{
  "advanced_config": {
    "enable_multi_hop": true,
    "enable_decomposition": true,
    "enable_reranking": true,
    "max_hops": 3,
    "multi_hop_timeout_ms": 30000
  }
}
```

**Expected Results:**
- Decomposes into 2 sub-questions:
  1. "What product was mentioned in Q3 earnings?"
  2. "What did the CEO say about [product]?"
- `retrieval_trace.reasoning_chain`:
  - `hops`: Array with 2 ReasoningStep objects
  - Hop 1: Retrieves from earnings, intermediate answer: "AI-Enhanced Authentication System"
  - Hop 2: Retrieves CEO statements about authentication
  - `total_hops`: 2
  - `total_latency_ms`: 3000-6000ms

**Verification:**
- Correct decomposition
- Intermediate answers make sense
- Final answer synthesizes both hops
- Latency 2-3x baseline

---

### Test 5: Multi-Hop with Collection Routing

**Query:** "Compare the pricing strategy in the 2024 plan with actual product pricing"

**Config:**
```json
{
  "collection_ids": [],
  "advanced_config": {
    "enable_collection_routing": true,
    "enable_multi_hop": true,
    "enable_decomposition": true,
    "enable_reranking": true,
    "collection_routing_threshold": 0.7,
    "max_hops": 3
  }
}
```

**Expected Results:**
- Collection routing: Routes to `product-docs` (pricing info)
- Multi-hop: Decomposes into 2-3 hops
- Reranking: Applied at each hop
- Full trace shows all three features working together

**Verification:**
- All three features active
- No conflicts between features
- Final answer comprehensive

---

### Test 6: Simple Query (No Multi-Hop)

**Query:** "What is the company mission?"

**Config:**
```json
{
  "advanced_config": {
    "enable_multi_hop": true,
    "enable_decomposition": true,
    "enable_reranking": true
  }
}
```

**Expected Results:**
- Single sub-question detected
- Multi-hop skipped
- `retrieval_trace.reasoning_chain.fallback_reason`: "Single sub-question, no multi-hop needed"
- Fast response (baseline latency)

**Verification:**
- Multi-hop correctly skipped for simple queries
- No performance penalty

---

## Performance Benchmarks

### Baseline (No Features)
- Latency: ~1-2 seconds
- Chunks: Top 10 by similarity score

### With Reranking
- Latency: ~1.2-2.2 seconds (+200ms)
- Chunks: Top 10 by cross-encoder score
- Quality: Better relevance

### With Collection Routing
- Latency: ~1.5-2.5 seconds (+500ms)
- Chunks: From selected collection only
- Quality: More focused results

### With Multi-Hop (2 hops)
- Latency: ~3-5 seconds (2-3x baseline)
- Chunks: From sequential retrieval
- Quality: Answers complex questions

### All Features Combined
- Latency: ~4-7 seconds
- Chunks: Multi-hop + reranked + routed
- Quality: Best for complex queries

---

## Troubleshooting

### Reranking Not Working
- Check `enable_reranking: true`
- Verify cross-encoder model loaded
- Check logs for model loading errors
- Falls back to similarity sorting if model fails

### Collection Routing Always Fallback
- Check collection descriptions in database
- Verify collections have meaningful names
- Try more specific queries
- Lower confidence threshold to test

### Multi-Hop Not Triggering
- Verify `enable_decomposition: true`
- Check query decomposes into >1 sub-question
- Review classification in trace
- Try more complex queries

### Timeout Errors
- Reduce `max_hops` (try 2 instead of 3)
- Reduce `multi_hop_timeout_ms` (try 20000 instead of 30000)
- Check if sub-questions are too complex
- Review logs for slow retrieval steps

---

## Sample Queries by Feature

### Reranking Queries
- "How does the authentication system work?"
- "What are the key features of the authentication platform?"
- "Explain the behavioral biometrics approach"

### Collection Routing Queries
- "What is the return policy?" → policies
- "What are the Q3 earnings?" → earnings
- "How do I integrate the authentication API?" → product-docs
- "What did the CEO say?" → blog

### Multi-Hop Queries
- "What did the CEO say about the product mentioned in Q3 earnings?"
- "Compare the pricing strategy in the 2024 plan with actual product pricing"
- "What authentication improvements were mentioned in earnings and what did the CEO say about them?"

### Combined Queries
- "What is the return policy for the authentication system mentioned in Q3 earnings?"
- "Compare CEO statements about authentication with the technical documentation"

---

## Next Steps

1. **Upload documents** to your RAG system
2. **Create collections** as specified
3. **Run test scenarios** in order
4. **Verify results** against expected outcomes
5. **Monitor performance** metrics
6. **Adjust thresholds** as needed for your use case

---

**Questions?** Contact: support@techcorp.com

---

*Last Updated: 2026-05-20*
