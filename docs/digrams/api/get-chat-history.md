# API Flow: GET /chat/sessions/{id}/history

```mermaid
sequenceDiagram
    participant Frontend
    participant Router as Router (chat.py)
    participant ChatRepository
    participant SQLite
    
    Frontend->>Router: GET /chat/sessions/{id}/history
    Router->>ChatRepository: get_history(id)
    ChatRepository->>SQLite: SELECT FROM chat_turns WHERE session_id={id}
    SQLite-->>ChatRepository: Turn and citation records
    ChatRepository-->>Router: List of turns and citations
    Router-->>Frontend: List of turns and citations
```
