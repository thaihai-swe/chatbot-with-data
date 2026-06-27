---
id: skill-spec-requirements
name: spec-requirements
description: "Define the 'What & Why' of a feature. Handles specification authoring, Socratic refinement to resolve ambiguity, and a built-in readiness review to ensure requirements are testable and complete before planning."
tags: ['spec', 'requirements', 'analysis']
triggers: ['requirement', 'spec', 'feature']
next_skill: 'spec-plan'

---
# Kit Spec
## Routing Guide

- **Use `/spec-requirements`** to define requirements and acceptance criteria.
- **Use `/spec-research`** first if the problem space, bug root cause, or brownfield codebase state is unknown.

## Overview
Create or refine `status.md`, `proposal.md`, `spec.md`, and (if issues are found) `requirements-review.md` in `artifacts/features/<slug>/`. This skill aligns the team on what is being built and how it will be verified.

## I/O Hand-off Protocol
- **Reads**: `artifacts/features/<slug>/analysis.md` (if exists), `artifacts/features/<slug>/status.md`, `memories/repo/adr-log.md`, domain packs.
- **Writes**: `artifacts/features/<slug>/spec.md`, `artifacts/features/<slug>/status.md`, `artifacts/features/<slug>/proposal.md`, optional `artifacts/features/<slug>/requirements-review.md`.
- **Next Skill**: `/spec-plan`

## When to Use

- Define a new feature, change request, or initiative.
- Refine existing specifications.
- Resolve ambiguity before design/planning.

## Workflow

1. **Initialization**: Create `status.md` if missing (from `_shared/status-template.md`). Set phase to `Spec'ing`.
2. **Intake & Routing**: Classify input type (`new_spec`, `spec_slice`, `change_request`, `new_initiative`, `maintenance`, `harness_improvement`) and risk flags in `status.md` per `references/intake.md`.
    - **System Spec Mode**: If the request is cross-cutting or system-wide, switch to System Spec Mode. Output target becomes `docs/system-specs/<name>.md`.
3. **Context Alignment**:
    - **Domain Pack Scan**: If any keyword from the feature description matches a domain pack trigger in `memories/domain/<name>/glossary.md` frontmatter, you MUST load that pack before writing the spec and note it in `status.md`.
    - **Analysis Check**: Read `artifacts/features/<slug>/analysis.md` (if exists) and record open research questions.
    - **Domain Spec Check**: If `memories/repo/domain-specs.md` exists, read relevant domain specs.
    - **ADR Conflict Check**: Load `memories/repo/adr-log.md`. Verify the proposed spec does not contradict locked decisions. If a contradiction exists, insert `[ADR CONFLICT: ADR-NNN — <decision summary>]` and block Handoff.
4. **Clarification (Grilling Phase)**: Do NOT guess missing details. Engage in a relentless interview (Socratic refinement) to resolve decision trees and eliminate ambiguity before writing the spec. Never just mark items as `[UNKNOWN]` and move on. Ask batch clarifying questions with recommended answers per `references/grilling-waves.md`. If answers remain contradictory after 2 rounds, write `[UNRESOLVED: <description>]` and stop.
5. **Complexity Classification**: Evaluate the scope of the work and update `status.md` with one of the following:
    - **Simple**: One area of the codebase, no new integrations, no data model changes, clear spec.
    - **Moderate**: Multiple areas OR one external integration OR schema change.
    - **Complex**: Cross-cutting, multiple integrations, or unknown dependencies.
6. **Proposal & Scope Definition**: Draft `proposal.md` to align scope before spec'ing. Explicitly list `In Scope`, `Out Of Scope`, and `Non-Goals`.
   - **Skip for Simple**: If Complexity is Simple, skip generating `proposal.md` entirely.
7. **Spec Authoring**: Draft `spec.md` (`what` & `why`) using `references/spec-template.md`. Record key gray-area design/UX choices. Define testable, observable acceptance criteria (AC-*) using strict markdown checklists or Gherkin. Specify verification surfaces (unit, integration, manual check).
   - **Simple**: The spec.md serves as the single alignment doc.
   - **Complex**: If uncertainty is high during spec authoring, trigger `/spec-research`.
    - **AC Protocol**: Every AC MUST have a verification command or script reference. Use `bash scripts/harness/gate-runner.sh ...` as the proof mechanism.
    - **NFR-AC Linkage**: Every non-functional requirement (performance, security, scalability) MUST link to at least one AC. Add a `Linked ACs:` field after each NFR block in the spec.
    - **Gherkin ACs**: When using Gherkin format, every scenario MUST include all three clauses (Given, When, Then). Avoid non-deterministic Then clauses (e.g., "it works", "the system should") — each Then MUST be an observable assertion.
8. **Completeness Check**: Ensure NO `[NEEDS CLARIFICATION]`, `[UNRESOLVED]`, or `[ADR CONFLICT]` tags remain. Conduct a requirements review using `references/requirements-review-template.md`. Only create `requirements-review.md` if issues or gaps are found; do NOT create the artifact if the review passes.
9. **Handoff**: Run `bash scripts/harness/phase-gate.sh <slug> "Spec Approved"` to verify preconditions. If it fails, fix the root cause before proceeding. Update `status.md` phase to `Spec Approved`, ensure the `Spec approved` checkbox under High-Level Progress is marked `[x]`, and route to `/spec-plan`.

## Anti-Patterns

- **Ambiguous ACs**: Writing "system should work" instead of binary pass/fail criteria. Every AC must be provable with a command.
- **Isolated NFRs**: Listing performance/security requirements without linking them to specific ACs.
- **Implementation Leakage**: Writing "use Redis for caching" in the spec. Spec is What/Why, not How — that belongs in plan.md.
- **Silent Scope Creep**: Adding requirements during clarification that weren't in the original request. Log scope changes in `status.md` and confirm with the user.
- **Premature Spec'ing**: Writing the spec before the grilling phase is complete. Every `[UNKNOWN]` is a risk.

## Core Rules
- **Anti-Hallucination**: Never invent plausible but unspecified business logic. Mark all unknowns explicitly.
- **What, not How**: Focus on requirements, not technical implementation.
- **Validation-Aware**: Every acceptance criterion must be testable.
- **Deterministic ACs**: ACs must be binary (pass/fail) and clearly mapped to a verification command or script.
- **NFR-AC Binding**: Every non-functional requirement MUST reference at least one acceptance criterion.
