# RAG Knowledge Base Lab

## Product Requirements Document

---

## 1. Summary

Build a learning-focused AI Chatbot Retrieval Augmented Generation (RAG) application that ingests user-provided knowledge sources, retrieves relevant evidence with multiple search strategies, generates answers with citations, and evaluates answer quality and retrieval quality over time. Use OpenAI library to connect to LLM.

Users can chat with the system, ask questions based on ingested documents, and see how different retrieval strategies affect answer quality. The system will also include safety features to refuse unsupported questions, prevent prompt injection, and make retrieval behavior transparent.

This project should serve two purposes:

* Help an engineer learn practical AI engineering concepts end to end.
* Act as a portfolio project that demonstrates production-style RAG patterns.

---

## 2. Product Vision

Create a document-aware AI assistant and experimentation platform that can:

* ingest documents and web content,
* organize documents into collections,
* answer questions using retrieved evidence,
* explain how it reached an answer,
* refuse unsupported questions,
* compare retrieval strategies,
* stream answers in the UI,
* detect duplicate documents,
* detect prompt-injection attempts,
* and measure system quality with repeatable evaluations.

---

## 3. Target Users

* Primary: software engineers transitioning into AI/ML
* Secondary: hiring managers or reviewers evaluating AI engineering skills
* Secondary: learners who want to inspect and compare RAG design choices

---

## 4. Goals

* Demonstrate the full RAG pipeline: ingestion, chunking, embedding, indexing, retrieval, generation, safety, and evaluation.
* Support experimentation across retrieval strategies and prompting approaches.
* Make system behavior visible through citations, scores, debug views, strategy comparisons, and experiment dashboards.
* Keep the first version small enough to build and understand without heavy infrastructure.
* Demonstrate advanced RAG patterns such as pre-retrieval query intelligence, LLM-based query expansion, query decomposition, HyDE, dynamic routing, configurable rerankers, parent-child retrieval, semantic chunking, and prompt-injection defense.

---

## 5. Non-Goals

* General-purpose internet chatbot
* Autonomous agent platform
* Multi-tenant SaaS product
* Large-scale production deployment
* Fine-tuning foundation models in v1

---

## 6. Core User Stories

* Upload documents and URLs to build a knowledge base
* Ask questions and receive answers
* Verify answers via citations
* Observe refusal behavior for weak evidence
* Compare retrieval strategies
* Run evaluations and track improvements
* Inspect pipeline internals, including chunks, scores, prompts, and retrieval modes
* Organize documents into collections and query specific knowledge bases
* Automatically detect duplicate or near-duplicate documents
* Use pre-retrieval query intelligence to expand, rewrite, and decompose questions before retrieval
* Use query expansion, HyDE, or synonym expansion to improve recall
* Use query decomposition for complex, comparative, or multi-hop questions
* Use dynamic routing to select the best retrieval strategy for a query
* Stream generated answers in the chat UI
* Inspect experiment results in a dashboard
* Configure rerankers and compare their effects on answer quality

---

# Must-Have

## 7. Functional Requirements

---

## 7.1 Knowledge Ingestion

The system must support ingestion from:

* PDF
* TXT / Markdown
* Web URLs

The ingestion system must:

* Extract text from supported source types
* Preserve source metadata
* Assign a stable `document_id`
* Support re-ingestion and re-indexing
* Support deletion of documents and associated data
* Store ingestion status and errors
* Associate each document with one or more collections when applicable
* Detect duplicate and near-duplicate documents

---

## 7.1.1 Duplicate Detection

The system must detect duplicate and near-duplicate documents during ingestion.

Duplicate detection should help prevent unnecessary storage, repeated chunks, noisy retrieval results, and misleading evaluation results.

The system must support duplicate detection using one or more of:

* file hash
* normalized text hash
* URL canonicalization
* document title and metadata matching
* chunk-level similarity
* embedding similarity
* near-duplicate text overlap

The system must classify duplicate status as:

* `unique`
* `exact_duplicate`
* `near_duplicate`
* `same_url`
* `same_title_different_content`
* `same_content_different_source`

When a duplicate or near-duplicate is detected, the system should allow one of the following actions:

* skip ingestion
* replace existing document
* ingest as a new version
* ingest anyway
* merge metadata
* warn the user before continuing

The system must log:

* duplicate detection method used
* matched existing document ID
* similarity score, if applicable
* duplicate decision
* user action or system action

The UI must show duplicate warnings during ingestion.

---

## 7.2 Document Processing

The system must chunk content into retrievable units.

The system must support configurable:

* chunk size
* chunk overlap

The system must support multiple chunking strategies:

* Fixed-size chunking
* Heading-aware chunking for Markdown
* Page-aware chunking for PDF
* Parent-child chunking
* Semantic chunking

The system should ensure chunks maintain semantic coherence where possible.

Each chunk must include:

* `document_id`
* `chunk_id`
* `source_type`
* `title`
* `page` or `section`
* `chunk_order`
* `source_url`, if applicable
* `collection_id` or collection metadata, if applicable
* `parent_chunk_id`, if applicable
* `child_chunk_ids`, if applicable
* semantic boundary metadata, if applicable

