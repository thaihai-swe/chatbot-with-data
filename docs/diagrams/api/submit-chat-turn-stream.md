# API Flow: POST /chat/sessions/{id}/turns/stream

```mermaid
sequenceDiagram
    participant Frontend
    participant Orchestrator as StreamingOrchestrator
    participant SafetyService
    participant AdvancedRetrievalService
    participant Weaviate
    participant GroundingService
    participant OpenAI as OpenAI (GPT-4o)
    participant DB as SQLite
    
    Frontend->>Orchestrator: POST /chat/sessions/{id}/turns/stream
    
    Orchestrator->>SafetyService: check_query
    SafetyService-->>Orchestrator: Safe
    
    rect rgb(240, 240, 240)
        Note right of Orchestrator: Retrieval Loop
        Orchestrator->>AdvancedRetrievalService: retrieve
        AdvancedRetrievalService->>Weaviate: query_hybrid
        Weaviate-->>AdvancedRetrievalService: Relevant chunks
        AdvancedRetrievalService-->>Orchestrator: Chunks + Trace
    end
    
    Orchestrator->>SafetyService: check_chunks
    SafetyService-->>Orchestrator: Filtered Safe Chunks
    
    Orchestrator->>GroundingService: evaluate_evidence
    GroundingService-->>Orchestrator: Sufficient
    
    Orchestrator->>OpenAI: chat_completions(stream=True)
    
    loop For each token
        OpenAI-->>Orchestrator: Token
        Orchestrator-->>Frontend: SSE event: token
    end
    
    Orchestrator->>GroundingService: calculate_groundedness
    GroundingService-->>Orchestrator: Score
    
    Orchestrator->>DB: Store Turn & Trace
    
    Orchestrator-->>Frontend: SSE event: complete
```
