---
name: aiddk-memory
description: Maintain the repository's durable knowledge. This skill owns the Constitution (rules) and the Project Knowledge Base (facts), as well as the promotion of findings from feature work into durable memory.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/.
metadata:
  author: spec-driven-development-kit
---

# Kit Memory

## Overview

Use this skill to manage `memories/repo/constitution.md` and the modular **Project Knowledge Base (PKB)**.

It handles:
1. **Automated Discovery:** Scanning config files (`package.json`, `Cargo.toml`, etc.) to seed the modular PKB.
2. **Constitution:** Normative rules and guardrails.
3. **Modular PKB:** Descriptive facts organized into `TECH_STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, and `UI_GUIDELINES.md`.
4. **Promotion:** Moving temporary findings from `analysis.md` or `review.md` into the correct durable memory module.

## Read First

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md` (Index)
- Root configuration files (e.g., `package.json`, `tsconfig.json`)
- `references/constitution-template.md`
- `references/project-knowledge-base-template.md`
- `references/pkb-tech-stack-template.md`
- `references/pkb-architecture-template.md`
- `references/pkb-conventions-template.md`
- `references/pkb-ui-guidelines-template.md`

## When to Use

- Initialize AIDDK in a new repository (Discovery wave).
- Define or revise repo-wide principles (Constitution).
- Document framework versions, system design, or data flow.
- Standardize naming, style, or visual standards.

## Workflow

1. **Discovery (Optional):** If initializing or refreshing, perform a broad scan of root config files and directory structures. Automatically seed or update relevant PKB modules.
2. **Identification:** Identify a finding in feature artifacts marked as a promotion candidate.
3. **Classification:** 
   - Is it a **Rule** (Normative)? -> `constitution.md`.
   - Is it a **Fact** (Descriptive)? -> Determine the correct PKB module (Tech Stack, Architecture, Conventions, UI).
4. **Update:** Update the corresponding file. If a module doesn't exist, create it from its template.
5. **Versioning:** If updating the Constitution, bump the semantic version.

## Stop Conditions

- The finding is still temporary or speculative.
- The request is feature-local and should stay in feature artifacts.

## Core Rules

- **Normative vs. Descriptive:** Rules go in the Constitution; Facts go in the Knowledge Base.
- **Durable only:** Do not save session residue or one-off feature notes.
- **Surgical Amendments:** Prefer refining existing rules over adding overlapping ones.
- **Versioning:** Use semantic versioning for the Constitution.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Let's save every useful note here." | Repo memory should capture only durable knowledge. |
| "This one feature preference belongs here." | Feature-local guidance belongs in feature artifacts. |

## Red Flags

- Feature-local notes are being promoted into repo memory.
- Descriptive architecture notes are being written as rules.

## Verification

Before finalizing the update, verify:
- The content is durable and evidence-based.
- Normative rules were kept out of the Knowledge Base.
- Semantic version bump is appropriate for Constitution changes.

## Output Rules

- Update only `constitution.md` and `project-knowledge-base.md`.
- Do not create extra repo-memory files.
