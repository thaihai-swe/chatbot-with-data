# RAG Knowledge Base Lab

A production-ready Retrieval-Augmented Generation (RAG) system with hybrid search, grounded chat, and citation tracking.

## 📚 Documentation

**New to the project?** Start with the [Onboarding Guide](docs/onboarding.md) for complete setup instructions.

### Core Documentation
- **[Onboarding Guide](docs/onboarding.md)** - Environment setup, installation, and verification steps
- **[Architecture Overview](docs/architecture-overview.md)** - System components and interaction flow
- **[AI Learning Guide](docs/ai-learning.md)** - RAG concepts, embeddings, hybrid search, and grounding
- **[API Flows](docs/api-flows.md)** - Detailed endpoint documentation with examples
- **[Database Schema](docs/database-schema.md)** - Data models and storage architecture
- **[System Flow Diagrams](docs/diagrams/system-flow.md)** - Visual end-to-end workflows

---

## Quick Start

### Backend startup:

```bash
# 1. Activate the Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Start the backend server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend startup:

```bash
# In a new terminal, from the root directory
cd frontend

# 1. Install Node dependencies
npm install

# 2. Start the dev server
npm run dev
```

---

## Testing Guide

| Test Goal | Question to Ask | Why it tests the mode |
|-----------|-----------------|----------------------|
| Keyword Test | "What should I do if I see ERR-999-X?" | Tests exact string matching for unique technical codes. |
| Semantic Test | "Tell me about using this device in dense air or deep underground." | Tests meaning-based retrieval (the file mentions "high-pressure" and "subterranean" but not "dense air"). |
| Hybrid Test | "Explain the low latency capabilities of the Nexus-7-Alpha." | Tests the combination of a specific product name (keyword) and a functional concept (semantic). |
| Settings Test | "What is the Shadow-Link protocol?" | Try asking this with alpha=0 (Keyword only) vs alpha=1 (Semantic only) to see how the ranking changes. |
