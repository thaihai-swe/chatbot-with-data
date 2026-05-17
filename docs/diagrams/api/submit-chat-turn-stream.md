# API Flow: POST /chat/sessions/{id}/turns/stream

```mermaid
sequenceDiagram
    participant Frontend
    participant Router as Router (chat.py)
    participant StreamingOrchestrator
    participant SafetyService
    participant AdvancedRetrievalService
    participant ChromaDB
    participant GroundingService
    participant LLM
    
    Frontend->>Router: POST /chat/sessions/{id}/turns/stream
    Router->>StreamingOrchestrator: start_stream(session_id, message)
    Router-->>Frontend: SSE Event Stream established
    
    StreamingOrchestrator->>SafetyService: check_query(message)
    SafetyService-->>StreamingOrchestrator: SafetyTrace
    
    alt Unsafe Query
        StreamingOrchestrator-->>Frontend: Stream Refusal Tokens
        StreamingOrchestrator-->>Frontend: Event: done
    else Safe Query
        par Retrieval and Safety
            StreamingOrchestrator->>AdvancedRetrievalService: retrieve(message)
            AdvancedRetrievalService->>ChromaDB: query_vectors
            ChromaDB-->>AdvancedRetrievalService: Relevant chunks
            AdvancedRetrievalService-->>StreamingOrchestrator: Chunks + RetrievalTrace
            
            StreamingOrchestrator->>SafetyService: check_chunks(chunks)
            SafetyService-->>StreamingOrchestrator: Safe chunks
        end
        
        StreamingOrchestrator->>GroundingService: evaluate_evidence(safe_chunks)
        GroundingService-->>StreamingOrchestrator: is_sufficient?
        
        alt Insufficient Evidence
            StreamingOrchestrator-->>Frontend: Stream Refusal Tokens
            StreamingOrchestrator-->>Frontend: Event: done
        else Sufficient Evidence
            StreamingOrchestrator->>LLM: stream_generation(message, context)
            LLM-->>StreamingOrchestrator: Tokens
            StreamingOrchestrator-->>Frontend: Event: token
            
            StreamingOrchestrator-->>Frontend: Event: citations (+ Traces)
            StreamingOrchestrator-->>Frontend: Event: done
        end
    end
```
