# Comprehensive System End-to-End Flow

This document provides a detailed map of all workflows within the RAG Knowledge Base Lab, covering Knowledge Ingestion, Management, Advanced Retrieval, and Grounded Chat.

---

## 1. System Architecture & Data Storage

The system utilizes a dual-storage strategy to balance complex metadata management with high-performance vector search.

### A. Metadata & Cache Store (SQLite)
**Location:** `backend/data/knowledge_base.db` (configured via `DATABASE_PATH`)

SQLite is the primary source of truth for all relational data and serves as a high-speed cache for expensive LLM operations.

| Table | Details & Data Stored |
| :--- | :--- |
| **Collections** | Logical namespaces; Stores `name`, `description`, `is_default`, and `routing_enabled`. |
| **Documents** | File/URL metadata; Stores `title`, `source_type`, `file_hash`, `normalized_text_hash`, and the full `extracted_text`. |
| **Chunks** | Atomic text units; Stores the `text` snippet, `chunk_order`, `strategy` used, and hierarchical links (`parent_chunk_id`). |
| **Embeddings** | **Cache Layer**; Stores the raw `embedding_vector` as a JSON array and an `input_text_hash`. This allows the system to skip OpenAI API calls if the text has not changed. |
| **Index Entries** | The "Glue"; Maps `chunk_id` to `embedding_id` and `vector_db_id` for consistent retrieval across re-indexing generations. |
| **Chat Sessions** | Stores session state and the selected `collection_ids` scope. |
| **Chat Turns** | Full query history; Stores `query_text`, `answer_text`, `groundedness_score`, and `safety_trace`. |
| **Citations** | Grounding evidence; Links specific chat turns to chunks with `quote_text` and metadata. |

### B. Vector Store (ChromaDB)
**Location:** `data/.chroma_db` (configured via `CHROMA_PERSIST_DIR`)

ChromaDB is optimized for Approximate Nearest Neighbor (ANN) search. It stores minimal data to remain fast and lightweight.

- **Vectors:** 1536-dimensional embeddings (OpenAI `text-embedding-3-small`).
- **Metadata (in Chroma):** 
    - `chunk_id`: UUID for joining with SQLite.
    - `document_id`: For document-level filtering.
    - `collection_id`: For rapid collection-scoped search.
    - `chunk_order`: To support neighbor lookups and parent-child expansion.
    - `page_number` / `section_title`: For rapid citation display before SQLite join.

---

## 2. Core Workflows

### A. Knowledge Ingestion & Duplicate Handling
Transforms raw data into indexed chunks with collision detection.

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant I as IngestionService
    participant E as Extractor
    participant D as DuplicateDetector
    participant C as ChunkingService
    participant V as IndexingService
    participant DB as SQLite
    participant CH as ChromaDB

    U->>F: Upload File / Submit URL
    F->>I: POST /ingestion/file-upload
    I->>DB: Create Ingestion Attempt (SUBMITTED)
    I-->>F: 202 Accepted (Attempt ID)

    Note right of I: Background Task Starts
    I->>E: extract(artifact_path)
    E-->>I: {text, metadata, hashes, title}
    I->>D: detect(candidate, existing_docs)
    
    alt Duplicate Detected
        I->>DB: Status: AWAITING_USER_ACTION
        U->>F: Review Decision (Replace/Version/Skip)
        F->>I: POST /duplicate-decision
    else Unique
        I->>I: Proceed automatically
    end

    I->>DB: Create/Update Document Record
    I->>C: chunk_document(document_id)
    C->>DB: Store Chunks in SQLite
    I->>V: index_document(document_id)
    V->>DB: Check Cache / Create Embeddings (OpenAI)
    V->>CH: add_vectors(embeddings, metadata)
    I->>DB: Status: COMPLETED
```

---

### B. Advanced Retrieval Flow
Intelligent query processing to maximize recall and precision.

1.  **Intent Classification:** LLM determines if the query is simple, complex (multi-step), or requires specific collection routing.
2.  **Query Expansion:** Generates 3-5 variations of the query to overcome semantic gaps.
3.  **HyDE (Hypothetical Document Embeddings):** Generates a synthetic answer to use as a "perfect" query vector.
4.  **Parallel Vector Search:** Executes all expanded queries against ChromaDB in parallel.
5.  **RRF (Reciprocal Rank Fusion):** Merges results from multiple retrieval strategies into a single ranked list.
6.  **Cross-Encoder Reranking:** A secondary LLM pass to re-score the top 20 candidates for maximum relevance.
7.  **Parent-Child Expansion:** Retrieves small chunks (e.g., 200 tokens) for precision but expands them to "parent" chunks (e.g., 1000 tokens) before sending to the LLM to provide broader context.

```mermaid
graph TD
    Q[User Query] --> Classify{Intent Classification}
    
    Classify -- Hybrid --> Expand[Query Expansion: 3-5 Variations]
    Classify -- Complex --> Decompose[Query Decomposition: Sub-questions]
    Classify -- Simple --> Baseline[Baseline Retrieval]

    Expand --> MultiSearch[Parallel Vector Search]
    Decompose --> MultiSearch
    Baseline --> MultiSearch
    
    Q --> HyDE[HyDE: Generate Hypothetical Answer]
    HyDE --> MultiSearch

    MultiSearch --> RRF[Reciprocal Rank Fusion]
    RRF --> Rerank[Cross-Encoder Reranking]
    Rerank --> PC[Parent-Child Expansion]
    PC --> Final[Final Grounding Context]
