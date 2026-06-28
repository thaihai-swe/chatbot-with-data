# Project Knowledge Base — Chatbot With Data

## Index

- **System Reference Documents** — links to architecture.md and core-policies.md
- **Repository Overview** — kit structure (skills/, references/, core-zero/, scripts/)
- **Key Architectural Boundaries** — template postures, memory governance, review modes, command ownership
- **Common Installation & Bootstrap Watchouts** — baseline testing, router drift, generated placeholders
- **Feature Lifecycle Handoff Patterns** — first-feature routing, state mismatch repair

## System Reference Documents

- **Architecture Boundary Map:** Refer to `core-zero/project/architecture.md` for static system snapshots, components, and runtime boundaries. Do not duplicate structural maps here.
- **Rules & Mandates:** Refer to `memories/repo/core-policies.md` for normative CC-* mandates.

## Repository Overview

- This repository is **Chatbot With Data** — a production-grade RAG system for querying documents via natural language.
- **Backend**: FastAPI Python app at `backend/` with async RAG pipeline
- **Frontend**: React SPA at `frontend/` with Vite dev server
- **Vector DB**: Weaviate 1.27.0 (Docker) for hybrid search (BM25 + semantic)
- **LLM**: OpenAI GPT-4o / compatible endpoint via provider abstraction layer
- **Metadata**: SQLite with 16 tables, 4 migration versions
- Design docs live under `documents/` (16 files covering architecture, API, schema, chunking, retrieval, security)
- Harness policy lives under `core-zero/`
- Utility scripts live under `scripts/`

## Key Architectural Boundaries

Refer to `core-zero/project/architecture.md` for static component paths and integration details. This section outlines AI-enforced execution boundaries.


### 1. Shipped Template Copy Posture
The installer script (`scripts/install.sh`) handles files using three distinct postures specified in `manifest.json`:
- **`overwrite`**: Core kit tools and guides (e.g. `skills/**`, `rules/**`, `MASTER_INDEX.md`) that are refreshed on every upgrade to keep the automation framework up to date.
- **`copyIfMissing`**: Starter template files and memory baselines (e.g., `AGENTS.md`, `core-policies.md`, `project-knowledge-base.md`). If the adopter project has customized these, the installer respects their edits and does not overwrite them.
- **`preserve`**: Feature-specific state folders (`artifacts/features/`, local settings). These are completely owned by the adopter project and are never touched by the installer.

### 2. The Memory Governance Loop
Tier definitions (Instruction / Auto / Extracted) and the promotion loop live in `skills/context-memory/SKILL.md` `## Memory Tiers`. Intent-based routing of these tiers lives in `MASTER_INDEX.md`.

### 3. Gated Integration vs. Standalone Review Distinction
The dual-purpose behavior of `code-review` (standalone PR mode vs. `/harness-verify`-gated blocking mode) is defined in `skills/code-review/SKILL.md`.

### 4. Shipped Command Ownership
The shipped helpers own the following durable surfaces:
- **`/context-status`** owns status reporting across `artifacts/features/` and regenerates `core-zero/generated/dashboard.html`.
- **`/harness-maintain`** owns codemap/reference-index regeneration and observability-driven harness assessment and improvement.
- **`/spec-adr`** owns ADR creation and append-only log updates in `memories/repo/adr-log.md`.
- **`/technical-docs`** owns feature-scoped API and flow documentation outputs.
- **`/codebase-documenter`** owns broader repo onboarding and architecture doc sets.
- **`/visualize`** owns optional SVG and Mermaid diagram outputs when a dedicated visual artifact is required.

## Common Installation & Bootstrap Watchouts

- **Baseline Testing**: `/starter-init` checks whether the target repository is greenfield or brownfield. It requires running the canonical baseline test or compile check. If none exists, the adopter must document the best available proof surface before autonomous feature work can proceed.
- **Drift in Routers**: `AGENTS.md` is the runtime instruction router and standards reference; it is intentionally detailed (~150 lines) to serve as a single entrypoint for agent behavior. Standard operating guidelines live in `core-policies.md` and are linked from `AGENTS.md`. If you trim `AGENTS.md`, ensure core operating guidelines remain accessible in `core-policies.md`.
- **Generated Placeholder Ownership**: `core-zero/project/code-map.md` is a shipped placeholder refreshed by `/harness-maintain`. `core-zero/generated/dashboard.html` is refreshed by `/context-status`.

## Domain Jargon / Ubiquitous Language

| Term | Definition |
|------|------------|
| RAG | Retrieval-Augmented Generation — core pattern: retrieve relevant chunks then generate answers grounded in those chunks |
| Hybrid Search | Default retrieval strategy combining BM25 keyword search + semantic vector search via RRF fusion |
| Chunking Strategies | 5 strategies for splitting documents: fixed-size, heading-aware (markdown), page-aware (PDF), semantic (topic-boundary), parent-child (hierarchical) |
| Query Intelligence | Pre-retrieval pipeline: intent classification, query expansion, HyDE (Hypothetical Document Embedding), query decomposition, synonym expansion, dynamic collection routing |
| Prompt Injection Defense | 3-layer protection: heuristic scanner (49 regex patterns), fuzzy scanner (cosine similarity to known corpus), LLM scanner (LLM judges if query is adversarial) |
| Grounded Generation | Evidence sufficiency scoring + groundedness checking + citation extraction to ensure answers are supported by retrieved chunks |
| X-Ray Panel | Frontend debug panel showing retrieval internals, chunk scores, citation mapping, and generation details |
| Collection Routing | LLM-routed selection of which document collections to search based on the user's query |
| CandidateMerger | RRF-based fusion of multi-strategy retrieval results (BM25 + semantic + optional HyDE) |

## Feature Lifecycle Handoff Patterns

- The first feature starts with `/spec-requirements` or `/spec-research`. `/context-session` is the session-boundary skill only after a feature slug and `status.md` already exist, and it still closes long work sessions with `handoff.md` and `progress.md`.
- Mismatches between handoff claims and actual disk state at session start must be routed to `/harness-maintain assess` to repair the state before delivery work commences.

## Preserved Behavior Baseline

From archaeology sweep (see `memories/repo/brownfield/brownfield-map.md`):

1. **Prompt injection defense must remain active**: The 3-layer safety check (heuristic → fuzzy → LLM) in `backend/chat/safety.py` must always run before any user query reaches the retrieval or generation pipeline.
2. **Hybrid search (BM25 + vector) must remain the default retrieval strategy**: The `CandidateMerger` with RRF fusion in `backend/chat/retrieval.py` is the core differentiator.
3. **SQLite schema must be backward-compatible**: 16 tables across 4 migration versions exist. Any schema changes must not break the existing migration chain in `backend/migrations/runner.py`.
