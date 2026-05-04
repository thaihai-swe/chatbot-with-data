---
name: constitution
description: Create or maintain memories/repo/constitution.md as the repository’s durable normative rule set. Use when updating repo-wide principles, quality gates, architectural guardrails, or agent operating constraints that should govern future work across many changes.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/.
metadata:
  author: spec-driven-development-kit
---

# Constitution

## Overview

Use this skill to create or maintain `memories/repo/constitution.md`.

This skill governs durable repository-wide rules. It is for normative guidance, not descriptive repository facts.

## Read First

Read these inputs when they exist:

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- relevant feature artifacts
- relevant repository files that provide direct evidence
- `references/constitution-template.md`

## When to Use

Use this skill when the user needs to:

- define or revise repo-wide principles
- add durable quality gates or delivery rules
- tighten architectural guardrails
- clarify how future agents should operate across the repository
- capture or revise the repository's effective AI contract inside the constitution

Do not use this skill for:

- feature-specific decisions
- temporary workarounds
- one-off delivery preferences
- descriptive current-state notes better suited for the project knowledge base

If the finding is durable but descriptive, route to `project-knowledge-base` or use `memory-promotion` first.

## Stop Conditions

Stop and explain what blocks a safe amendment when:

- the proposed change is really a feature-local note or temporary preference
- repository evidence is too weak to justify a durable rule
- the request is descriptive context rather than a normative guardrail

When stopping, say:

- what the candidate change appears to be
- why it does not belong in the constitution yet
- which adjacent skill or artifact should own it instead

## Core Rules

- Keep the constitution normative rather than descriptive.
- Prefer refining existing `CC-*` rules over adding overlapping new ones.
- Preserve stable identifiers and explain version bumps when the meaning changes.
- Route descriptive durable knowledge to `project-knowledge-base` instead of encoding it as a rule.
- Treat downstream doc and adapter alignment as follow-up work after the rule change, not as a substitute for it.

## Amendment Rules

- Amend only when the rule is repo-wide, durable, and evidence-based.
- Prefer refining existing rules over adding new ones.
- Preserve stable identifiers such as `CC-###`.
- Merge duplicates instead of creating overlapping principles.
- Remove or rewrite content that is descriptive instead of normative.

Do not amend the constitution for one-off preferences or unresolved debates.

## Versioning

Use semantic versioning for the constitution:

- `MAJOR` for backward-incompatible governance changes
- `MINOR` for new principles or materially expanded guidance
- `PATCH` for clarifications and non-semantic refinements

If the bump is ambiguous, explain the reasoning before finalizing it.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We should just add another rule to be safe." | The constitution should stay durable and minimal, not become a dumping ground. |
| "This one feature preference belongs here." | Feature-local guidance should stay in feature artifacts unless it is truly repo-wide. |
| "The docs already say it, so the constitution can stay stale." | The constitution is the durable rule source, not a mirror of downstream prose. |

## Red Flags

- descriptive architecture notes are being written as rules
- new rules overlap existing `CC-*` items instead of refining them
- the requested change would be better stored in `project-knowledge-base.md`

## Verification

Before finalizing the constitution, verify:

- the amendment is repo-wide, durable, and evidence-based
- stable identifiers remain coherent
- the semantic version bump is explained and appropriate
- no unexplained placeholders remain
- related skills, adapters, or docs that depend on the rule have been identified

## References

- Use [references/constitution-template.md](references/constitution-template.md) as the bundled structure.
- Ensure placeholder tokens are fully replaced with concrete text.
- Keep rules declarative, testable, and action-oriented.
- Treat the constitution as the canonical home for non-negotiable AI operating rules instead of creating a separate `AI_CONTRACT.md`.

## Workflow

1. Load the current constitution and identify placeholders, gaps, or stale rules.
2. Gather evidence from repository context, durable patterns, and explicit user direction.
3. Decide whether an amendment is warranted and what version bump it requires.
4. Update the constitution while preserving stable IDs and heading structure where practical.
5. Check whether related templates or agent contracts may need follow-up because the rules changed.
6. Validate that no unexplained placeholders remain and that dates and versioning are coherent.

## Output Standard

The constitution is ready only when it:

- contains durable repo-wide rules
- is normative rather than descriptive
- uses stable identifiers consistently
- is self-sufficient for future agents without chat history
- reflects an appropriate semantic version bump when changed

## Output Rules

- Update only `memories/repo/constitution.md`.
- Do not create extra repo-memory files.
- If no durable amendment is warranted, say so plainly instead of forcing a change.