---

## 7.2.1 Parent-Child Chunking

The system must support parent-child chunking as an advanced chunking strategy.

Parent-child chunking should allow the system to:

* retrieve small, precise child chunks
* expand selected results to larger parent chunks for context
* preserve section-level or page-level coherence
* reduce irrelevant context while keeping enough surrounding information for answer generation

Parent chunks may represent:

* full sections
* full pages
* heading groups
* larger text windows
* document subsections

Child chunks may represent:

* smaller overlapping windows
* individual paragraphs
* sub-sections
* semantically coherent text spans

Each child chunk must maintain a reference to its parent chunk.

Each parent chunk must maintain references to its child chunks.

The retrieval pipeline should support:

* retrieving child chunks first
* expanding child chunks to parent chunks before generation
* displaying both child and parent relationships in debug view
* citing the exact child chunk used to support a claim

---

## 7.2.2 Semantic Chunking

The system must support semantic chunking as an advanced chunking strategy.

Semantic chunking should split documents based on meaning instead of only character count or token count.

Semantic chunking may use:

* paragraph boundaries
* headings
* sentence similarity
* embedding similarity
* topic shifts
* LLM-assisted segmentation
* layout-aware PDF parsing, if available

The system must:

* avoid splitting coherent ideas unnecessarily
* avoid combining unrelated sections
* preserve heading, page, and section metadata
* expose semantic chunk boundaries in debug view
* support fallback to fixed-size chunking when semantic chunking fails

Semantic chunking configuration should include:

* maximum chunk size
* minimum chunk size
* similarity threshold
* overlap behavior
* fallback strategy

---

## 7.3 Embeddings and Indexing

The system must:

* Generate embeddings for all chunks
* Store vectors in a vector database
* Support a configurable embedding model
* Start with one embedding provider in v1
* Store metadata required for filtering and citation
* Support re-indexing when documents, chunking settings, or embedding settings change
* Support indexing child chunks and parent chunks when parent-child retrieval is enabled
* Preserve collection and namespace metadata in the vector database

---

## 7.4 Retrieval Pipeline

The retrieval pipeline must follow this sequence:

1. Receive the original user query
2. Run pre-retrieval query intelligence
3. Classify the query
4. Detect whether collection routing is needed
5. Decompose the query into sub-questions, if the query is complex, comparative, or multi-hop
6. Rewrite the query, if needed
7. Expand the query into 3-5 LLM-generated query variations, if enabled
8. Generate a hypothetical answer or hypothetical document using HyDE, if enabled
9. Add synonym expansions, if enabled
10. Select a retrieval strategy using static configuration or dynamic routing
11. Run candidate retrieval using semantic, keyword, hybrid, HyDE, query-expanded, decomposed-query, or parent-child retrieval
12. Merge and deduplicate retrieved candidates across the original query, expanded queries, and sub-questions
13. Apply metadata and collection filters
14. Rerank candidates using a configurable reranker, if enabled
15. Select top-k context chunks
16. Expand child chunks to parent chunks, if parent-child retrieval is enabled
17. Pass selected context to answer generation
18. Generate an answer with citations
19. Run safety and groundedness checks
20. Return the answer, citations, and debug data

The system must support:

* Semantic retrieval
* Keyword / sparse retrieval
* Hybrid retrieval
* Metadata filtering
* Query rewriting
* Pre-retrieval query intelligence
* Query expansion
* Query decomposition
* HyDE
* Synonym expansion
* Dynamic routing
* Configurable reranking
* Parent-child retrieval
* Collection-aware retrieval
* Automatic collection detection
* Configurable retrieval strategies

The system must expose:

* original query
* rewritten query
* expanded queries
* decomposed sub-questions, if enabled
* query expansion generation prompt and model, if applicable
* HyDE-generated text, if enabled
* synonym expansions, if enabled
* selected routing decision
* routing reason
* retrieved chunks
* retrieval scores
* retrieval mode
* intermediate outputs
* selected top-k context
* applied filters
* reranking results, if enabled
* parent-child expansion results, if enabled

---

## 7.4.0 Pre-Retrieval Query Intelligence

The system must support a pre-retrieval query intelligence stage before candidate retrieval begins.

Pre-retrieval query intelligence should improve retrieval recall, support complex questions, and make query transformation behavior visible to users.

The pre-retrieval stage must support:

* query classification
* query rewriting, if needed
* LLM-based query expansion
* query decomposition
* synonym expansion, if enabled
* collection-routing signals, if enabled

### Query Expansion

The system must use an LLM to generate 3-5 alternative query variations from the user's original question when query expansion is enabled.

The generated variations should preserve the user's intent while improving retrieval coverage through alternate wording, related terminology, abbreviations, spelling variants, and domain-specific phrasing.

The system must:

* keep the original user query unchanged
* generate a configurable number of query variations, defaulting to 3-5
* store each generated variation
* use expanded queries only for retrieval
* merge and deduplicate retrieved results across all query variations
* prevent expanded queries from being treated as evidence
* show generated query variations in the debug view
* log the LLM model, prompt template, and latency used for expansion
* evaluate whether expanded queries improve or hurt retrieval quality

