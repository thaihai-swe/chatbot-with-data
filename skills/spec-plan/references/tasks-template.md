# Task Breakdown

## Metadata

- Feature name:
- Related spec / plan / design:
- Owner:
- Last updated:

## Rules

- Keep tasks proportional to delivery profile; Simple stays compact.
- Each task small, testable, and traceable to REQ/AC/plan.
- Mark `[P]` only when truly independent (no write/contract conflicts); state ownership boundary.
- Prefer explicit file/module targets when known.
- First unblocked task must be executable from this file alone.
- Task states: `Not Started` | `In Progress` | `Blocked` | `Done` | `Deferred`.
- Behavior-changing tasks: name the failing proof/test expected before the fix (TDD: RED → GREEN).
- Don't finalize until REQ → AC → TASK → validation coverage is complete.

## User Story Decomposition

Required for Moderate and Complex when the feature has more than one user story. Skipped for Simple and single-story features (record `US-001 (P1) — covers all tasks` and proceed).

Group tasks into independently shippable slices. Each story slice must be:

- **Independently testable** — its proving commands run without depending on later slices.
- **Independently shippable** — releasing only this slice produces a useful, complete outcome.
- **Priority-tagged** — `P1` ships first (MVP must-have), `P2` ships next, `P3` is follow-up.

Cross-slice dependency rule: a `P2` task may depend on `P1` tasks; a `P3` task may depend on `P1` or `P2` tasks; never the reverse. Setup and Foundational phases are not stories — they have no priority lane and no `User story:` linkage.

| Phase | Purpose | Story | Ships independently |
|---|---|---|---|
| Setup | Project scaffolding, dependency install, CI wiring | n/a | no |
| Foundational | Shared infra all stories depend on | n/a | no |
| Story P1: <name> | First MVP-shippable behavior | US-001 | yes |
| Story P2: <name> | Next slice | US-002 | yes (with P1 deployed) |
| Story P3: <name> | Follow-up slice | US-003 | yes (with P1 + P2 deployed) |
| Polish | Docs, perf, observability cleanup | n/a | no |

Adjust phase count to the feature — drop unused rows, add stories as needed.

## Implementation Strategy

Required when User Story Decomposition is filled. Pick one strategy and record the reason. The choice guides ordering and review pacing.

| Strategy | When to use | Effect |
|---|---|---|
| MVP-first | Moderate/Complex with multiple stories where the team wants to ship as soon as P1 is verified | Complete and verify P1 (including its tests) before any P2 work begins; each story is a separate ship gate |
| Incremental | Stories tightly coupled or built sequentially against the same module | Run all P1 tasks, then all P2, then all P3; one final verification covers the feature |
| Parallel-team | Subagent or multi-developer slices with clean ownership boundaries | After Foundational completes, stories run concurrently; each slice owns its boundary and verifies itself |

```
Selected strategy: <MVP-first | Incremental | Parallel-team>
Reason: <one line>
```

## Heuristic Citations

*Optional. Cite any LH-* IDs applied in the design or execution of these tasks.*
- LH-NNN: <brief description>

## Task Block Format

Every task uses this canonical block. Repeat per task; assign sequential `TASK-NNN` IDs grouped under phases.

```
- [ ] TASK-NNN
  Status: Not Started                # Not Started | In Progress | Blocked | Done | Deferred
  Routing: AFK                       # AFK = unsupervised mechanical | HITL = human checkpoint required
  Summary:
  Outcome enabled:                   # link to user scenario or outcome when relevant
  Plan reference:                    # plan phase or task this came from
  Linked requirement(s):             # REQ-XXX
  Linked acceptance criteria:        # AC-XXX
  User story:                        # US-XXX (P1|P2|P3) — empty for Setup/Foundational/Polish
  Ownership boundary:                # required if [P]
  Affected file(s) or module(s):
  Depends on:                        # other TASK-IDs
  Can run in parallel:               # yes/no; if yes, also fill Ownership boundary
  Proving command or proof:          # exact command, test, scenario, or log
  Validation evidence:               # filled after run; passing output or pointer
  Session note:                      # blockers, progress, HITL checkpoint description
```

`[ ]` toggles to `[X]` when `Status: Done`. Implementation agent must keep checkbox and Status aligned.

## Phases

Default scaffold — adjust phase count and goals to the plan. Story IDs and priorities come from `spec.md` `## User Stories And Key Scenarios`.

### Phase 1: Setup
Goal:
Completion criteria:
- [ ] CC-001
Tasks:
- [ ] TASK-001 …  (use the block above; leave `User story:` empty for setup tasks)

### Phase 2: Foundational
Goal:
Completion criteria:
- [ ] CC-002
Tasks:
- [ ] TASK-… …

### Phase 3: User Story P1 — <Story ID + short label>
Goal:
Story ID:                                # US-XXX
Priority: P1
Acceptance criteria covered:             # AC-XXX, AC-XXX
Independent proof:                       # exact command(s) that pass once this phase ships
Completion criteria:
- [ ] CC-003 All AC-XXX in this story map to a Done task.
- [ ] CC-004 Independent proof passes with later user-story phases absent.
Tasks:
- [ ] TASK-… … (`User story:` must be set on every task in this phase)

### Phase 4: User Story P2 — <Story ID + short label>
*Optional for the MVP cut. Repeat the P1 block format.*
Goal:
Story ID:                                # US-XXX
Priority: P2
Acceptance criteria covered:
Independent proof:
Completion criteria:
- [ ] CC-005
- [ ] CC-006
Tasks:
- [ ] TASK-… …

### Phase 5: User Story P3 — <Story ID + short label>
*Optional. Repeat the P1 block format.*
Goal:
Story ID:                                # US-XXX
Priority: P3
Acceptance criteria covered:
Independent proof:
Completion criteria:
- [ ] CC-007
- [ ] CC-008
Tasks:
- [ ] TASK-… …

### Phase N: Polish
Goal:
Completion criteria:
- [ ] CC-NNN No new behavior; touched files only.
Tasks:
- [ ] TASK-… …

## Notes Per Task

Add `### TASK-NNN` subsections only when notes exceed the inline `Session note` field.

## Completion Notes

- What was delivered:
- What was deferred:
- What needs follow-up:

## Resume Notes

- Current phase:
- Next recommended task:
- Active blocker:
- Last validation evidence added:
- Exact next command or proof to run:
