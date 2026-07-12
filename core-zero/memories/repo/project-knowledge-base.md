# CoreZero Project Knowledge Base

## Index

- System Reference Documents — links to architecture.md and core-policies.md
- Repository Overview — kit structure (skills/, references/, core-zero/, scripts/)
- Key Architectural Boundaries — template postures, memory governance, review modes, command ownership
- Common Installation & Bootstrap Watchouts — baseline testing, router drift, generated placeholders
- Feature Lifecycle Handoff Patterns — first-feature routing, state mismatch repair

## System Reference Documents

- Architecture Boundary Map: Refer to `core-zero/project/architecture.md` for static system snapshots, components, and runtime boundaries. Do not duplicate structural maps here.
- Rules & Mandates: Refer to `core-zero/memories/repo/core-policies.md` for normative CC-* mandates.

## Repository Overview

- This repository is an artifact-first kit for Harness Engineering and spec-driven AI development.
- Core workflow logic lives in `skills/*/SKILL.md`.
- Reusable scaffolds live beside each skill under `references/`.
- Adopter-facing documentation lives under `core-zero/`.
- Maintainer-facing documentation lives under `documents/`.
- Generated references live under `core-zero/generated/`.
- Bootstrap and maintenance scripts live under `scripts/`.

## Key Architectural Boundaries

Refer to `core-zero/project/architecture.md` for static component paths and integration details. This section outlines AI-enforced execution boundaries.

### 1. Shipped Template Copy Posture
The installer script (`scripts/install.sh`) handles files using three distinct postures specified in `manifest.json`:
- `overwrite`: Core kit tools and guides (e.g. `skills/`, `rules/`, `MASTER_INDEX.md`) that are refreshed on every upgrade to keep the automation framework up to date.
- `copyIfMissing`: Starter template files and memory baselines (e.g., `AGENTS.md`, `core-policies.md`, `project-knowledge-base.md`). If the adopter project has customized these, the installer respects their edits and does not overwrite them.
- `preserve`: Feature-specific state folders (`artifacts/features/`, local settings). These are completely owned by the adopter project and are never touched by the installer.

### 2. The Memory Governance Loop
Tier definitions (Instruction / Auto / Extracted) and the promotion loop live in `skills/context-memory/SKILL.md` `## Memory Tiers`. Intent-based routing of these tiers lives in `MASTER_INDEX.md`.

### 3. Gated Integration vs. Standalone Review Distinction
The dual-purpose behavior of `code-review` (standalone PR mode vs. `/harness-verify`-gated blocking mode) is defined in `skills/code-review/SKILL.md`.

### 4. Shipped Command Ownership
The shipped helpers own the following durable surfaces:
- `scripts/corezero status` owns deterministic status reporting across `artifacts/features/` and regenerates `core-zero/generated/dashboard.html`.
- `/harness-maintain` owns codemap/reference-index regeneration and observability-driven harness assessment and improvement.
- `/spec-adr` owns ADR creation and append-only log updates in `core-zero/memories/repo/adr-log.md`.
- `/technical-docs` owns feature-scoped API and flow documentation outputs.
- `/codebase-documenter` owns broader repo onboarding and architecture doc sets.
- `/visualize` owns optional SVG and Mermaid diagram outputs when a dedicated visual artifact is required.

## Common Installation & Bootstrap Watchouts

- Baseline Testing: `/starter-init` checks whether the target repository is greenfield or brownfield. It requires running the canonical baseline test or compile check. If none exists, the adopter must document the best available proof surface before autonomous feature work can proceed.
- Drift in Routers: `AGENTS.md` is the runtime instruction router and standards reference; it is intentionally detailed (~150 lines) to serve as a single entrypoint for agent behavior. Standard operating guidelines live in `core-policies.md` and are linked from `AGENTS.md`. If you trim `AGENTS.md`, ensure core operating guidelines remain accessible in `core-policies.md`.
- Generated Placeholder Ownership: `core-zero/project/code-map.md` is a shipped placeholder refreshed by `/harness-maintain`. `core-zero/generated/dashboard.html` is refreshed by `scripts/corezero status`.

## Feature Lifecycle Handoff Patterns

- The first feature starts with `/spec-requirements` or `/spec-research`. `scripts/corezero session-*` is available only after a feature slug and `status.md` already exist, and closes long work sessions with `.corezero/sessions/<slug>/session.md`.
- Mismatches between handoff claims and actual disk state at session start must be routed to `/harness-maintain assess` to repair the state before delivery work commences.

## Project Main Components & Integration Boundaries

- **Frontend Application**: Vite-bundled React Single Page Application communicating with the backend API using fetch and Server-Sent Events.
- **Backend Application**: FastAPI ASGI server performing document ingestion, chunking, understanding, vector database sync, and LLM orchestration.
- **Relational Boundary**: SQLite database (`data/knowledge_ingestion/app.db` or `data.db`) storing structured metadata, turns, citations, and settings.
- **Vector Boundary**: Local Weaviate instance (port 8080) containing semantic indexes of chunked document text.

## Preserved Behavior Baseline

1. **SSE Event Stream Formatting**: The streaming orchestrator (`streaming.py`) must emit structured messages matching the SSE format (`event: {event_name}\ndata: {json_payload}\n\n`). The client expects events: `status`, `token`, `citations`, `error`, and `done`. The `citations` event payload must include `citations`, `retrieved_chunks`, `retrieval_trace`, `safety_trace`, `conflict_status`, `conflict_details`, `groundedness_score`, and `provenance`.
2. **Pre-generation Safety and Grounding Gating**: The streaming orchestrator verifies prompt safety using `safety_service.check_query`. If classified as unsafe, it registers a completed turn and streams the refusal message immediately. It also runs `grounding_service.evaluate_evidence`. If evidence is insufficient, it simulates a token-by-token stream of the refusal reason and ends the turn without querying the LLM for generation.
3. **Turn Cancellation Pipeline**: The backend checks `is_cancelled(turn_id)` at key pipeline checkpoints (post-retrieval, during refusal streaming, during generation, and before finalizing). If cancellation is requested, the turn status is immediately committed to SQLite as `cancelled` and the response stream is closed.
4. **Duplicate Detection Ingestion Status**: During ingestion (`service.py`), document text is compared via `DuplicateDetector`. If classified as anything other than `UNIQUE`, the process halts, and the status updates to `AWAITING_USER_ACTION`. Unique documents proceed directly to document understanding, chunking, and Weaviate indexing.

## Domain Jargon & Ubiquitous Language

- **Citation**: A verified reference back to a retrieved source text chunk in an uploaded document, including text fragment and source metadata.
- **Groundedness / Grounding**: Gating check to ensure the generated response is strictly supported by retrieved facts, preventing hallucinations.
- **Ingestion**: The end-to-end process of receiving files, extracting text, run-throughs with document understanding, splitting via chunkers, and indexing.
- **SSE (Server-Sent Events)**: The streaming protocol used to push real-time response tokens, status updates, and citation metadata to the client.
- **Duplicate Detector**: Ingestion component validating that an incoming file's text is not already present, returning uniqueness classifications.
- **Reranking**: Scoring step executing after initial vector store retrieval to sort chunks by prompt-relevance using a FlashRank model.
- **Ablation / Variant**: Evaluation dashboard terminology for assessing RAG system changes (different chunkers, vector configurations, etc.).

