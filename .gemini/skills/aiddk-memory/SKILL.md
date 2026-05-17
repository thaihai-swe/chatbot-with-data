---
name: aiddk-memory
description: Create, maintain, and route durable repository memory. Manage constitution.md (repo-wide rules), project-knowledge-base.md (durable facts), and decide where findings belong. Use when capturing stable patterns, defining governance rules, or classifying findings that deserve to outlive a single feature.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Kit Memory

## Overview

Use this skill to manage durable repository memory across three functions:

1. **Constitution** - Repo-wide normative rules (CC-* identifiers)
2. **Project Knowledge Base** - Durable descriptive facts, patterns, boundaries
3. **Memory Promotion** - Route findings to the right destination (constitution, knowledge base, or feature artifacts)

This skill is the gateway to durable team memory. It decides what survives beyond a single feature and how to organize it.

## Read First

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- relevant feature artifacts or review outputs
- relevant repository files and code paths
- `references/constitution-template.md`
- `references/project-knowledge-base-template.md`
- `references/decision-template.md`

## When to Use

Use this skill when you need to:

- **Create or amend constitution.md**: Define repo-wide principles, quality gates, guardrails, or agent operating constraints
- **Create or maintain project-knowledge-base.md**: Document recurring patterns, boundaries, architecture notes, integration seams, brownfield watchouts
- **Route findings**: Decide whether a finding should become durable repo memory, and if so, to which file
- **Promote lesson learned**: Capture knowledge from analysis, implementation, review, or cleanup for future reuse
- **Review repo memory**: Ensure constitution and knowledge base remain accurate, durable, and non-overlapping

Do not use this skill for:

- Writing feature-specific artifacts (`spec.md`, `plan.md`, `tasks.md`)
- Temporary findings or session notes
- Speculative future design with no repository basis
- Post-implementation code review (use `aiddk-verify` for that)

## Workflow

### Part 1: Memory Promotion (Classify Findings)

When a finding emerges from analysis, implementation, review, or cleanup:

1. **Identify the finding** and its source artifact
2. **Check durability**: Is this evidence-based, stable, and likely useful beyond this feature?
3. **Classify**: Is it a repo-wide rule (normative), a durable pattern (descriptive), or still feature-local?
4. **Route**:
   - **Normative rule** -> `constitution.md` (repo-wide principle, quality gate, guardrail)
   - **Durable pattern** -> `project-knowledge-base.md` (recurring implementation pattern, boundary, watchout)
   - **Still local** -> Keep in feature artifacts until future features need it
5. **Explain** why the finding belongs in the chosen destination

### Part 2: Constitution Management (Repo-Wide Rules)

When updating `memories/repo/constitution.md`:

1. **Load current constitution** and identify gaps, stale rules, or placeholders
2. **Gather evidence** from repository patterns, explicit user direction, or team agreements
3. **Decide amendment**: Is a change warranted? What version bump does it require?
4. **Amend carefully**:
   - Use stable identifiers (CC-*)
   - Keep rules normative, not descriptive
   - Merge duplicates instead of creating overlapping principles
   - Preserve heading structure and semantic versioning
5. **Verify**: No unexplained placeholders, dates coherent, version bump justified

**Amendment Rules**:
- Amend only when the rule is repo-wide, durable, and evidence-based
- Prefer refining existing CC-* rules over adding new ones
- Preserve stable identifiers
- Route descriptive knowledge to `project-knowledge-base.md` instead

**Stop Conditions**:
- The proposed change is feature-local (keep in feature artifacts)
- Repository evidence is weak
- The content is descriptive, not normative (route to `project-knowledge-base.md`)

### Part 3: Project Knowledge Base (Durable Facts)

When updating `memories/repo/project-knowledge-base.md`:

1. **Read current knowledge base** and understand existing sections
2. **Assess durability**: Is this stable, evidence-based, and useful for future work?
3. **Integrate**:
   - Merge into existing sections where possible (avoid duplication)
   - Create concise new sections only when a clear boundary emerges
   - Capture patterns, watchouts, architecture notes, decision history
   - Include confidence level or provenance if evidence is partial
4. **Remove duplication** and keep the file concise
5. **Verify**: Content is durable, descriptive (not normative), and reusable

## Stop Conditions

- The finding is still speculative or weakly evidenced
- The content is really a repo-wide rule (route to `constitution.md`)
- The note is feature-local and belongs in feature artifacts

## Core Rules

- **Normative vs. Descriptive:** Rules go in the Constitution; facts go in the Knowledge Base
- **Durable only:** Do not save session residue or one-off feature notes
- **Surgical Amendments:** Prefer refining existing rules over adding overlapping ones
- **Versioning:** Use semantic versioning for the Constitution
- **Evidence first:** Promote only what the repository or artifacts can support
- **Concise memory:** Merge overlaps and store the reusable summary, not raw notes

## Rationalization vs. Reality

| Rationalization | Reality |
|---|---|
| "I'll remember this without writing it down." | Human (and AI) memory is volatile. Documentation is the permanent storage for institutional knowledge. |
| "It's just a one-off setup detail." | Today's 'one-off' is tomorrow's blocker for a teammate. |
| "Updating the PKB takes too long." | The cost of 'discovering' the same fact twice is always higher than the cost of documenting it once. |

## Red Flags
- Descriptive architecture notes are written as rules
- New rules overlap existing CC-* items instead of refining them
- Temporary workarounds are being promoted as durable knowledge
- Normative language creeps into descriptive sections
- Feature-local notes are being promoted without clear reuse signal

## Verification

Before finalizing any change:

- [ ] Amendment is repo-wide, durable, and evidence-based (or explicitly feature-local)
- [ ] Normative rules are in constitution; descriptive facts in knowledge base
- [ ] Stable identifiers remain coherent (CC-*, section headings)
- [ ] No unexplained placeholders remain
- [ ] Semantic version bump is justified
- [ ] Overlapping sections were merged, not duplicated
- [ ] Future agents can understand the memory without chat history

## Output Standard

Memory is ready only when it:

- Contains durable repo-wide knowledge (constitution) or reusable patterns (knowledge base)
- Separates normative rules from descriptive facts
- Is grounded in repository evidence
- Uses stable identifiers and structure
- Remains concise and decision-forward

## Output Rules

- Update only `memories/repo/constitution.md` or `memories/repo/project-knowledge-base.md`
- Do not create extra repo-memory files
- Route findings to the owning skill with a short reason
- If no durable update is warranted, say so plainly
- Preserve heading structure and identifier stability when amending

## References

- [references/constitution-template.md](references/constitution-template.md) - Constitution structure
- [references/project-knowledge-base-template.md](references/project-knowledge-base-template.md) - Knowledge base structure
- [references/decision-template.md](references/decision-template.md) - Decision record shape for complex promotions