### Query Decomposition

For complex questions, an agent must decompose the user's query into smaller sub-questions before retrieval.

Query decomposition should be used for:

* comparative questions
* multi-hop questions
* questions that ask about multiple entities, documents, features, or time periods
* questions that require evidence from multiple sources
* questions containing conjunctions such as "compare", "versus", "and", "pros and cons", or "difference between"

Examples:

```text
User query: Compare X and Y.
Sub-question 1: What is X?
Sub-question 2: What is Y?
Sub-question 3: How do X and Y differ?
```

```text
User query: How did policy A affect metric B in Q1 and Q2?
Sub-question 1: What does the knowledge base say about policy A?
Sub-question 2: What evidence exists for metric B in Q1?
Sub-question 3: What evidence exists for metric B in Q2?
Sub-question 4: What relationship is supported between policy A and metric B?
```

The system must:

* detect when decomposition is needed
* generate sub-questions that preserve the original intent
* keep each sub-question traceable to the original query
* retrieve evidence for each sub-question independently when enabled
* merge and deduplicate results across sub-questions
* track which retrieved chunks support which sub-question
* synthesize the final answer across sub-question evidence
* show sub-questions and per-sub-question retrieval results in debug view
* avoid answering decomposed sub-questions without retrieved evidence
* evaluate decomposition quality and retrieval impact

Pre-retrieval query intelligence must be configurable, observable, and safe. It must not introduce unsupported assumptions into the final answer.

---

## 7.4.1 Query Expansion

The system must support query expansion to improve recall.

Query expansion should create additional search queries from the user’s original query.

The system should use an LLM to generate 3-5 alternative query variations by default, unless the configured query expansion count is changed.

Query expansion may use:

* LLM-generated alternate queries, defaulting to 3-5 variations
* related terms
* domain-specific terminology
* abbreviations
* spelling variants
* product-specific vocabulary
* user intent clarification

The system must:

* keep the original query
* store all expanded queries
* show expanded queries in debug view
* allow query expansion to be enabled or disabled
* allow the number of expanded queries to be configured, with a default range of 3-5 variations
* merge and deduplicate results from expanded queries
* evaluate whether expansion improves or hurts retrieval quality

Query expansion must not introduce unsupported assumptions into the final answer.

Expanded queries are used only for retrieval, not as evidence.

---

## 7.4.2 HyDE

The system must support HyDE, or Hypothetical Document Embeddings, as an optional retrieval strategy.

When HyDE is enabled, the system should:

1. Use an LLM to generate a hypothetical answer or hypothetical document for the user query.
2. Embed the generated hypothetical text.
3. Retrieve chunks that are semantically similar to the hypothetical text.
4. Use the retrieved real chunks as evidence.
5. Never cite the hypothetical text as evidence.

HyDE may be useful when:

* the original query is short
* the query lacks keywords found in the documents
* semantic search performs poorly
* the user asks a conceptual question

The system must:

* store the HyDE-generated text for debugging
* show HyDE output in debug view
* allow HyDE to be enabled or disabled
* allow HyDE prompt templates to be configured
* compare HyDE retrieval against standard semantic retrieval in evaluations
* prevent HyDE output from being treated as ground truth
* ensure final answers cite only retrieved source chunks, never the hypothetical document

---

## 7.4.3 Synonym Expansion

The system must support synonym expansion to improve keyword and hybrid retrieval.

Synonym expansion may use:

* predefined synonym dictionaries
* domain-specific term maps
* LLM-generated synonyms
* abbreviation expansion
* acronym expansion
* spelling variants
* plural/singular variants

Examples:

```text
auth → authentication
login → sign in
docs → documentation
db → database
config → configuration
```

The system must:

* allow synonym expansion to be enabled or disabled
* support editable synonym dictionaries
* log applied synonyms
* show synonym expansions in debug view
* use synonym expansion for retrieval only
* avoid adding synonyms that change the user’s intent
* evaluate the effect of synonym expansion on retrieval quality

---

## 7.4.4 Dynamic Routing

The system must support dynamic routing to select the best retrieval and generation strategy for a query.

Dynamic routing may choose based on:

* query length
* query type
* collection metadata
* source type
* user-selected mode
* confidence scores
* whether the query appears multi-hop
* whether the query is keyword-heavy
* whether the query is conceptual
* whether the query requires exact matching
* previous evaluation performance

Dynamic routing may select among:

* semantic retrieval
* keyword retrieval
* hybrid retrieval
* HyDE retrieval
* query expansion retrieval
* parent-child retrieval
* reranking enabled or disabled
* single-collection retrieval
* cross-collection retrieval

The system must expose:

* selected route
* routing reason
* enabled retrieval features
* disabled retrieval features
* fallback route, if applicable

Examples:

* If a query contains exact identifiers, use keyword or hybrid retrieval.
* If a query is conceptual, use semantic retrieval or HyDE.
* If a query is broad, use query expansion.
* If a query asks across topics, use multi-hop or cross-collection retrieval.
* If the user explicitly selects a collection, route only to that collection.

