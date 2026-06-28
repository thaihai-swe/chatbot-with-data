# Product Sense

> Pre-filled from archaeology sweep evidence (2026-06-28). Product vision and business context require adopter input for full accuracy.

## Target Users

Primary: Developers and AI enthusiasts exploring production-grade RAG implementations. This is a portfolio/learning project demonstrating end-to-end RAG system architecture.

Secondary: End-users who need to query a private document corpus via natural language, with full transparency into retrieval and generation internals.

## Core Problem

Querying unstructured documents (PDFs, text files, web pages) using natural language, with:
- Accurate, grounded answers with citations
- Transparent retrieval internals (X-Ray Panel)
- Protection against prompt injection and adversarial inputs
- Support for multiple chunking and retrieval strategies

## Success Metrics

- **Correctness**: Answers are grounded in retrieved chunks with verifiable citations
- **Safety**: Prompt injection attacks are detected and blocked (3-layer defense)
- **Transparency**: Users can inspect which chunks were retrieved and how scores were computed
- **Portfolio Value**: Demonstrates competency in FastAPI, React, vector databases, LLM integration, and production RAG patterns

> [USER REVIEW NEEDED] — Refine user personas, success metrics, and business goals.
