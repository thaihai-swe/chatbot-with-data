# ADR Log

<!-- Central registry of all Architecture Decision Records. /spec-adr appends new entries here when decisions are recorded. -->

## Purpose

Track all architecture decisions in one place for discoverability. Each ADR lives in `docs/project/adr/[number]-[slug].md` but is indexed here for cross-feature visibility.

## Write Contract

- **Write Authority**: Only `/spec-adr` has write authority over this index.
- **Trigger**: Append a new entry immediately when a new ADR is proposed or accepted. Do not wait for feature merge.
- **Immutability**: Past log entries are immutable. If a decision changes, create a new ADR, update its status to `Superseded`, and reference the new ADR ID.
- **Format**: All log entries must follow the exact structure defined in the `## Entry Template` section below.

## How To Use This File

- One entry per ADR. Do not edit past entries.
- Each entry links to the full ADR artifact under `docs/project/adr/[number]-[slug].md`.
- Status values: `Proposed`, `Accepted`, `Deprecated`, `Superseded`.
- `/context-memory` may read this file for architecture drift detection but does not append entries.

## Entry Template

```
### ADR-<NNN> — <Short Decision Title>

- Date: YYYY-MM-DD
- Feature slug: <slug>
- Artifact: docs/project/adr/[number]-[slug].md
- Status: Proposed | Accepted | Deprecated | Superseded
- Superseded by: <ADR-NNN or none>
- One-line summary: <What was decided and why>
```

## Status Definitions

| Status | Meaning |
|--------|---------|
| Proposed | Under discussion, not yet decided |
| Accepted | Decision made and active |
| Deprecated | No longer relevant (context changed) |
| Superseded | Replaced by a newer ADR (link to replacement) |

## Log

<!-- Append new entries below in ADR-001, ADR-002, ... order. -->
