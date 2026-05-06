# Project Knowledge Base

## Purpose

Describe what stable repository knowledge this file stores and how agents should use it alongside `memories/repo/constitution.md`.

This file is not general documentation. It is durable agent memory.

Use it to store:

- stable repository facts
- reusable implementation patterns
- decision heuristics that apply across many features
- durable brownfield watchouts

Do not use it for:

- feature-specific analysis
- temporary implementation notes
- one-off debugging sessions
- speculative future design with no repository basis

## How Agents Should Use This File

- Read this file before writing `spec.md`, `plan.md`, or `tasks.md`.
- Prefer entries here over ad hoc assumptions in chat.
- Apply guidance from this file only when it is relevant to the current task.
- If a fact here conflicts with `memories/repo/constitution.md`, treat the constitution as authoritative.

## Source Of Truth Map

List the main authoritative files, directories, or systems agents should consult.

- Domain or concern:
  Source of truth:
  Why it matters:

- Domain or concern:
  Source of truth:
  Why it matters:

## Stable Invariants

Capture facts or constraints that are expected to remain true across many features.

- Invariant:
  Why it matters:
  Confidence: High | Medium | Low
  Provenance: Observed in repo | Team convention

- Invariant:
  Why it matters:
  Confidence: High | Medium | Low
  Provenance: Observed in repo | Team convention

## Decision Heuristics

Capture repeatable decision rules agents should apply when multiple implementation options exist.

- Heuristic:
  Use when:
  Avoid when:
  Why it helps:

- Heuristic:
  Use when:
  Avoid when:
  Why it helps:

## Known Good Patterns

Record patterns or reference implementations worth copying.

- Pattern:
  Use when:
  Reference:
  Notes:

- Pattern:
  Use when:
  Reference:
  Notes:

## Anti-Patterns And Forbidden Moves

Record mistakes agents should avoid repeating.

- Anti-pattern:
  Why it is harmful:
  Safer alternative:

- Anti-pattern:
  Why it is harmful:
  Safer alternative:

## Boundaries And Ownership

Describe important module or system boundaries and why they matter.

- Boundary:
  Owned by / primary area:
  Why it matters:
  Integration note:

- Boundary:
  Owned by / primary area:
  Why it matters:
  Integration note:

## Shared Dependencies And Infrastructure

- Dependency or platform:
  Why it matters:
  Watchout:

- Dependency or platform:
  Why it matters:
  Watchout:

## Durable Brownfield Watchouts

Capture stable hotspots, historical pitfalls, or areas that regularly need extra care.

- Watchout:
  Use this knowledge when:
  Impact if ignored:

- Watchout:
  Use this knowledge when:
  Impact if ignored:

## Glossary And Naming

Capture important project terms, aliases, and naming conventions agents should recognize.

- Term:
  Meaning:
  Notes:

- Term:
  Meaning:
  Notes:

## Freshness And Maintenance

- Last major refresh date:
- What kinds of changes should trigger a refresh:
- What does not belong here:

## Promotion Rules

- What belongs here:
- What should stay in feature artifacts under `artifacts/features/<slug>/`:
- What should instead go to `memories/repo/constitution.md`:
- When a finding is durable enough to promote:
- How to record confidence or provenance when evidence is partial:
