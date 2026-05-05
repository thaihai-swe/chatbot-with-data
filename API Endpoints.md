
## API Endpoints

All endpoints are documented in the backend and return standard HTTP status codes.

### Collections

- `GET /collections` - List all collections
- `POST /collections` - Create collection
- `PATCH /collections/{id}` - Update collection (rename, description)
- `DELETE /collections/{id}` - Delete collection

### Documents

- `GET /documents` - List documents (with filters: collection_id, query)
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document
- `POST /documents/{id}/move` - Move document to collection(s)
- `POST /documents/{id}/reingest` - Re-ingest document
- `POST /documents/{id}/reindex` - Initiate re-indexing (placeholder for now)

### Ingestion

- `POST /ingestion/file-upload` - Upload and ingest file
- `POST /ingestion/url` - Fetch and ingest URL
- `GET /ingestion/attempts` - List ingestion attempts (with status filter)
- `GET /ingestion/attempts/{id}` - Get ingestion attempt details
- `POST /ingestion/attempts/{id}/duplicate-decision` - Resolve duplicate

### Health

- `GET /health` - Backend health check

All requests include a `X-Request-ID` header for traceability and debugging.