```

---

### C. Grounded Question-to-Answer Logical Workflow
The decision logic and processing steps for generating a safe, grounded response.

```mermaid
flowchart TD
    Start([User submits Question]) --> Safety1{Query Safety Check}
    
    Safety1 -- Malicious --> Refuse1[Generate Safety Refusal]
    Safety1 -- Safe --> Retrieval[Advanced Retrieval Flow]
    
    Retrieval --> Safety2{Chunk Safety Filtering}
    Safety2 --> FilteredChunks[Remove Risk Chunks]
    
    FilteredChunks --> Grounding1{Is evidence sufficient?}
    
    Grounding1 -- No --> Refuse2[Generate Grounding Refusal]
    Grounding1 -- Yes --> Context[Assemble Context Package]
    
    Context --> DB_Generating[Update Turn Status: Generating]
    DB_Generating --> Gen[LLM Generation: GPT-4o]
    
    Gen --> PostGrounding{Verify Groundedness}
    PostGrounding --> Citations[Extract & Map Citations]
    
    Citations --> DB_Done[Store Citations & Update Turn: Completed]
    DB_Done --> End([Deliver Answer + Traces])
    
    Refuse1 --> DB_Done
    Refuse2 --> DB_Done
```

---

### D. Grounded Question-to-Answer Sequence
Detailed interaction between components during the chat lifecycle.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant O as ChatService / StreamingOrchestrator
    participant S as SafetyService
    participant R as AdvancedRetrievalService
    participant G as GroundingService
    participant C as ContextService
    participant L as LLM (OpenAI GPT-4o)
    participant CIT as CitationService
    participant DB as SQLite

    U->>O: Submit Question
    O->>S: check_query(text)
    alt High Risk (Injection)
        S-->>O: Flag: Unsafe
        O->>DB: Log Refusal Turn
        O-->>U: "I cannot answer this question."
    end

    O->>R: retrieve(query, config, collections)
    Note right of R: Multi-strategy: HyDE, Expansion, RRF
    R-->>O: Raw Chunks + RetrievalTrace

    O->>S: check_chunks(chunks)
    Note right of S: Filter Malicious Context (Indirect Injection)
    S-->>O: Safe Chunks

    O->>G: evaluate_evidence(safe_chunks)
    alt Insufficient Information
        G-->>O: Flag: Unsupported
        O->>DB: Log Grounding Failure Turn
        O-->>U: "I don't have enough information."
    end

    O->>C: assemble_context(query, chunks, history)
    Note right of C: Format: System Prompt + XML Context + History
    C-->>O: Context Package

    O->>DB: Create Turn (Status: Generating)

    par Stream or Block
        O->>L: generate_answer(context)
        L-->>O: Response Tokens
        O-->>U: Streaming SSE Events (event: token)
    end

    O->>G: calculate_groundedness(answer, chunks)
    G-->>O: NLI Score (0.0 - 1.0)

    O->>CIT: extract_citations(answer)
    CIT->>CIT: map_citations_to_chunks(labels, chunks)
    CIT-->>O: Valid Citations

    O->>DB: Store Citations & Update Turn (Status: Completed)
    O-->>U: Final SSE Event (event: citations + Traces)
```

---

### E. Grounding & Citation Logic details

1.  **Citation Mapping:** The LLM is instructed to use `[n]` markers corresponding to the context chunks provided in the prompt.
2.  **Verification:** `CitationService` verifies that every `[n]` used in the answer actually exists in the retrieved set.
3.  **Traceability:** The system returns a "Retrieval Trace" (which chunks were found and why) and a "Safety Trace" (which safety filters were triggered).
4.  **Grounding Check:** 
    - **Pre-check:** `GroundingService` performs a rapid evaluation of the retrieved chunks against the query intent.
    - **Post-check:** `GroundingService` calculates a final groundedness score (0.0-1.0) using NLI (Natural Language Inference) logic between the generated answer and the source chunks.
