# Deprecated Heuristics Archive

## Purpose
Cold storage for learned heuristics that decayed out of active use.
Entries preserve their original LH-* IDs for traceability. An entry
here is not deleted knowledge — it is knowledge that was not cited
in recent feature work and may be revived if the pattern recurs.

## Archived Entries

<!-- Entries appended by /context-memory decay action. -->
<!-- Each entry retains: LH-NNN, Trigger, Working heuristic, Evidence, -->
<!-- Confidence, Last reviewed, Original status, Archive date, Archive reason. -->

### LH-004: Agent tends to overscaffold when starting new files
- Trigger:
  - agent creates a new file or module for the first time in a session
- Working heuristic:
  - check existing files of similar type before writing; match their structure, not a generic template. Prefer the smallest file that satisfies the task over a boilerplate scaffold.
- Evidence:
  - repeated over-generation of boilerplate sections that the codebase never uses (e.g., full docstrings, empty method stubs, placeholder configs)
- Confidence: High
- Last reviewed: 2026-06-20
- Original status: **[PROMOTED]** Added to `docs/policies/code-design.md`
- Archive date: 2026-06-25
- Archive reason: Promoted to normative code-design.md rule; original heuristic superseded by normative requirement.

### LH-008: Domain packs are ignored when building new features
- Trigger:
  - agent implements a feature that touches a domain with an installed pack but does not load it
- Working heuristic:
  - during `/spec-research` and `/spec-requirements`, explicitly check if the task keywords match any domain pack triggers in `MASTER_INDEX.md` `## By Domain Packs`. If a match exists, load the pack before writing the spec.
- Evidence:
  - features built without loading domain packs repeated patterns that were already captured in the pack, or violated boundary rules
- Confidence: High
- Last reviewed: 2026-06-20
- Original status: **[PROMOTED]** Added as a MUST rule in `spec-requirements/SKILL.md`
- Archive date: 2026-06-25
- Archive reason: Promoted to normative spec-requirements SKILL.md rule; original heuristic superseded by MUST requirement.
