---
id: skill-starter-init
name: starter-init
description: "Initialize the kit structure in a new repository.  Initialize a project for harnessed agentic development."
tags: ['setup', 'init', 'onboarding']
triggers: ['init', 'start', 'setup', 'install']
next_skill: 'spec-research'

---
# Starter Init

## Overview
Bootstraps the `docs/` and `memories/` directories with standard templates, then guides the adopter through customizing the seeded memory files for their project.
Establishes the repository baseline for the harness before feature work begins. Detects repo type, runs a read-only archaeology pass for brownfield repositorys, and sets up the initial memory scaffold with adopter-specific content.
## I/O Hand-off Protocol
- **Reads**: target repo structure, `memories/repo/*.md` seeded by the installer.
- **Writes**: Generates `docs/` and `memories/` folders, baseline markdown files, `.gitignore` entries, and customized memory files.
- **Next Skill**: `/spec-research` (brownfield) or `/spec-requirements` (greenfield).

## Workflow

1. **Step 1: Initialization**: Read `docs/project/agent-capabilities.md` and check that the current agent has all Required capabilities (shell execution, file editing, skill invocation). Warn if Recommended (subagent) or Optional (Python 3, mmdc) capabilities are missing. Create `docs/project`, `docs/generated`, `memories/repo`, and `memories/domain`. Ensure `.gitignore` is populated with kit ignores (`docs/generated/*`, `memories/repo/harness-telemetry.md`, `scripts/harness/gate-runner.local.sh`). Use `references/init-checklist.md` to guide the bootstrap process.
2. **Step 2: Archaeology Sweep (Phase A)**: Detect greenfield vs. brownfield.
   - Greenfield: empty repo or only the kit's own files. Skip archaeology.
   - Brownfield: Follow `references/brownfield-mode.md` to conduct a read-only archaeology sweep. Delegate broad searches using subagents (Subagent-First Exploration). Create `memories/repo/brownfield/brownfield-map.md` to document the findings. Record the baseline test command and high-risk paths. If no baseline exists, prompt the adopter.
3. **Step 3: Memory Customization (Phase B)**: This is mandatory. The installer seeds `memories/repo/*.md` with generic kit content. Run each step interactively by prompting the user for details to rewrite them:
    - **`core-policies.md`**: Prompt for project identity, default branch, and verification commands. Mark missing commands as `N/A`.
    - **`core-policies.md` Security**: Prompt for trust boundaries and sensitive paths (use Phase A findings). Keep `Prompt-Injection Defense` verbatim.
    - **`project-knowledge-base.md`**: Prompt for main components, integration boundaries, preserved behaviors, and **Domain Jargon / Ubiquitous Language**. Capturing project-specific jargon radically reduces verbosity and ambiguity in future sessions.
    - **`learned-heuristics.md`**: Drop kit-specific LH-* entries unless explicitly kept.
    - **Domain Packs**: Read `memories/domain/glossary.md` triggers. Prompt if subdomains exist. If yes, copy the domain scaffold into `memories/domain/<name>/` and update `MASTER_INDEX.md`.
    - **Gate Runner Setup**: Prompt for project build/lint/test commands. If provided, copy the generic template to `scripts/harness/gate-runner.local.sh` and seed it with the adopter's commands.
      ```
      cp scripts/harness/gate-runner.local.example.sh scripts/harness/gate-runner.local.sh
      ```
      Then edit `gate-runner.local.sh` to set the actual commands.
4. **Step 4: Confirm and Handoff**: Run `/context-memory --audit` to confirm all kit-internal paths are removed from the memory files and triggers are populated. Route the user to `/spec-research` (brownfield) or `/spec-requirements` (greenfield).

## Core Rules
- **Mandatory Customization**: Skipping Phase B leaves the adopter with kit-content masquerading as project memory. The bootstrap is not complete until Phase B is done or explicitly deferred with `[DEFERRED]`.
- **Ask, Don't Guess**: Every memory rewrite comes from an adopter answer or explicit code evidence, not from agent inference. Mark `[UNKNOWN]` per CC-003 when the adopter cannot answer yet.
- **Surgical Edits**: Update only the sections this skill names. Preserve formatting, IDs (CC-*, LH-*), and cross-file references.
- **Read-Only Archaeology**: The subagent exploration (Phase A) MUST be read-only. No source code modifications during the sweep.
- **Subagent Summaries Only**: Raw subagent output (file listings, grep output) never floods the main context. Only summary reports merge back.
- **Profile Auto-Promotion**: Record in `brownfield-map.md` under `## Profile Rules`: any feature touching a path rated `high` or `critical` MUST be promoted to `Complex` in its `status.md`.
- **No Shadow Installer**: Do not create missing harness files that `install.sh` was supposed to seed. Stop and repair the install surface instead.
- **Router Entrypoint**: `AGENTS.md` is the canonical shipped router. Downstream init seeds from that source.
- **Security Baseline**: Formulate trust boundaries in `memories/repo/core-policies.md` `## Security Policy` during bootstrap.

## Output Rules
- **Can update**: Seeded installer files (`AGENTS.md`, `memories/repo/core-policies.md`, `memories/repo/project-knowledge-base.md`, `memories/repo/learned-heuristics.md`, `docs/project/architecture.md`, `docs/project/code-map.md`, `docs/project/glossary.md`, `docs/project/tech-stack.md`, `docs/project/product-sense.md`, `docs/project/project-constraints.md`, and project-policy docs under `docs/project/*.md`).
- **Can create** (Brownfield Phase A only): `memories/repo/brownfield/brownfield-map.md`, `memories/repo/brownfield/dependency-graph.md`.
- **Cannot create**: Missing harness surface files that `install.sh` was supposed to seed; stop and repair the install surface instead.
- **Cannot create**: `spec.md`, `plan.md`, `tasks.md`.

`starter-init` creates and seeds memory files at init time. It does not overwrite non-empty versions of these files on re-init. Ongoing updates are owned by `/context-memory`.