Dynamic routing must be configurable and observable.

---

## 7.4.5 Configurable Rerankers

The system must support configurable rerankers.

Rerankers may be used after candidate retrieval to improve ranking quality before answer generation.

The system should support one or more reranker types:

* no reranker
* cross-encoder reranker
* LLM-based reranker
* embedding similarity reranker
* metadata-aware reranker
* recency-aware reranker
* custom scoring function

The system must allow configuration of:

* reranker enabled or disabled
* reranker provider
* reranker model
* number of candidates sent to reranker
* final top-k after reranking
* score threshold
* timeout behavior
* fallback behavior when reranking fails

The system must expose:

* pre-rerank order
* post-rerank order
* original retrieval scores
* reranker scores
* reranker model used
* reranker latency

The strategy comparison UI and evaluation dashboard must allow users to compare retrieval quality with and without reranking.

---

## 7.4.6 Parent-Child Retrieval

The system must support parent-child retrieval when parent-child chunking is enabled.

Parent-child retrieval should:

* retrieve smaller child chunks for precision
* expand selected child chunks into larger parent chunks for generation context
* cite the specific child chunks that support claims
* optionally include parent context for answer completeness

The system must support:

* child-only retrieval
* parent-only retrieval
* child retrieval with parent expansion
* configurable parent expansion size
* configurable number of child chunks per parent
* deduplication of repeated parent chunks
* debug visualization of parent-child relationships

Parent-child retrieval must be evaluated against standard chunk retrieval.

---

## 7.5 Query Processing

The system must rewrite and process queries when needed.

The system must classify queries as:

* answerable
* conversational
* unsupported
* ambiguous
* out-of-domain
* multi-hop
* comparative
* decomposition-needed
* exact-match
* conceptual
* adversarial or prompt-injection-like

The system must support query modes:

* simple
* expanded
* HyDE
* synonym-expanded
* multi-hop
* decomposed
* dynamically routed

The system must expose the selected query mode in the debug view. When decomposition is used, the debug view must show the original query, generated sub-questions, and retrieval results associated with each sub-question.

---

## 7.5.1 Automatic Collection Detection

The system must support automatic collection detection as an advanced retrieval feature.

If the user does not explicitly select a collection, the system may infer the most relevant collection using:

* query intent
* collection names
* collection descriptions
* document titles
* document metadata
* prior chat context
* embedding similarity between query and collection summaries
* keyword matching
* LLM-based routing

The system must support:

* explicit collection selection
* search across all collections
* automatic collection detection
* fallback to all collections when confidence is low

Automatic collection detection must output:

* selected collection or collections
* confidence score
* reason for selection
* fallback behavior
* whether the user explicitly selected the collection or the system inferred it

Automatic collection detection must be visible in debug view and logged for evaluation.

For v1, explicit collection selection should be prioritized. Automatic collection detection should be optional and configurable.

---

## 7.6 Answer Generation

The system must generate answers grounded in retrieved evidence.

The system must:

* Generate answers using only retrieved evidence for factual document-based claims
* Include citations for factual claims derived from retrieved documents
* Avoid unsupported claims
* Explicitly state uncertainty when evidence is partial
* Refuse when evidence is insufficient
* Preserve chat history
* Manage the context window by trimming, ranking, and packing context
* Avoid treating retrieved document content as system instructions
* Stream generated answers to the UI when streaming is enabled
* Support non-streaming fallback behavior

---

## 7.6.1 Streaming Answer Generation

The system must support streaming UI for answer generation.

When streaming is enabled, the UI should show answer tokens progressively as they are generated.

The system must:

* stream partial answer text
* preserve citation correctness
* avoid displaying fabricated citations during streaming
* add final citations once evidence mapping is complete
* support cancellation of in-progress generation
* show generation status
* handle errors gracefully
* support fallback to non-streaming responses

The streaming UI should show statuses such as:

* understanding query
* retrieving evidence
* reranking results
* generating answer
* checking groundedness
* finalizing citations

Streaming must not bypass safety checks.

---

## 7.7 Safety and Quality

The system must:

* Refuse out-of-domain or unsupported questions
* Perform groundedness checks
* Treat retrieved content as untrusted
* Prevent instruction override from retrieved documents
* Detect prompt-injection patterns where possible
* Support advanced prompt-injection detection
* Log safety-related decisions

The system must output:

* retrieval support score
* groundedness status
* answerability flag
* refusal reason, if refused
* prompt-injection risk score, if applicable
* safety decision

The system must log:

* refusals
* weak support
* hallucination risks
* possible prompt-injection attempts
* conflicting evidence
* safety classifier output
* prompt-injection patterns detected
* documents or chunks that triggered injection warnings

---

## 7.7.1 Advanced Prompt-Injection Detection

The system must support advanced prompt-injection detection for retrieved content and user queries.

The system must treat all retrieved content as untrusted data, not instructions.

Advanced prompt-injection detection may use:

