# Documentation Conventions

Shared rules for the documentation skills (`technical-docs`, `codebase-documenter`). Each skill links here from its `Read First` section instead of restating these rules. Skill-specific rules stay in the SKILL.md file.

## Core Rules

- **Document observed behavior only.** If the code and existing docs conflict, trust the code and note the conflict.
- **No fabrication.** Do not invent file paths, sample payloads, enum values, status codes, configuration values, or behavior. If examples cannot be derived from source or trusted docs, say so.
- **Build a mental model first.** A reader should understand the system without opening implementation files first.
- **Reuse shared concepts.** Document a concept once and reference it; do not repeat the same explanation across sections.
- **Name by role.** Components and actors are named by what they do, not by filename.
- **Label uncertainty.** Mark assumptions, gaps, and open questions explicitly instead of guessing.
- **Stop on missing fundamentals.** If you cannot determine the system boundary, primary entry points, or which routes are in scope, stop and ask.

## Output Rules

- Default to Markdown.
- Keep Markdown scannable: short sections, tables where helpful, diagrams near the sections they support.
- Keep Mermaid diagrams inside fenced ```mermaid blocks.
- Order sections for onboarding: overview → visuals → workflows or endpoints → deeper reference material.

## Output Locations

Each documentation skill saves to a canonical location. Do not deviate unless the user specifies a different path.

| Skill | Feature-scoped invocation | Global / standalone invocation |
|---|---|---|
| `/technical-docs` | `--mode api` -> `artifacts/features/<slug>/api-docs.md`<br>`--mode flow` -> `artifacts/features/<slug>/flows.md`<br>`--mode both` -> `artifacts/features/<slug>/technical-docs.md` | `--mode api` -> `docs/api/<version>.md`<br>`--mode flow` -> `docs/flows/<name>.md`<br>`--mode both` -> `docs/technical-docs/<name>.md` |
| `/codebase-documenter` | *(always global)* | `docs/` root (`README.md`, `ARCHITECTURE.md`, etc.) |
| `/visualize` | `artifacts/features/<slug>/diagrams/<name>.svg` or `.mmd` | `docs/generated/diagrams/<name>.svg` or `.mmd` |

A **feature-scoped invocation** is one triggered from inside a feature lifecycle (i.e., a feature slug exists and is active in `status.md`). A **global invocation** is one triggered directly by the user with no active slug.

## Verification (shared checks)

Before finalizing, every documentation skill should verify:

- Scope and audience are explicit.
- Every claim is traceable to source code or existing trusted documentation.
- The document includes at least one valid Mermaid diagram for its primary subject.
- Supporting diagrams or structured sections add information instead of restating prose.
- Assumptions and gaps are labeled clearly.
- A reader can build a mental model without reading implementation files first.

Skill-specific verification (depth coverage, endpoint contracts, workflow grounding) lives in each SKILL.md.
