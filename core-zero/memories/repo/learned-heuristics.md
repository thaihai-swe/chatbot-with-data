# CoreZero Learned Heuristics

## Index

- LH-001 — Docs drift at workflow surface; update in same wave
- LH-002 — Bootstrap and docs verified together
- LH-003 — Generated references worth seeding early (code-map.md)
- LH-004 — Agent overscaffolds new files [ARCHIVED — promoted to code-design.md]
- LH-005 — Vague task validation leads to skipped verification
- LH-006 — Token budget underestimation triggers mid-task compaction
- LH-007 — Memory thresholds trigger post-oversize; track proactively
- LH-008 — Domain packs ignored when building features [ARCHIVED — promoted to spec-requirements]
- LH-009 — Module-level python mock bindings bypass definition-module patching

## Purpose

This file captures repeated, evidence-backed heuristics that improve maintenance of the kit.

## Heuristics

### LH-001: Docs drift fastest at the workflow surface
- Trigger:
  - a backend route or API contract changes
- Working heuristic:
  - update API documentation/endpoints in the same wave
- Evidence:
  - repeated drift found in lifecycle docs, command references, and install guidance
- Confidence: High
- Last reviewed: 2026-05-27
- Promote to stronger rule? No

### LH-005: Task validation evidence must be specific and machine-verifiable
- Trigger:
  - creating tasks in `tasks.md`
- Working heuristic:
  - every task must specify a concrete command or test file that runs and exits 0 as its validation proof, rather than vague human descriptions.
- Evidence:
  - tasks with vague proof criteria (e.g. "manual verify") lead to incomplete or skipped validation during alignment audits
- Confidence: High
- Last reviewed: 2026-06-23
- Promote to stronger rule? No

### LH-006: Token budget underestimation causes context compaction mid-complex task
- Trigger:
  - running a complex feature that loads many memory files and generates large tool output
- Working heuristic:
  - estimate token cost at feature start: count loaded files, add 2x buffer for tool output. If total exceeds 60% of capacity, split work into smaller phases and checkpoint between them.
- Evidence:
  - context compaction triggered mid-implementation, causing loss of design details and rework
- Confidence: High
- Last reviewed: 2026-06-18
- Promote to stronger rule? No — operational guidance, not normative

### LH-009: Python mock patching of module-level imports
- Trigger:
  - Patching class-level imports in Python tests where the target class is already imported at the module level in other modules.
- Working heuristic:
  - When patching a class (e.g. `WeaviateVectorStore`), if it is imported at the module level (e.g., `from indexing.weaviate_store import WeaviateVectorStore` in `ingestion.service`), mocking the class at its definition module (`indexing.weaviate_store.WeaviateVectorStore`) will not retroactively update references in the already-imported modules. We must patch the reference inside the target module where it is used (e.g., `ingestion.service.WeaviateVectorStore`).
- Evidence:
  - Refused connection error to Weaviate (localhost:8080) when running the full test suite in `pytest`, because `ingestion.service` was pre-imported by other test files before the patch was applied, binding it to the unmocked class.
- Confidence: High
- Last reviewed: 2026-07-12
- Promote to stronger rule? No