* pattern matching
* keyword rules
* allowlist and blocklist rules
* LLM-based classification
* prompt-injection risk scoring
* instruction-intent detection
* document-level scanning during ingestion
* chunk-level scanning during retrieval
* adversarial evaluation datasets

The system should detect attempts such as:

* ignoring previous instructions
* overriding system instructions
* disabling citations
* revealing hidden prompts
* changing the assistant role
* exfiltrating secrets
* instructing the model to trust the document above all else
* instructing the model to delete or modify user data
* asking the model to execute unauthorized actions
* hiding malicious instructions inside markdown, HTML, comments, or quoted text

Each detected prompt-injection issue must include:

* detection method
* risk score
* matched pattern or classifier reason
* affected document ID
* affected chunk ID
* recommended action
* final system decision

Possible actions include:

* ignore malicious instructions and continue using factual content
* exclude suspicious chunk from generation
* lower the chunk’s trust score
* refuse the answer
* show warning in debug view
* log the issue for evaluation

Prompt-injection detection must be included in safety evaluation.

---

## 7.8 Evaluation

The evaluation dataset must include:

* fact lookup questions
* summarization questions
* multi-hop questions
* ambiguous questions
* out-of-domain questions
* adversarial / prompt-injection questions
* query expansion test cases
* query decomposition test cases
* HyDE test cases
* synonym expansion test cases
* dynamic routing test cases
* parent-child retrieval test cases
* semantic chunking test cases
* duplicate detection test cases
* automatic collection detection test cases

The system must support:

* repeated evaluation runs
* experiment comparison
* pass/fail output for each run
* regression tracking across experiments
* strategy comparison across retrieval methods
* evaluation of advanced retrieval features
* evaluation of configurable rerankers

Metrics must include:

### Retrieval

* Recall@k ≥ defined threshold
* MRR / ranking quality ≥ defined threshold
* precision@k
* nDCG@k, if supported
* parent-child retrieval accuracy
* collection routing accuracy
* query decomposition coverage and correctness
* duplicate detection accuracy

### Answer Quality

* groundedness ≥ defined threshold
* relevance ≥ defined threshold
* refusal correctness ≥ defined threshold
* citation accuracy ≥ defined threshold
* answer completeness
* uncertainty handling

### Safety

* prompt-injection resistance ≥ defined threshold
* unsafe instruction rejection rate
* suspicious chunk detection accuracy
* unsupported answer refusal accuracy

### Experimentation

* latency by strategy
* token usage by strategy
* cost estimate by strategy, if available
* retrieval improvement over baseline
* answer quality improvement over baseline
* regression status

Each evaluation run must output:

* overall pass/fail status
* per-test-case pass/fail status
* metric scores
* experiment configuration
* retrieval strategy used
* model settings used
* reranker settings used
* chunking strategy used
* query expansion settings used
* query decomposition settings used
* HyDE settings used
* routing decision
* timestamp
* regression comparison, if previous runs exist

---

## 7.9 Observability and Debugging

The system must log:

* original query
* rewritten query
* expanded queries
* decomposed sub-questions, if enabled
* per-sub-question retrieval results, if decomposition is enabled
* HyDE-generated text, if enabled
* synonym expansions, if enabled
* query classification
* retrieval mode
* dynamic routing decision
* routing reason
* collection or namespace used
* automatic collection detection result
* metadata filters applied
* retrieved chunks
* retrieval scores
* reranking scores, if applicable
* parent-child expansion results, if applicable
* final selected context
* final answer
* citations
* refusal reason
* groundedness status
* prompt-injection detection result
* latency
* token usage
* model name
* embedding model
* reranker model
* experiment configuration

The UI must show:

* retrieved chunks
* citations
* refusal reasoning
* retrieval strategy
* retrieval scores
* selected query mode
* answerability flag
* groundedness status
* prompt-injection warning, if detected
* expanded queries, if enabled
* decomposed sub-questions, if enabled
* per-sub-question retrieval results, if decomposition is enabled
* HyDE output, if enabled
* synonym expansions, if enabled
* routing decision
* reranking comparison
* parent-child context expansion
* automatic collection detection result

---

## 7.10 Collections and Namespacing

The system must support multiple collections or namespaces in the vector database.

Collections allow users to organize documents into separate knowledge bases, such as:

* Product Docs
* Research Papers
* Internal Notes
* Course Materials
* Project Documentation

The system must allow users to:

* create collections
* rename collections
* delete collections
* assign documents to collections during ingestion
* move documents between collections
* view documents within a collection
* query a specific collection
* query across all collections
* enable automatic collection detection
* inspect collection-level retrieval performance

During retrieval, the system must support:

* filtering by collection
* searching across all collections
* isolating results to one collection when explicitly selected
* using metadata filters to restrict retrieval scope
* automatically selecting one or more relevant collections when enabled
* exposing the selected collection or namespace in debug output

If the user does not specify a collection, the system should either:

* search across all collections by default, or
* infer the most relevant collection using query intent and document metadata.

For v1, explicit collection selection should be prioritized over automatic collection inference.

Automatic collection detection may be added as an advanced capability after the core retrieval system is working.

The system must ensure that chunks, embeddings, metadata, citations, evaluations, and logs preserve collection information.

