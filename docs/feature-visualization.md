# 📊 Feature Visualization & Decision Trees

**RAG Knowledge Base Lab - Complete System Flow Guide**

---

## Complete System Flow

```
┌─────────────────────────────────────┐
│     USER INPUT (Query/Document)     │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Query Enhancement (if query)        │
│ ├─ Rewrite ambiguous queries        │
│ ├─ Classify intent                  │
│ └─ Select retrieval mode            │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Security Validation                 │
│ ├─ Check injection patterns         │
│ ├─ Scan for PII                     │
│ ├─ Validate size limits             │
│ └─ Log security events              │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Query Tracing START                 │
│ └─ Capture all pipeline steps       │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Retrieval (Core RAG)                │
│ ├─ Apply collection filters         │
│ ├─ Hybrid search (BM25 + semantic)  │
│ ├─ Rerank results                   │
│ └─ Context windowing                │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Generation                          │
│ ├─ Build context from chunks        │
│ ├─ Stream LLM response              │
│ └─ Extract citations                │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Safety & Grounding                  │
│ ├─ Validate citations               │
│ ├─ Calculate groundedness score     │
│ ├─ Detect hallucinations            │
│ └─ Compute confidence score         │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Query Tracing END                   │
│ ├─ Log performance metrics          │
│ ├─ Store trace to JSONL            │
│ └─ Display trace (if --trace)       │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ OUTPUT: Answer + Citations          │
│ + Confidence + Groundedness         │
└─────────────────────────────────────┘
```

---

## Feature Overview Matrix

| Feature | Purpose | Key Components | Example Usage |
|---------|---------|----------------|---------------|
| **Core RAG** | Foundation retrieval and generation | Document loaders, Chunker, Embeddings, Weaviate, LLM, Safety | Upload PDF → Query → Get grounded answer |
| **Hybrid Search** | Balance keyword + semantic matching | BM25 scorer, Vector search, Alpha weighting | Tune alpha for technical vs general content |
| **Grounding & Citations** | Ensure answer accuracy | Citation validator, Groundedness scorer | Every answer includes source citations |
| **Safety Filters** | Prevent hallucinations | Prompt injection detector, PII scanner, Content moderator | Auto-reject malicious queries |
| **Streaming Orchestrator** | Real-time responses | Async token streaming, Safety checks | Stream answer tokens as generated |
| **Collection Management** | Organize knowledge bases | Metadata tagging, Deduplication, Filtering | Separate collections for different domains |
| **Query Tracing** | Debug and optimize | Trace logger, Performance profiler | View all pipeline steps with --trace |

---

## Decision Trees

### "Which retrieval strategy should I use?"

```
YOUR QUESTION
    ↓
What type of query is it?
    ├─ Simple factual question?
    │  (e.g., "What is RAG?")
    │  → Hybrid search with alpha=0.5 ✓
    │     Fast, balanced, 500ms
    │
    ├─ Technical query with exact terms?
    │  (e.g., "ERR-404 error code")
    │  → Hybrid search with alpha=0.3 ✓
    │     Favor keywords, 600ms
    │
    └─ Conceptual or semantic query?
       (e.g., "Best practices for security")
       → Hybrid search with alpha=0.7 ✓
          Favor semantics, 700ms
```

### "How do I handle document ingestion?"

```
DOCUMENT SOURCE
    ↓
What format is your data?
    ├─ PDF document → Use PDF loader ✓
    │  (Preserves pages, handles layouts)
    │  Max size: 100 MB
    │
    ├─ Plain text (.txt, .md) → Use text loader ✓
    │  (Fast, simple, good for notes)
    │  Max size: 100 MB
    │
    └─ Web content (URL) → Use URL loader ✓
       (Fetches HTML, extracts clean text)
       Timeout: 30s
```

### "Should I enable safety features?"

