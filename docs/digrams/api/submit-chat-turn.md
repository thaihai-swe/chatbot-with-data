# API Flow: POST /chat/sessions/{id}/turns

```mermaid
sequenceDiagram
    participant Frontend
    participant Router as Router (chat.py)
    participant ChatService
    participant AdvancedRetrievalService
    participant ChromaDB
    participant LLM
    participant CitationService
    participant ChatRepository
    participant SQLite
    
    Frontend->>Router: POST /chat/sessions/{id}/turns (message)
    Router->>ChatService: process_turn(session_id, message)
    ChatService->>AdvancedRetrievalService: retrieve_context(message)
    AdvancedRetrievalService->>ChromaDB: query_vectors
    ChromaDB-->>AdvancedRetrievalService: Relevant chunks
    AdvancedRetrievalService-->>ChatService: Context
    ChatService->>LLM: generate_response(message, context)
    LLM-->>ChatService: Text response
    ChatService->>CitationService: create_citations(response, chunks)
    CitationService-->>ChatService: Citations
    ChatService->>ChatRepository: save_turn(session_id, response, citations)
    ChatRepository->>SQLite: INSERT INTO chat_turns
    ChatRepository-->>ChatService: Saved turn
    ChatService-->>Router: Response JSON
    Router-->>Frontend: Response JSON
```
