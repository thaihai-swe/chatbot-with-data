# CoreZero Project Knowledge Base

## Index

- **System Reference Documents** — links to architecture.md and core-policies.md
- **Repository Overview** — kit structure (skills/, references/, docs/, scripts/)
- **Key Architectural Boundaries** — template postures, memory governance, review modes, command ownership
- **Common Installation & Bootstrap Watchouts** — baseline testing, router drift, generated placeholders
- **Feature Lifecycle Handoff Patterns** — first-feature routing, state mismatch repair

## System Reference Documents

- **Architecture Boundary Map:** Refer to `docs/project/architecture.md` for static system snapshots, components, and runtime boundaries. Do not duplicate structural maps here.
- **Rules & Mandates:** Refer to `memories/repo/core-policies.md` for normative CC-* mandates.

## Repository Overview

- This repository is an artifact-first kit for Harness Engineering and spec-driven AI development.
- Core workflow logic lives in `skills/*/SKILL.md`.
- Reusable scaffolds live beside each skill under `references/`.
- Adopter-facing documentation lives under `docs/`.
- Maintainer-facing documentation lives under `documents/`.
- Generated references live under `docs/generated/`.
- Bootstrap and maintenance scripts live under `scripts/`.

## Key Architectural Boundaries

Refer to `docs/project/architecture.md` for static component paths and integration details. This section outlines AI-enforced execution boundaries.


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
- **`/context-status`** owns status reporting across `artifacts/features/` and regenerates `docs/generated/dashboard.html`.
- **`/harness-maintain`** owns codemap/reference-index regeneration and observability-driven harness assessment and improvement.
- **`/spec-adr`** owns ADR creation and append-only log updates in `memories/repo/adr-log.md`.
- **`/technical-docs`** owns feature-scoped API and flow documentation outputs.
- **`/codebase-documenter`** owns broader repo onboarding and architecture doc sets.
- **`/visualize`** owns optional SVG and Mermaid diagram outputs when a dedicated visual artifact is required.

## Common Installation & Bootstrap Watchouts

- **Baseline Testing**: `/starter-init` checks whether the target repository is greenfield or brownfield. It requires running the canonical baseline test or compile check. If none exists, the adopter must document the best available proof surface before autonomous feature work can proceed.
- **Drift in Routers**: `AGENTS.md` is the runtime instruction router and standards reference; it is intentionally detailed (~150 lines) to serve as a single entrypoint for agent behavior. Standard operating guidelines live in `core-policies.md` and are linked from `AGENTS.md`. If you trim `AGENTS.md`, ensure core operating guidelines remain accessible in `core-policies.md`.
- **Generated Placeholder Ownership**: `docs/project/code-map.md` is a shipped placeholder refreshed by `/harness-maintain`. `docs/generated/dashboard.html` is refreshed by `/context-status`.

## Feature Lifecycle Handoff Patterns

- The first feature starts with `/spec-requirements` or `/spec-research`. `/context-session` is the session-boundary skill only after a feature slug and `status.md` already exist, and it still closes long work sessions with `handoff.md` and `progress.md`.
- Mismatches between handoff claims and actual disk state at session start must be routed to `/harness-maintain assess` to repair the state before delivery work commences.