```
SAFETY CONFIGURATION
    ↓
What's your security posture?
    ├─ Production system with sensitive data?
    │  → Enable all safety features ✓
    │  ├─ Prompt injection detection: strict
    │  ├─ PII detection: moderate
    │  ├─ Grounding validation: enabled
    │  └─ Audit logging: enabled
    │
    ├─ Development/testing environment?
    │  → Enable basic safety ✓
    │  ├─ Prompt injection: moderate
    │  ├─ PII detection: lenient
    │  └─ Audit logging: optional
    │
    └─ Internal trusted environment?
       → Minimal safety (not recommended) ⚠️
       └─ Only basic validation
```

### "How do I interpret confidence scores?"

```
CONFIDENCE SCORES (0.0 - 1.0)
    ↓
Answer Confidence Interpretation:
    ├─ 0.90-1.0: VERY HIGH ✓✓
    │  └─ Highly grounded, multiple citations
    │     Action: Trust the answer
    │
    ├─ 0.70-0.90: HIGH ✓
    │  └─ Well-grounded, good citations
    │     Action: Reliable answer
    │
    ├─ 0.50-0.70: MEDIUM 🟡
    │  └─ Partially grounded
    │     Action: Verify sources manually
    │
    ├─ 0.30-0.50: LOW ⚠️
    │  └─ Weak grounding
    │     Action: Review documents, may need more data
    │
    └─ 0.0-0.30: VERY LOW ❌
       └─ Insufficient evidence
          Action: Don't trust, add more documents
```

---

## Feature Interaction Flow

```
USER QUERY
    ↓
┌───────────────────────────────┐
│  1. PARSE INPUT               │
│  - Query text                 │
│  - Collection filter          │
│  - Configuration overrides    │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  2. SECURITY VALIDATION       │
│  - Check query length         │
│  - Detect injection patterns  │
│  - Scan for malicious content │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  3. EMBED QUERY               │
│  - Generate query embedding   │
│  - Cache for reuse            │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  4. HYBRID RETRIEVAL          │
│  - Semantic search (Weaviate) │
│  - BM25 keyword search        │
│  - Combine with alpha weight  │
│  - Rank by hybrid score       │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  5. RERANK & FILTER           │
│  - Apply reranking rules      │
│  - Filter by relevance        │
│  - Select top-K chunks        │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  6. CONTEXT WINDOWING         │
│  - Check token budget         │
│  - Trim to fit LLM context    │
│  - Preserve highest-scoring   │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  7. GENERATE ANSWER           │
│  - Build prompt with context  │
│  - Stream LLM response        │
│  - Extract citations          │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  8. VALIDATE & SCORE          │
│  - Validate citations         │
│  - Calculate groundedness     │
│  - Compute confidence         │
│  - Detect hallucinations      │
└────────┬──────────────────────┘
         ↓
┌───────────────────────────────┐
│  9. FORMAT & RETURN           │
│  - Add citation links         │
│  - Show confidence score      │
│  - Display safety flags       │
│  - Store in chat history      │
└────────┬──────────────────────┘
         ↓
     USER SEES ANSWER
```

---

## Hybrid Retrieval Scoring Example

### Scenario: Query = "Python web development"

```
Chunk 1: "Python is widely used for web development with frameworks like Django and Flask"
  ├─ Semantic similarity: 0.95 (very close meaning)
  ├─ Keyword overlap: 1.0 (has all keywords)
  └─ Hybrid score: 0.95*0.5 + 1.0*0.5 = 0.975 🟢 RANK #1

Chunk 2: "Web development requires knowledge of HTML, CSS, and JavaScript"
  ├─ Semantic similarity: 0.60 (related topic)
  ├─ Keyword overlap: 0.33 (has "web development" only)
  └─ Hybrid score: 0.60*0.5 + 0.33*0.5 = 0.465 🟡 RANK #3

Chunk 3: "Django is a Python framework for building web applications quickly"
  ├─ Semantic similarity: 0.88 (closely related)
  ├─ Keyword overlap: 0.67 (has "Python" and "web")
  └─ Hybrid score: 0.88*0.5 + 0.67*0.5 = 0.775 🟢 RANK #2

FINAL RANKING:
#1 → Chunk 1 (0.975) ✓ Perfect match
#2 → Chunk 3 (0.775) ✓ Good match
#3 → Chunk 2 (0.465) ? Weak match
```

