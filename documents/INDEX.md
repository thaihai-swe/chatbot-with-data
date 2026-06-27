# Documentation Index

**Last verified:** 2026-05-29

This index lists every document in `/docs` with a one-line summary and a freshness/status badge. Use it to find what you need quickly.

## Status Legend
- 🟢 **Implemented** — accurately describes shipped code
- 🟡 **Partial** — describes a mix of shipped and planned features (clearly labeled inside)
- ⏳ **Planned** — describes a roadmap item, not yet built
- 📚 **Educational** — concept-focused, evergreen

---

## Getting Started

| Doc | Status | Summary |
|---|---|---|
| [onboarding.md](./onboarding.md) | 🟢 | Setup, install, and verify the system end-to-end |
| [README.md](../README.md) | 🟢 | Portfolio narrative: problem, pipeline, techniques, results |

## Architecture & Reference

| Doc | Status | Summary |
|---|---|---|
| [system-architecture.md](./system-architecture.md) | 🟢 | Components, data flow, and module map |
| [database-schema.md](./database-schema.md) | 🟢 | All SQLite tables, columns, FKs, and indexes |
| [api-flows.md](./api-flows.md) | 🟢 | Every REST endpoint with request/response and internal flow |
| [diagrams/api/](./diagrams/api/) | 🟡 | Mermaid sequence diagrams for 24 of 27 endpoints |
| [diagrams/system-flow.md](./diagrams/system-flow.md) | 🟡 | Mermaid diagrams for ingestion and retrieval pipelines |

## Pipeline Deep Dives

| Doc | Status | Summary |
|---|---|---|
| [RETRIEVAL_FLOW.md](./RETRIEVAL_FLOW.md) | 🟡 | End-to-end retrieval: query intelligence, multi-strategy, RRF |
| [CHUNKING_STRATEGIES.md](./CHUNKING_STRATEGIES.md) | 🟢 | Five chunking strategies and auto-selection logic |
| [feature-visualization.md](./feature-visualization.md) | 🟡 | Decision trees and visual flows for each subsystem |

## Safety & Validation

| Doc | Status | Summary |
|---|---|---|
| [PROMPT_INJECTION_DETECTION.md](./PROMPT_INJECTION_DETECTION.md) | 🟢 | Three-layer injection defense: heuristic, fuzzy, LLM |
| [PROMPT_INJECTION_TESTING_GUIDE.md](./PROMPT_INJECTION_TESTING_GUIDE.md) | 🟢 | Test cases for verifying injection detection |
| [SYSTEM_VALIDATION_GUIDE.md](./SYSTEM_VALIDATION_GUIDE.md) | 🟡 | Input validation, integrity checks, health monitoring |
| [PII_DETECTION_TUNING.md](./PII_DETECTION_TUNING.md) | ⏳ | PII detection design (not yet implemented) |

## Learning Resources

| Doc | Status | Summary |
|---|---|---|
| [ai-learning.md](./ai-learning.md) | 📚 | RAG concepts, embeddings, hybrid search, grounding |
| [SECURITY_LEARNING_RESOURCES.md](./SECURITY_LEARNING_RESOURCES.md) | 📚 | External security and prompt-injection references |

## Roadmap & Recommendations

| Doc | Status | Summary |
|---|---|---|
| [enhancement-recommendations.md](./enhancement-recommendations.md) | 🟡 | Implemented vs planned upgrades, with rationale |
| [../rag-prd-requirement.md](../rag-prd-requirement.md) | 🟡 | Full feature requirements for production-grade RAG |

---

## How to Read These Docs

- **Reviewers/recruiters:** Start with [README.md](../README.md), then [system-architecture.md](./system-architecture.md), then [RETRIEVAL_FLOW.md](./RETRIEVAL_FLOW.md).
- **New contributors:** Start with [onboarding.md](./onboarding.md), then [database-schema.md](./database-schema.md), then [api-flows.md](./api-flows.md).
- **AI learners:** Start with [ai-learning.md](./ai-learning.md), then [RETRIEVAL_FLOW.md](./RETRIEVAL_FLOW.md), then [CHUNKING_STRATEGIES.md](./CHUNKING_STRATEGIES.md).

## Doc Conventions

Every doc has a metadata header:

```
**Status:** 🟢 Implemented | 🟡 Partial | ⏳ Planned | 📚 Educational
**Last verified:** YYYY-MM-DD
**Source files:** backend/path/to/file.py, ...
```

When something is described that doesn't exist in code yet, it is explicitly marked `⏳ Planned` or sectioned under "Roadmap" so readers don't confuse aspiration with reality.
