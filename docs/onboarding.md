# Onboarding Guide for New Developers & AI Learners

Welcome to the RAG Knowledge Base Lab! This guide will help you set up your development environment and understand the system architecture.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running Tests](#running-tests)
6. [Verification Steps](#verification-steps)
7. [Next Steps](#next-steps)

---

## Quick Start

Get the system running in 5 minutes:

```bash
# Terminal 1: Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Terminal 3: Weaviate (if not running)
docker run -d -p 8080:8080 -p 50051:50051 semitechnologies/weaviate:latest
```

Backend runs at `http://localhost:8000`  
Frontend runs at `http://localhost:5173` (or similar)  
Weaviate runs at `http://localhost:8080`

---

## Environment Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker (for Weaviate)
- Git

### 1. Clone the Repository

```bash
git clone <repo-url>
cd chatbot-with-data
```

### 2. Create Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Configure Environment Variables

Copy the sample environment file and update with your API keys:

```bash
cp .env.sample .env
```

Edit `.env` with:
- `OPENAI_API_KEY`: Your OpenAI API key (for embeddings and chat)
- `EMBEDDING_API_BASE`: OpenAI API base URL (default: https://api.openai.com/v1)
- `EMBEDDING_API_KEY`: Embedding service API key (can be same as OPENAI_API_KEY)
- `WEAVIATE_URL`: Weaviate instance URL (default: http://localhost:8080)

Example `.env`:
```
OPENAI_API_KEY=sk-...
EMBEDDING_API_BASE=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-...
WEAVIATE_URL=http://localhost:8080
```

---

## Backend Setup

### 1. Install Dependencies

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database

The SQLite database is created automatically on first run. To reset:

```bash
rm backend/data/rag_lab.db  # Remove existing database
# Database will be recreated on next backend start
```

### 3. Start the Backend Server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 4. Verify Backend Health

```bash
curl http://localhost:8000/health
# Expected response: {"status":"ok"}
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

You should see:
```
  VITE v... ready in ... ms

  ➜  Local:   http://localhost:5173/
```

### 3. Open in Browser

Navigate to `http://localhost:5173` and you should see the chat interface.

---

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Integration Tests

```bash
# Ensure backend and frontend are running
cd tests
pytest integration/ -v
```

---

## Verification Steps

### Step 1: Upload a Document

1. Open frontend at `http://localhost:5173`
2. Click "Upload Document"
3. Select a PDF, TXT, or MD file
4. Wait for processing to complete

### Step 2: Query the Document

1. In the chat interface, type a question about the document
2. The system should return a grounded answer with citations

### Step 3: Check Backend Logs

You should see logs like:
```
INFO: Processing ingestion attempt: <uuid>
INFO: Chunking document...
INFO: Generating embeddings...
INFO: Indexing chunks in Weaviate...
INFO: Ingestion complete
```

### Step 4: Verify Database

```bash
sqlite3 backend/data/rag_lab.db
sqlite> SELECT COUNT(*) FROM documents;
sqlite> SELECT COUNT(*) FROM chunks;
sqlite> .quit
```

---

## Example: Using the API with Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Create a collection
collection_response = requests.post(
    f"{BASE_URL}/collections",
    json={"name": "My Knowledge Base", "description": "Test collection"}
)
collection_id = collection_response.json()["id"]
print(f"Created collection: {collection_id}")

# 2. Upload a document
with open("sample.pdf", "rb") as f:
    files = {"file": f}
    data = {"collection_ids": [collection_id]}
    upload_response = requests.post(
        f"{BASE_URL}/ingestion/file-upload",
        files=files,
        data=data
    )
    attempt_id = upload_response.json()["id"]
    print(f"Upload attempt: {attempt_id}")

# 3. Check ingestion status
status_response = requests.get(
    f"{BASE_URL}/ingestion/attempts/{attempt_id}"
)
print(f"Status: {status_response.json()['status']}")

# 4. Create a chat session
session_response = requests.post(
    f"{BASE_URL}/chat/sessions",
    json={"collection_ids": [collection_id]}
)
session_id = session_response.json()["id"]
print(f"Chat session: {session_id}")

# 5. Send a query
query_response = requests.post(
    f"{BASE_URL}/chat/sessions/{session_id}/turns/stream",
    json={"query": "What is the main topic?"}
)
print(f"Answer: {query_response.json()['answer']}")
```

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# List collections
curl http://localhost:8000/collections

# Create a collection
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{"name":"My Collection","description":"Test"}'

# Upload a file
curl -X POST http://localhost:8000/ingestion/file-upload \
  -F "file=@sample.pdf" \
  -F "collection_ids=[\"<collection-id>\"]"
```

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.9+)
- Verify virtual environment is activated: `which python` should show `.venv` path
- Check port 8000 is not in use: `lsof -i :8000`

### Frontend won't start
- Check Node version: `node --version` (need 16+)
- Clear npm cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### Weaviate connection error
- Ensure Docker is running: `docker ps`
- Check Weaviate is accessible: `curl http://localhost:8080/v1/.well-known/ready`
- Restart Weaviate: `docker restart <container-id>`

### Database locked error
- Stop all backend processes
- Remove lock file: `rm backend/data/rag_lab.db-wal`
- Restart backend

### API returns 401 or 403
- Verify `OPENAI_API_KEY` is set correctly in `.env`
- Check API key has required permissions
- Regenerate key if needed

---

## Next Steps

1. **Read the Architecture Overview**: See [`architecture-overview.md`](./architecture-overview.md) to understand system components and how they interact
2. **Explore API Flows**: Check [`api-flows.md`](./api-flows.md) for detailed endpoint documentation with request/response examples
3. **Learn RAG Concepts**: Review [`ai-learning.md`](./ai-learning.md) for ingestion pipeline, embeddings, hybrid search, grounding, and safety filters
4. **Check Database Schema**: See [`database-schema.md`](./database-schema.md) for data model details, table definitions, and access patterns
5. **Review System Flow**: Look at [`diagrams/system-flow.md`](./diagrams/system-flow.md) for end-to-end flow diagrams and sequence charts

---

## Getting Help

- Check logs: `tail -f backend/logs/app.log`
- Review error messages in browser console (F12)
- Search existing issues in the repository
- Ask in the team Slack channel

Happy coding! 🚀
