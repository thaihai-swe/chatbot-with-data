---
id: skill-spec-adr
name: spec-adr
description: "Create or evaluate an architecture decision record (ADR). Use when choosing between technologies, documenting design trade-offs, or reviewing system proposals. This skill ensures decisions are recorded with context, trade-offs, and long-term consequences."
tags: ['spec', 'decision', 'architecture']
triggers: ['adr', 'decision', 'architecture decision']
next_skill: ''

---
# Kit ADR

## Overview
Record significant architectural decisions.
## When to Use
- **Technology Choices:** Choosing between Kafka vs SQS, React vs Angular, etc.
- **Design Trade-offs:** Documenting why a specific architectural pattern was chosen over another.
- **System Proposals:** Reviewing and refining new component designs.
- **Refactoring Decisions:** Documenting major structural changes and their rationale.
## I/O Hand-off Protocol
- **Reads**: Codebase context, `docs/rules/ponytail.md`.
- **Writes**: `docs/project/adr/[number]-[slug].md` (new file) and `memories/repo/adr-log.md` (append entry via Write Contract).
- **Next Skill**: Return to previous skill (e.g., `/spec-plan` or `/spec-implement`).

## Workflow
1. **Identify Decision Needs**: Note when tech choices, structural shifts, design tradeoffs, or major refactorings require a durable architectural record.
2. **Evaluate Alternatives**: Research and evaluate at least two options. Analyze them against complexity, cost, scalability, and team familiarity dimensions.
3. **Draft Decision Record**: Author the ADR document under `docs/project/adr/[number]-[slug].md` using `references/adr-template.md` (or the lightweight format for minor decisions).
4. **Append to Log Ledger**: Update `memories/repo/adr-log.md` by appending a structured entry using the format defined in `## Entry Template`.
5. **Update Central Registry**: Add the decision to the index table in `docs/project/adr/index.md` to maintain cross-feature visibility.

## Core Rules
- **Comparative Analysis:** Always include at least two options with pros and cons.
- **Traceability:** Link ADRs to `spec.md` when writing during the spec phase. Link to `plan.md` only when the planning phase has completed and the plan exists.
- **Immutability:** Once "Accepted," ADRs should be superseded or deprecated, not deleted or significantly altered.
- **Surgical Scope:** Focus on the architectural decision, not the implementation details.

## Read First

Read this skill thoroughly before invoking it.