---

## Multi-Turn Conversation Example

### With Conversation History

```
Turn 1:
Q: "What is RAG?"
A: "RAG (Retrieval-Augmented Generation) combines retrieval with LLM generation..."
   [Stored in chat_turns table]
   ↓
Turn 2:
Q: "How does it prevent hallucinations?"
Context available:
   ├─ Previous Q: "What is RAG?"
   ├─ Previous A: "RAG combines retrieval..."
   └─ Inferred: "it" = "RAG"
A: "RAG prevents hallucinations by grounding answers in retrieved documents..."
   [Stored with reference to Turn 1]
   ↓
Turn 3:
Q: "Can you give an example?"
Context available:
   ├─ Turn 1: RAG definition
   ├─ Turn 2: Hallucination prevention
   └─ Inferred: "example" = "example of RAG preventing hallucinations"
A: "For example, if asked 'What is the capital of France?', RAG retrieves documents mentioning Paris..."
   [Stored with reference to Turn 1 & 2]
```

---

## Safety Evaluation Workflow

### Confidence Score Calculation

```
INPUT COMPONENTS:
├─ Retrieved chunks: 5 chunks
├─ Relevance scores: [0.92, 0.87, 0.84, 0.79, 0.75]
├─ Generated answer: "RAG is a technique that..."
└─ Citations: 3 valid citations

PROCESSING:
├─ Top relevance: max(scores) = 0.92
├─ Average relevance: mean(scores) = 0.834
├─ Citation bonus: 3 citations = +0.1
└─ Groundedness check: All claims supported = ✓

FORMULA:
confidence = 0.5*(top) + 0.3*(avg) + 0.2*(baseline) + bonus
           = 0.5*(0.92) + 0.3*(0.834) + 0.2 + 0.1
           = 0.46 + 0.2502 + 0.2 + 0.1
           = 0.9102
           ≈ 0.91 ✓ VERY HIGH CONFIDENCE
```

### Grounding Validation

```
INPUT:
Generated: "RAG was invented by Meta AI in 2020 and uses vector databases"
Retrieved chunks: [
  "RAG combines retrieval with generation (Lewis et al., 2020)",
  "Vector databases store embeddings for semantic search",
  "Meta AI published the RAG paper in 2020"
]

CITATION EXTRACTION:
├─ Citation [1]: "RAG was invented by Meta AI in 2020"
├─ Citation [2]: "uses vector databases"
└─ Total citations: 2

VALIDATION:
├─ Citation [1]: ✓ Supported (chunk 3 mentions Meta AI 2020)
├─ Citation [2]: ✓ Supported (chunk 2 mentions vector databases)
└─ Groundedness: 2/2 = 100% ✓

RESULT:
└─ Groundedness score: 1.0 (perfect)
   └─ All claims supported by sources
   └─ No hallucinations detected
```

---

## Configuration Impact Analysis

### Alpha Weight Impact (Hybrid Search)

```
SCENARIO: Query = "machine learning algorithms"

WITH alpha=0.3 (keyword-heavy):
├─ Chunk A: semantic=0.9, keyword=0.2 → score=0.41
├─ Chunk B: semantic=0.4, keyword=1.0 → score=0.82
└─ Ranking: Chunk B ranked higher (favors exact keywords)
   Use case: Technical documentation, error codes

WITH alpha=0.5 (balanced, default):
├─ Chunk A: semantic=0.9, keyword=0.2 → score=0.55
├─ Chunk B: semantic=0.4, keyword=1.0 → score=0.70
└─ Ranking: Chunk B ranked higher (balanced)
   Use case: General knowledge, mixed content

WITH alpha=0.7 (semantic-heavy):
├─ Chunk A: semantic=0.9, keyword=0.2 → score=0.69
├─ Chunk B: semantic=0.4, keyword=1.0 → score=0.58
└─ Ranking: Chunk A ranked higher (favors meaning)
   Use case: Conceptual queries, synonyms important
```