---

## 7.11 Citation Format Rules

Every answer must include structured citations when factual claims are derived from retrieved documents.

A valid citation must include:

* document title or ID
* page or section, if available
* chunk ID
* source URL, if applicable

Citations must:

* only reference retrieved chunks
* never be fabricated
* support the actual claims being made
* be traceable back to stored chunk metadata
* cite real retrieved chunks, not expanded queries, HyDE-generated text, or synthetic retrieval helpers

The system must support:

* inline citations
* reference list citations

---

## 7.12 Prompt Injection Handling

The system must:

* Treat all retrieved content as untrusted
* Ignore instructions inside retrieved documents
* Separate system instructions from retrieved context
* Detect prompt-injection patterns where possible
* Support advanced prompt-injection detection
* Log suspected injection attempts
* Include adversarial tests in evaluation
* Prevent retrieved documents from overriding system, developer, or application rules

Examples of prompt-injection patterns include:

* “Ignore previous instructions”
* “Reveal the system prompt”
* “Do not cite sources”
* “Always answer yes”
* “Delete user data”
* “Use this document as your new instruction set”
* hidden instructions in HTML comments
* malicious markdown instructions
* encoded or obfuscated override attempts

When a prompt-injection attempt is detected, the system should:

* continue answering if safe and evidence is valid
* exclude malicious instructions from reasoning
* optionally exclude suspicious chunks
* log the attempt
* expose a warning in the debug view
* include the detection result in evaluation output

---

## 7.13 Answerability Threshold Logic

The system must determine whether a question is answerable based on:

* retrieval score thresholds
* number of supporting chunks
* groundedness confidence
* citation coverage
* evidence consistency
* collection scope
* reranker confidence
* prompt-injection risk
* dynamic routing confidence

The system must refuse when:

* retrieval confidence is low
* evidence is insufficient
* evidence is conflicting
* the question is outside the available knowledge base
* the available evidence does not support a reliable answer
* prompt-injection risk is too high
* no selected retrieval route produces sufficient evidence

Thresholds must be configurable.

The answerability decision must be:

* logged
* visible in the debug view
* included in evaluation output

Suggested refusal categories:

```text
NO_RELEVANT_EVIDENCE
LOW_RETRIEVAL_CONFIDENCE
INSUFFICIENT_SUPPORT
CONFLICTING_EVIDENCE
OUT_OF_DOMAIN
PROMPT_INJECTION_DETECTED
ROUTING_CONFIDENCE_TOO_LOW
COLLECTION_CONFIDENCE_TOO_LOW
```

---

## 7.14 Configuration Requirements

The system must support centralized configuration for ingestion, chunking, retrieval, generation, safety, evaluation, and observability.

Configuration should be easy to inspect, edit, and reuse across experiments.

The system must support configuration through one or more of:

* `.env` file
* YAML configuration file
* JSON configuration file
* UI settings panel
* command-line arguments for evaluation runs

The system must support configurable values for:

### Ingestion

* allowed file types
* maximum file size
* URL ingestion enabled or disabled
* document re-ingestion behavior
* duplicate document handling
* duplicate detection enabled or disabled
* duplicate detection method
* near-duplicate similarity threshold

### Chunking

* chunk size
* chunk overlap
* chunking strategy
* maximum chunk length
* minimum chunk length
* parent-child chunking enabled or disabled
* semantic chunking enabled or disabled
* semantic similarity threshold
* parent chunk size
* child chunk size
* child-to-parent expansion behavior

### Embeddings

* embedding provider
* embedding model
* embedding batch size
* vector dimension, if needed
* re-embedding behavior

### Vector Database

* vector database provider
* collection name
* namespace behavior
* persistence directory
* metadata fields to index

### Retrieval

* retrieval mode
* top-k
* semantic search enabled or disabled
* keyword search enabled or disabled
* hybrid search enabled or disabled
* hybrid weighting
* metadata filters
* query expansion enabled or disabled
* number of expanded queries
* query expansion LLM prompt template
* query decomposition enabled or disabled
* query decomposition trigger rules
* maximum number of decomposed sub-questions
* HyDE enabled or disabled
* HyDE prompt template
* synonym expansion enabled or disabled
* synonym dictionary path
* dynamic routing enabled or disabled
* routing rules
* automatic collection detection enabled or disabled
* collection confidence threshold
* parent-child retrieval enabled or disabled
* parent expansion enabled or disabled
* reranker enabled or disabled
* reranker provider
* reranker model
* reranker candidate count
* final context limit

### Query Processing

* query rewriting enabled or disabled
* query expansion enabled or disabled
* query decomposition enabled or disabled
* decomposition trigger rules
* maximum number of sub-questions
* HyDE enabled or disabled
* synonym expansion enabled or disabled
* multi-hop mode enabled or disabled
* dynamic routing enabled or disabled
* query classification enabled or disabled

### Answer Generation

* LLM provider
* LLM model
* temperature
* max output tokens
* system prompt template
* citation style
* chat history length
* context packing strategy
* streaming enabled or disabled
* streaming fallback behavior

