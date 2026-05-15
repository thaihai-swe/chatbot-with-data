# API Flow: POST /chat/sessions/{id}/turns/stream

```mermaid
sequenceDiagram
    participant Frontend
    participant Router as Router (chat.py)
    participant StreamingOrchestrator
    participant AdvancedRetrievalService
    participant ChromaDB
    participant LLM
    
    Frontend->>Router: POST /chat/sessions/{id}/turns/stream
    Router->>StreamingOrchestrator: start_stream(session_id, message)
    Router-->>Frontend: SSE Event Stream established
    
    par Retrieval and LLM
        StreamingOrchestrator->>AdvancedRetrievalService: retrieve_context(message)
        AdvancedRetrievalService->>ChromaDB: query_vectors
        ChromaDB-->>AdvancedRetrievalService: Relevant chunks
        AdvancedRetrievalService-->>StreamingOrchestrator: Context
    and
        StreamingOrchestrator->>LLM: stream_generation(message, context)
        LLM-->>StreamingOrchestrator: Tokens
    end
    
    StreamingOrchestrator-->>Frontend: Stream Tokens/Citations via SSE
```
