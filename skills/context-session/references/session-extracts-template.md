# Session Extracts: [Feature Name]
<!-- triaged: false -->

Extracted-tier memory. Per-feature distillation of session lessons that *might* be worth promoting into durable repo memory. Generated at `context-session END` as candidates only — nothing here is durable until `context-memory` triages it.

## How To Use This File

- `context-session END` appends candidates to this file. Do not edit candidates from prior sessions; append new ones.
- Each candidate is a hypothesis, not a rule. Weak signal goes here so it does not bloat instruction-tier memory.
- `context-memory` reads this file and decides per candidate: **promote**, **defer**, or **discard**.
- Promoted candidates are removed from the `## Pending Candidates` section and recorded under `## Triaged` with their destination.
- Discarded candidates are recorded under `## Triaged` with `discarded` and a one-line reason. Do not delete them — the trail matters.

## Candidate Categories

When appending, classify the candidate so triage is fast:

- **Heuristic** — a repeatable execution pattern that worked. Likely promotion: `learned-heuristics.md`.
- **Pattern** — a durable code or architecture observation. Likely promotion: `project-knowledge-base.md`.
- **Rule** — a normative constraint the team should follow. Likely promotion: `core-policies.md`.
- **Security** — a permission, trust, or sandbox observation. Likely promotion: `core-policies.md` `## Security Policy`.
- **Harness gap** — the environment allowed a mistake. Likely promotion: `harness-telemetry.md` (auto tier) for further analysis.
- **Spec gap** — the requirement was ambiguous. Likely action: route back to `spec-requirements`.

## Pending Candidates

<!-- Append new candidates here at session END. Format below. -->

```
### EXT-<NNN> — <one-line summary>

- Session: YYYY-MM-DD <session label or handoff filename>
- Category: Heuristic | Pattern | Rule | Security | Harness gap | Spec gap
- Confidence: Low | Medium | High
- Evidence: <link to specific lines in review.md, progress.md, or commit>

**Observation**
<2-3 sentences. What the agent noticed during the session.>

**Why it might be durable**
<Why this could matter beyond this feature. Be honest about uncertainty.>

**Suggested destination**
<File path the candidate would belong in if promoted.>
```

## Triaged

<!-- context-memory moves processed candidates here. Format: -->

<!--
- EXT-001 — promoted to memories/repo/learned-heuristics.md (LH-014). Rationale: pattern observed in 3+ sessions.
- EXT-002 — discarded. Rationale: feature-local, not generalizable.
- EXT-003 — deferred. Rationale: needs one more confirming session before promotion.
-->
