# API Flow: DELETE /documents/{id}

```mermaid
sequenceDiagram
    participant Frontend
    participant Router as Router (documents.py)
    participant Repository
    participant Weaviate
    
    Frontend->>Router: DELETE /documents/{id}
    Router->>Repository: delete_document(id)
    Repository->>Weaviate: delete_by_document(id)
    Weaviate-->>Repository: Success
    Repository-->>Router: Deleted
    Router-->>Frontend: 204 No Content
```