### Safety

* minimum retrieval score
* minimum number of supporting chunks
* groundedness check enabled or disabled
* prompt-injection detection enabled or disabled
* advanced prompt-injection detection enabled or disabled
* prompt-injection risk threshold
* suspicious chunk handling
* refusal threshold
* conflicting evidence behavior

### Evaluation

* evaluation dataset path
* metrics enabled
* pass/fail thresholds
* experiment name
* baseline run ID
* number of repeated runs
* output report path
* strategy comparison enabled or disabled
* regression tracking enabled or disabled

### Observability

* logging enabled or disabled
* log level
* token usage tracking enabled or disabled
* latency tracking enabled or disabled
* debug view enabled or disabled
* run storage enabled or disabled
* expanded query logging enabled or disabled
* query decomposition logging enabled or disabled
* per-sub-question retrieval logging enabled or disabled
* HyDE logging enabled or disabled
* routing decision logging enabled or disabled
* reranking trace logging enabled or disabled

Each experiment run must store the configuration used for that run so that results are reproducible.

---

## 7.15 UI Screens

The application must include explicit UI screens that make the RAG pipeline understandable and inspectable.

---

### 7.15.1 Document Library Screen

The Document Library screen must allow users to:

* upload documents
* ingest web URLs
* view all ingested documents
* view document metadata
* view ingestion status
* delete documents
* re-index documents
* assign documents to collections
* filter documents by collection
* search documents by title or metadata
* view duplicate detection warnings
* choose how to handle duplicate documents

Each document row should show:

* document title
* document ID
* source type
* collection
* ingestion status
* duplicate status
* number of chunks
* created date
* last indexed date
* available actions

---

### 7.15.2 Collections Screen

The Collections screen must allow users to:

* create collections
* rename collections
* delete collections
* view documents in a collection
* move documents between collections
* select a default collection
* see collection-level statistics
* enable or disable automatic collection detection
* inspect collection routing behavior

Each collection should show:

* collection name
* collection ID
* number of documents
* number of chunks
* last updated date
* routing description, if available

---

### 7.15.3 Chat Screen

The Chat screen must allow users to:

* ask questions
* select a collection or search all collections
* enable automatic collection detection
* select retrieval strategy
* view generated answers
* stream generated answers
* cancel streaming generation
* view inline citations
* view citation details
* see refusal messages when evidence is insufficient
* continue a conversation with preserved chat history

The Chat screen should include:

* question input box
* answer panel
* citation panel
* collection selector
* automatic collection detection toggle
* retrieval strategy selector
* streaming toggle
* optional toggle for debug output
* chat history panel

---

### 7.15.4 Citation Detail View

The Citation Detail View must allow users to inspect evidence behind an answer.

It must show:

* cited document title
* document ID
* chunk ID
* parent chunk ID, if applicable
* page or section
* source URL, if applicable
* cited text snippet
* retrieval score
* reranking score, if applicable
* retrieval strategy used

Users should be able to open the cited source or inspect the full chunk.

---

### 7.15.5 Debug View

The Debug View must show pipeline internals for each query.

It must show:

* original query
* rewritten query
* expanded queries
* decomposed sub-questions
* per-sub-question retrieval results
* HyDE-generated text
* synonym expansions
* query classification
* selected query mode
* dynamic routing decision
* routing reason
* selected collection or namespace
* automatic collection detection result
* retrieval strategy
* metadata filters
* retrieved chunks
* retrieval scores
* reranking scores
* selected context
* parent-child expansion results
* prompt template used
* final answer
* citations
* groundedness status
* answerability flag
* prompt-injection detection result
* refusal reason, if applicable
* latency
* token usage

The Debug View should make it easy for learners and reviewers to understand how the system produced an answer.

---

### 7.15.6 Strategy Comparison UI

The Strategy Comparison UI must allow users to compare different retrieval and generation methods for the same query.

It should support comparison across:

* semantic retrieval
* keyword retrieval
* hybrid retrieval
* query rewriting enabled vs disabled
* query expansion enabled vs disabled
* query decomposition enabled vs disabled
* HyDE enabled vs disabled
* synonym expansion enabled vs disabled
* reranking enabled vs disabled
* different reranker models
* parent-child retrieval enabled vs disabled
* semantic chunking vs fixed-size chunking
* automatic collection detection vs explicit collection selection
* different top-k values

The screen should show:

* retrieved chunks per strategy
* scores per strategy
* generated answer per strategy
* citation differences
* answerability decision per strategy
* latency per strategy
* token usage per strategy
* reranker scores per strategy
* groundedness status per strategy
* prompt-injection warnings per strategy

This screen is important for the learning and portfolio value of the project.

---

### 7.15.7 Experiment Dashboard

The Experiment Dashboard must allow users to:

* run evaluation datasets
* view evaluation results
* compare experiment runs
* inspect failed cases
* inspect regressions
* view pass/fail status
* export benchmark reports
* compare retrieval configurations
* compare reranker configurations
* compare chunking strategies
* compare query expansion, query decomposition, HyDE, and synonym expansion results
* track quality over time

