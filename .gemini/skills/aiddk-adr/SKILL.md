---
name: aiddk-adr
description: Create or evaluate an architecture decision record (ADR). Use when choosing between technologies, documenting design trade-offs, or reviewing system proposals. This skill ensures decisions are recorded with context, trade-offs, and long-term consequences.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories.

---

# Kit ADR

## Overview
This skill manages the creation, evaluation, and logging of Architecture Decision Records (ADRs). It ensures that technical decisions are not just made, but documented with their full context and trade-offs for future maintainers.

**Non-Goals:**
- This is not a replacement for `aiddk-plan` (implementation strategy).
- This is not for recording meeting minutes or general project notes.

## When to Use
- **Technology Choices:** Choosing between Kafka vs SQS, React vs Angular, etc.
- **Design Trade-offs:** Documenting why a specific architectural pattern was chosen over another.
- **System Proposals:** Reviewing and refining new component designs.
- **Refactoring Decisions:** Documenting major structural changes and their rationale.

**Routing:**
- For implementation steps and task breakdown, use `/aiddk-plan`.
- For low-level code implementation, use `/aiddk-implement`.

## Read First
- `artifacts/features/<slug>/status.md`
- `artifacts/features/<slug>/adr-*.md`
- `memories/repo/adr-log.md`
- `skills/aiddk-adr/references/adr-template.md`

## Workflow
1. **Context Check:** Read `status.md` to identify the current phase and any blockers related to the decision.
2. **Gather Context:** Identify the problem, constraints, and forces at play.
3. **Identify Options:** List at least two viable alternatives.
4. **Comparative Analysis:** Evaluate each option against dimensions like Complexity, Cost, Scalability, and Team Familiarity.
5. **Draft ADR:** Use `adr-template.md` to document the decision, trade-offs, and consequences.
6. **Update Log:** Append the new ADR reference to `memories/repo/adr-log.md`.
7. **Finalization:** Update `status.md`. If this ADR was a blocker, mark it as resolved.

## Stop Conditions
- Required constraints (e.g., budget, RPS, deadline) are missing or ambiguous.
- No viable alternatives are considered (avoid "the only way" thinking).
- The decision requires input from a stakeholder who hasn't been consulted.

## Core Rules
- **Comparative Analysis:** Always include at least two options with pros and cons.
- **Traceability:** Link ADRs to relevant `spec.md` or `design.md` files.
- **Immutability:** Once "Accepted," ADRs should be superseded or deprecated, not deleted or significantly altered.
- **Surgical Scope:** Focus on the architectural decision, not the implementation details.

## Rationalization vs. Reality

| Rationalization | Reality |
|---|---|
| "It's too small for an ADR." | Small decisions compound into big technical debt. |
| "Everyone agreed in chat, no need to document." | Chat logs are not architectural history. New team members shouldn't have to search Slack to understand why a choice was made. |
| "I'll write the ADR after I'm done with the implementation." | Post-hoc documentation often omits the alternatives considered and the 'why' behind the chosen path. |

## Red Flags
- The ADR lacks a "Consequences" section (everything has a cost).
- "Team Familiarity" is the only reason for a decision.
- The "Context" section is too vague to understand the original problem.

## Verification
- Verify that at least two options were assessed.
- Ensure "Consequences" (both positive and negative) are explicitly listed.
- Confirm the ADR is added to the central `adr-log.md`.

## Output Rules
- Update or create `artifacts/features/<slug>/adr-[number].md`.
- Update `memories/repo/adr-log.md`.
- Do not modify `spec.md` or `plan.md` (only link to them).