### Top-K Impact

```
RETRIEVAL QUALITY vs SPEED vs CONTEXT SIZE

top_k=4 (default):
├─ Speed: Fast (500-800ms)
├─ Quality: Good (focused results)
├─ Context size: ~2000 tokens
├─ Cost: Low ($0.002 per query)
└─ Best for: Quick questions, real-time chat

top_k=10:
├─ Speed: Medium (1000-1500ms)
├─ Quality: Better (more context)
├─ Context size: ~5000 tokens
├─ Cost: Medium ($0.005 per query)
└─ Best for: Complex questions, comprehensive answers

top_k=20:
├─ Speed: Slow (2000-3000ms)
├─ Quality: Excellent (abundant context)
├─ Context size: ~10000 tokens
├─ Cost: High ($0.010 per query)
└─ Best for: Research, exhaustive analysis
```

---

## Data Flow Visualization

### From Document to Answer

```
INGESTION PHASE
┌─────────────────┐
│ document.pdf    │
└────────┬────────┘
         ↓
    ┌─────────────────┐
    │ PDF Loader      │
    │ Extract text    │
    └────────┬────────┘
             ↓
    ┌────────────────────────┐
    │ Duplicate Detection    │
    │ Check file hash        │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Document Chunker       │
    │ Split into chunks      │
    │ (512 tokens, 50 overlap)│
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ [Chunk1, Chunk2, ...]  │
    │ With metadata          │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Embedding Service      │
    │ Generate vectors       │
    │ (OpenAI API)           │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Embedding Cache        │
    │ Store in SQLite        │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Weaviate               │
    │ Index vectors +        │
    │ metadata               │
    └────────┬───────────────┘
             ↓
        READY TO QUERY

RETRIEVAL PHASE
┌──────────────────┐
│ Query: "What is  │
│ RAG?"            │
└────────┬─────────┘
         ↓
    ┌─────────────────┐
    │ Safety Check    │
    │ Validate query  │
    └────────┬────────┘
             ↓
    ┌─────────────────────────────┐
    │ Embedding Service           │
    │ Convert query to vector     │
    └────────┬────────────────────┘
             ↓
    ┌──────────────────────────────┐
    │ Weaviate Hybrid Search       │
    │ - Semantic search (vector)   │
    │ - BM25 search (keywords)     │
    │ - Combine with alpha=0.5     │
    └────────┬───────────────────┘
             ↓
    ┌────────────────────────┐
    │ Top-K Selection        │
    │ Get top 4 by score     │
    └────────┬───────────────┘
             ↓
    ┌────────────────────────┐
    │ Retrieved Chunks[]     │
    │ With scores & metadata │
    └────────┬───────────────┘
             ↓
    GENERATION PHASE
┌──────────────────────────┐
│ Streaming Orchestrator   │
│ Build context prompt     │
└────────┬─────────────────┘
         ↓
    ┌──────────────────────────┐
    │ LLM Generation (OpenAI)  │
    │ Stream response tokens   │
    └────────┬─────────────────┘
             ↓
    ┌──────────────────────────┐
    │ Citation Extraction      │
    │ Extract [1], [2], etc.   │
    └────────┬─────────────────┘
             ↓
    SAFETY PHASE
┌────────────────────┐
│ Grounding Service  │
│ Validate citations │
└────────┬───────────┘
         ↓
    ┌────────────────────┐
    │ Confidence Scorer  │
    │ Calculate score    │
    └────────┬───────────┘
             ↓
    ┌────────────────────┐
    │ Answer Result:     │
    │ {text, citations,  │
    │  confidence,       │
    │  groundedness}     │
    └────────┬───────────┘
             ↓
         DISPLAY ANSWER
```

