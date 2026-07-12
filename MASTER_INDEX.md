# Master Index — Lazy-Load Skeleton

## Purpose
Read this at session start to locate domain-specific indexes and memory files. Phase model (source of truth): 4 delivery phases (Spec / Plan / Implement / Verify). Bootstrap, Session START, and Memory Sync are session lifecycle steps.

## Runtime Context Pack (every session)
- `core-zero/memories/repo/core-policies.md` — only `## Purpose` and `## Normative Rules`
- `core-zero/rules/caveman.md` — communication style
- `core-zero/rules/headroom.md` — context management
- `scripts/corezero context-load` — canonical routed memory loader for agents
- `scripts/corezero context-pack` — deterministic selection, section routing, and token report without content

## Phase-Based Loading
Read `references/phase-matrix.md` for the 4×4 matrix (phase × guidance) that tells you what to add and what to stop reading at each delivery phase.

## Intent-Based Loading
Read `references/intent-keywords.md` for keyword-to-file routing. Evaluate each file individually; do not block-load groups.

## Memory Router Summary
| Tier | Files | Load Trigger |
|------|-------|--------------|
| Instruction | selected sections of `core-policies.md`, `code-design.md` | Session start; before rule changes |
| Auto | `harness-telemetry.md` | When debugging harness behavior |
| Extracted | `session-extracts.md` | During `scripts/corezero session-end` |
| Domain | `core-zero/memories/domain/*/` | When task touches that domain |

## Skill Routing
Read `MASTER_INDEX.md` only for this index. Skills declare `triggers` in `skills/*/SKILL.md` frontmatter.

## Context Assembly
Agent context loading CLI: `scripts/corezero context-load --feature <slug> --phase <phase> --intent "<keywords>" --budget 3000`
Context planning CLI: `scripts/corezero context-pack --feature <slug> --phase <phase> --json`
Session assembly CLI: `scripts/corezero session-start --feature <slug> [--phase Spec]`

## By Domain Packs

- **RAG Chat Domain** (`core-zero/memories/domain/rag/`) — Triggers: `rag`, `chat`, `citations`, `ingestion`, `grounding`, `weaviate`

