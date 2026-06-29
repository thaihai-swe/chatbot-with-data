---
domain: frontend
triggers: [frontend, react, ui, screen, component, vite, x-ray, chat ui, document library, settings, evaluation]
---

# Frontend UI — Glossary

> **Ownership:** Collaborative — skill-updated + user-maintained.

## Ubiquitous Language

| Term | Definition | Source |
|------|------------|--------|
| X-Ray Panel | Debug panel showing retrieval internals: chunk scores, citation mapping, generation details | `frontend/src/components/XRayPanel/` |
| Collection Routing UI | UI for selecting and managing document collections | `frontend/src/screens/Collections/` |
| Duplicate Decision | UI for reviewing and resolving duplicate document detections | `frontend/src/screens/DuplicateDecision/` |
| Evaluation | Sanity-check interface for testing the RAG pipeline | `frontend/src/screens/Evaluation/` |

## Notes

- 6 screens total, 11 reusable components.
- API client modules in `frontend/src/api/`: `client.js`, `chat.js`, `knowledgeApi.js`, `settings.js`.
- Single-page app using React Router v6.
