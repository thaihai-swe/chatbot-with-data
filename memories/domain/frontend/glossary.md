---
domain: frontend
triggers: [frontend, react, ui, screen, component, vite, x-ray, chat ui, document library, settings, evaluation, playground]
---

# Frontend UI — Glossary

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Ubiquitous Language

| Term | Definition | Source |
|------|------------|--------|
| X-Ray Panel | Debug panel showing retrieval internals: chunk scores, citation mapping, generation details | `frontend/src/components/XRayPanel/` |
| Experiment Comparison | Side-by-side comparison of different retrieval/LLM configurations | `frontend/src/screens/ExperimentComparison/` |
| Collection Routing UI | UI for selecting and managing document collections | `frontend/src/screens/Collections/` |
| Duplicate Decision | UI for reviewing and resolving duplicate document detections | `frontend/src/screens/DuplicateDecision/` |
| Evaluation | Sanity-check interface for testing the RAG pipeline | `frontend/src/screens/Evaluation/` |
| Playground | Ad-hoc query testing interface for developers | `frontend/src/screens/Playground/` |

## Notes

- 7 screens total, 13 reusable components.
- API client modules in `frontend/src/api/`: `client.js`, `chat.js`, `knowledgeApi.js`, `settings.js`.
- Single-page app using React Router v6.
