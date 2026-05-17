# API Flow: POST /chat/sessions/{id}/turns

```mermaid
sequenceDiagram
    participant Frontend
    participant Router as Router (chat.py)
    participant ChatService
    participant SafetyService
    participant AdvancedRetrievalService
    participant ChromaDB
    participant GroundingService
    participant LLM
    participant CitationService
    participant ChatRepository
    participant SQLite
    
    Frontend->>Router: POST /chat/sessions/{id}/turns (message)
    Router->>ChatService: process_turn(session_id, message)
    
    ChatService->>SafetyService: check_query(message)
    SafetyService-->>ChatService: SafetyTrace (is_answerable?)
    
    alt Unsafe Query
        ChatService->>ChatRepository: save_refusal
        ChatService-->>Router: Refusal JSON
    else Safe Query
        ChatService->>AdvancedRetrievalService: retrieve(message)
        AdvancedRetrievalService->>ChromaDB: query_vectors
        ChromaDB-->>AdvancedRetrievalService: Relevant chunks
        AdvancedRetrievalService-->>ChatService: Chunks + RetrievalTrace
        
        ChatService->>SafetyService: check_chunks(chunks)
        SafetyService-->>ChatService: Safe chunks
        
        ChatService->>GroundingService: evaluate_evidence(safe_chunks)
        GroundingService-->>ChatService: is_sufficient?
        
        alt Insufficient Evidence
            ChatService->>ChatRepository: save_refusal
            ChatService-->>Router: Refusal JSON
        else Sufficient Evidence
            ChatService->>LLM: generate_answer(message, context)
            LLM-->>ChatService: Text response
            ChatService->>CitationService: extract/map_citations(response, chunks)
            CitationService-->>ChatService: Citations
            ChatService->>ChatRepository: save_turn(session_id, response, citations, safety_trace)
            ChatRepository->>SQLite: INSERT INTO chat_turns
            ChatRepository-->>ChatService: Saved turn
            ChatService-->>Router: Response JSON
        end
    end
    
    Router-->>Frontend: Response JSON
```
