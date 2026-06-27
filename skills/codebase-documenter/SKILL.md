---
id: skill-codebase-documenter
name: codebase-documenter
description: "Generate comprehensive codebase documentation covering architecture, components, data flow, setup, deployment, and contributing — produces a multi-file doc set."
tags: ['docs', 'architecture', 'onboarding']
triggers: ['documentation', 'codebase', 'architecture', 'readme']
next_skill: ''

---
# Codebase Documenter



## Overview

Produces a multi-file Markdown documentation set (README, ARCHITECTURE, COMPONENTS, etc.) explaining how a codebase is organized and how to onboard onto it. Grounds all claims in source code.

## When to Use (vs. Others)

- **Use `/codebase-documenter`** for repo onboarding: setup, directories, build commands, and contributing guides.
- **Use `/technical-docs --mode flow`** for event/transaction workflow narratives (2-5 core flows).
- **Use `/technical-docs --mode api`** for HTTP route inputs and outputs.

## Read First

- `memories/repo/core-policies.md` and `memories/repo/project-knowledge-base.md`
- Root config and package/build files (`package.json`, `pom.xml`, etc.).
- References: `references/templates.md`, `references/best-practices.md`, `references/diagram-patterns.md`, `../_shared/doc-conventions.md`, and `../_shared/diagram-catalog.md`.

## I/O Hand-off Protocol

### Inputs
- Repository root path and project structure
- `memories/repo/core-policies.md` and `memories/repo/project-knowledge-base.md`

### Outputs
- Multi-file documentation set: README.md, ARCHITECTURE.md, COMPONENTS.md, DEVELOPMENT.md, DEPLOYMENT.md, CONTRIBUTING.md
- Output directory determined by user or default to `docs/`

### Next Skill
None (terminal — documentation is consumed by developers directly)

## Workflow

1. **Scope & Depth**:
   - `Quick`: Produce `README.md` and `ARCHITECTURE.md` only. No component-level deep dives. Use when the user needs a fast orientation.
   - `Moderate` (default): All 6 output files (README.md, ARCHITECTURE.md, COMPONENTS.md, DEVELOPMENT.md, DEPLOYMENT.md, CONTRIBUTING.md). Moderate component depth.
   - `Deep`: All 6 files plus: inline code walkthrough for 2–3 key flows, test coverage map, and a runnable onboarding validation script. Use when new team members need hands-on depth.

   If the user does not specify, default to `Moderate`.
2. **Explore**: Map folders, dependencies, and main entry points.
3. **Trace**: Trace key execution flows through code to construct mental models.
4. **Document**: Write separate Markdown pages using templates. Embed system architecture diagrams. Provide real code snippets with `file:line` references.
5. **Verify**: Before finalizing:
   - Run `grep -rI 'TODO\|PLACEHOLDER\|TBD' <output-dir>` — any hit is a verification failure. Fix or document it explicitly.
   - Confirm every command in `DEVELOPMENT.md` is syntactically valid shell. If a `Makefile` or `package.json` exists, cross-check command names against their definitions.
   - Confirm every directory listed in `ARCHITECTURE.md` or `COMPONENTS.md` matches the actual filesystem layout (`ls` or `find` to verify).

### Update Mode

When output files already exist (e.g., a prior `codebase-documenter` run):
1. Read existing output files.
2. Diff their content against the current codebase structure (directories, key entry points, main dependencies).
3. Update only sections where the code has changed. Preserve developer-authored additions in non-generated sections (e.g., custom tips in CONTRIBUTING.md).
4. Increment a `<!-- Last updated: YYYY-MM-DD -->` comment at the top of each modified file.
Do not regenerate from scratch unless explicitly requested.

## Required Coverage (10 Areas)

1. Project purpose.
2. High-level architecture patterns.
3. Folder structure.
4. Key component responsibilities.
5. External dependencies.
6. Data models/schemas.
7. Development setup/prerequisites.
8. Coding conventions.
9. Deployment pipelines.
10. Contributing guidelines.

## Diagram Preferences

- Layered architecture diagram showing system structure.
- Supporting sequence flow, ERD, or microservices maps per `../_shared/diagram-catalog.md` and `references/diagram-patterns.md`.

## Output Rules

- Follow `../_shared/doc-conventions.md` rules.
- Multi-file output format (README.md, ARCHITECTURE.md, COMPONENTS.md, DEVELOPMENT.md, DEPLOYMENT.md, CONTRIBUTING.md).
- Setup instructions must be actionable with exact commands.
- Verify that a fresh developer can onboard using the docs.

## Stop Conditions

- Codebase is unreadable or access-denied.

## Core Rules

- Ground all claims in source code. Do not guess structure.



## Verification

- [ ] No `TODO` or `PLACEHOLDER` strings remain in output files.
- [ ] Every directory listed in ARCHITECTURE.md exists on disk.
- [ ] Every command in DEVELOPMENT.md is valid shell syntax.
- [ ] Setup steps can be followed sequentially to reach a runnable state.
- [ ] CONTRIBUTING.md includes at minimum: how to run tests, how to submit a change, and code style references.
- [ ] At least one architecture diagram is embedded and current.