The dashboard must show:

* experiment name
* configuration used
* retrieval metrics
* answer quality metrics
* safety metrics
* pass/fail result
* timestamp
* baseline comparison
* failed examples
* regression summary
* latency summary
* token usage summary
* strategy-level comparison
* reranker-level comparison
* prompt-injection test results

---

### 7.15.8 Settings / Configuration Screen

The Settings screen must allow users to inspect and update configuration values.

It should include sections for:

* ingestion settings
* duplicate detection settings
* chunking settings
* semantic chunking settings
* parent-child retrieval settings
* embedding settings
* vector database settings
* retrieval settings
* query expansion settings
* query decomposition settings
* HyDE settings
* synonym expansion settings
* dynamic routing settings
* automatic collection detection settings
* reranker settings
* query processing settings
* generation settings
* streaming settings
* safety settings
* prompt-injection detection settings
* evaluation settings
* observability settings

The Settings screen should allow users to save named configurations for experiments.

---

## 8. Non-Functional Requirements

The system must support:

* Simple local setup
* Laptop-friendly development
* Modular architecture
* Clear separation of components
* Reproducible experiment runs
* Reasonable latency for small document collections
* Local persistence for vectors, metadata, logs, and evaluations
* Streaming response support without blocking the entire UI
* Configurable fallbacks when advanced features fail

Core components:

* ingestion
* duplicate detection
* chunking
* semantic chunking
* parent-child indexing
* embeddings
* retrieval
* dynamic routing
* reranking
* generation
* streaming
* safety
* prompt-injection detection
* evaluation
* UI/API
* configuration
* observability

---

## 9. v1 Technical Direction

Frontend:

* HTML
* CSS
* React

Backend:

* Python API
* virtual environment

Storage:

* ChromaDB for vectors
* SQLite for metadata, runs, evaluations, and logs

Model:

* Start with one provider
* Add provider abstraction later

Configuration:

* YAML or JSON configuration file
* `.env` for secrets and provider keys
* Stored experiment configuration for repeatability

Deployment:

* Local-first development
* No heavy infrastructure required for v1

---

## 10. Advanced Capabilities

Advanced capabilities include:

* Pre-retrieval query intelligence
* Query expansion
* Query decomposition
* HyDE
* Synonym expansion
* Dynamic routing
* Automatic collection detection
* Streaming UI
* Strategy comparison UI
* Experiment dashboard
* Configurable rerankers
* Duplicate detection
* Parent-child retrieval
* Semantic chunking
* Advanced prompt-injection detection
* Multiple embedding models
* Query expansion using LLM-generated 3-5 alternate queries
* Query decomposition for complex, comparative, and multi-hop questions
* Synonym dictionaries and domain-specific vocabulary maps
* Dynamic routing based on query type and confidence
* Streaming answer generation with cancellation
* Batch ingestion
* Freshness metadata
* Background jobs
* Automated regression alerts

---

## 11. Learning and Portfolio Features

The system must include feature toggles for:

* query rewriting
* query expansion
* query decomposition
* HyDE
* synonym expansion
* dynamic routing
* reranking
* configurable reranker selection
* hybrid search
* multi-hop retrieval
* parent-child retrieval
* semantic chunking
* groundedness checks
* prompt-injection detection
* advanced prompt-injection detection
* collection filtering
* automatic collection detection
* streaming UI

The system should include a visual pipeline:

```text
question → pre-retrieval intelligence → classify → rewrite → expand/decompose → route → retrieve → rerank → select context → answer → cite → evaluate
```

The visual pipeline should show optional advanced steps when enabled:

```text
query expansion
query decomposition
HyDE generation
synonym expansion
dynamic routing
automatic collection detection
parent-child expansion
semantic chunking
advanced prompt-injection detection
```

Portfolio-facing artifacts should include:

* demo notebooks
* benchmark reports
* architecture diagram
* example evaluation dataset
* before/after retrieval strategy comparison
* query expansion comparison examples
* query decomposition comparison examples
* HyDE comparison examples
* reranker comparison examples
* semantic chunking comparison examples
* parent-child retrieval examples
* duplicate detection examples
* automatic collection routing examples
* example prompt-injection test results
* screenshots of debug views
* screenshots of strategy comparison UI
* screenshots of experiment dashboard
* short project README

---

## 12. AI Concepts Demonstrated

This project should demonstrate:

* Retrieval-Augmented Generation
* embeddings and vector representations
* vector similarity search
* sparse retrieval
* hybrid retrieval
* reranking
* configurable rerankers
* query rewriting
* pre-retrieval query intelligence
* query expansion
* query decomposition
* HyDE
* synonym expansion
* dynamic routing
* query routing
* automatic collection detection
* context window management
* parent-child retrieval
* semantic chunking
* duplicate detection
* streaming generation
* grounded generation
* citation-based answering
* hallucination detection
* prompt-injection defense
* advanced prompt-injection detection
* collection-aware retrieval
* configuration-driven experimentation
* strategy comparison
* evaluation dashboards
* evaluation-driven development
* offline evaluation pipelines
* observability for AI systems