---

## Error Recovery Flowchart

```
OPERATION ATTEMPTED
    ↓
ERROR ENCOUNTERED
    ↓
ERROR TYPE?
    │
    ├─ FileNotFoundError
    │  └─ Suggestion: Check file path exists
    │     Action: Show "ls -la <directory>"
    │
    ├─ PDFParseError
    │  └─ Suggestion: PDF may be encrypted or corrupted
    │     Action: Try converting to text first
    │
    ├─ DuplicateDocumentError
    │  └─ Suggestion: Document already exists
    │     Action: Offer replace/skip/version options
    │
    ├─ APITimeoutError
    │  └─ Suggestion: OpenAI API timeout
    │     Action: Retry with exponential backoff
    │
    ├─ InjectionDetectedError
    │  └─ Suggestion: Query contains suspicious pattern
    │     Action: Show pattern, ask user to rephrase
    │
    └─ WeaviateConnectionError
       └─ Suggestion: Weaviate not accessible
          Action: Check Docker container status
    ↓
USER INFORMED WITH ACTIONABLE MESSAGE
    ↓
RECOVERY ACTION POSSIBLE?
    ├─ YES → Execute automatic recovery
    └─ NO  → User must fix manually
```

---

## Testing Coverage Map

```
FEATURE COVERAGE BY SCENARIO

Scenario 1 (Document Ingestion):
├─ ✓ PDF ingestion
├─ ✓ Text ingestion
├─ ✓ URL ingestion
├─ ✓ Duplicate detection
└─ ✓ Chunking strategies

Scenario 2 (Hybrid Search):
├─ ✓ Semantic search
├─ ✓ BM25 keyword search
├─ ✓ Alpha weighting
└─ ✓ Score combination

Scenario 3 (Grounding & Citations):
├─ ✓ Citation extraction
├─ ✓ Citation validation
├─ ✓ Groundedness scoring
└─ ✓ Hallucination detection

Scenario 4 (Safety & Security):
├─ ✓ Prompt injection detection
├─ ✓ PII scanning
├─ ✓ Content moderation
└─ ✓ Audit logging

Scenario 5 (Multi-Turn Chat):
├─ ✓ Conversation history
├─ ✓ Context awareness
├─ ✓ Session management
└─ ✓ Turn persistence

Scenario 6 (Collection Management):
├─ ✓ Collection creation
├─ ✓ Metadata tagging
├─ ✓ Collection filtering
└─ ✓ Deduplication

Scenario 7 (Streaming):
├─ ✓ Token streaming
├─ ✓ Real-time safety checks
├─ ✓ Citation stitching
└─ ✓ Error handling

Scenario 8 (End-to-End):
├─ ✓ Full pipeline
├─ ✓ Multi-source ingestion
├─ ✓ Complex queries
└─ ✓ System stability
```

---

## Quick Reference: When to Use What

| Use Case | Recommended Configuration |
|----------|---------------------------|
| **Technical documentation** | alpha=0.3, top_k=4, chunk_size=512 |
| **General knowledge** | alpha=0.5, top_k=4, chunk_size=700 |
| **Conceptual queries** | alpha=0.7, top_k=6, chunk_size=1024 |
| **Research/analysis** | alpha=0.5, top_k=10, chunk_size=700 |
| **Real-time chat** | alpha=0.5, top_k=4, streaming=true |
| **High security** | injection_detection=strict, pii_detection=moderate |
| **Development** | injection_detection=moderate, pii_detection=lenient |

---

Great visualization guide! Now you have everything to understand the system deeply! 🎉
