# Regression Testing

<!-- Used by /harness-maintain Eval Mode to detect spec/output drift over time. Provides patterns for catching regressions in both agent behavior and delivered features. -->

## Purpose

Detect when previously-verified behavior degrades — either because code changed, specs drifted, or the harness itself weakened. Regression testing operates at three levels: feature, harness, and agent behavior.

## Level 1: Feature Regression

### What to Check

After any code change, verify that previously-passing features still pass.

| Check | Method | Frequency |
|-------|--------|-----------|
| Mechanical gate still passes | Run all gate commands | Every implementation task |
| Existing tests still pass | Full test suite | Before verify phase |
| No new lint/type errors | Lint + typecheck | Every implementation task |
| No behavioral drift | Compare output against spec AC | During verify alignment audit |

### Detection Signals

- Test that previously passed now fails
- Lint errors in files not touched by the current feature
- Performance degradation beyond budget (if monitored)
- API contract violation (response shape changed)

### Response

1. Stop current work
2. Identify which change caused the regression
3. Fix the regression before continuing
4. Record in `harness-telemetry.md` if the harness should have caught it earlier

## Level 2: Harness Regression

### What to Check

The harness itself can degrade — skills get stale, templates drift, cross-references break.

| Check | Method | Frequency |
|-------|--------|-----------|

| Templates match skill expectations | Manual review | Monthly |
| Memory files are current | Review dates and evidence | Per session start |
| Cross-references resolve | Grep for broken links | After skill changes |

### Detection Signals

- Consistency check fails
- Skill references a template that doesn't exist
- Memory file contains stale information (outdated commands, removed files)
- Agent repeatedly hits the same failure pattern (harness isn't learning)

### Response

1. Run `/harness-maintain` Assess Mode
2. Classify as Harness/Model/Spec problem
3. Apply fix via Improve Mode
4. Record in `harness-telemetry.md`

## Level 3: Agent Behavior Regression

### What to Check

Agent quality can degrade across sessions — context loss, pattern drift, or model changes.

| Check | Method | Frequency |
|-------|--------|-----------|
| Agent follows skill contracts | Review against SKILL.md | Per feature |
| Agent uses correct commands | Check core-policies.md compliance | Per session |
| Agent produces complete artifacts | Check against templates | Per phase |
| Agent doesn't skip verification | Audit task evidence | Per verify phase |

### Detection Signals

- Agent skips grilling waves
- Agent marks tasks "done" without evidence
- Agent ignores stop conditions
- Agent produces artifacts missing required sections
- Agent uses deprecated commands

### Response

1. Record the behavior in `harness-telemetry.md`
2. Classify: Is this a harness problem (environment allowed it) or model problem (agent ignored constraints)?
3. If harness: strengthen the gate or add a mechanical check
4. If model: add explicit guidance to the relevant skill's Core Rules

## Regression Test Checklist

Run before declaring any feature complete:

```markdown
## Regression Check

- [ ] Full test suite passes (not just new tests)
- [ ] Lint/typecheck clean across entire repo
- [ ] No unintended file changes (git diff is surgical)
- [ ] Previously-verified features still work (smoke test)
- [ ] Consistency check passes
- [ ] No stale evidence in current feature artifacts
```

## Continuous Regression Prevention

The harness prevents regression through:
- **Clean-state guarantee:** `/starter-init` ensures baseline is green before work starts
- **Mechanical gates:** Exact commands that must pass — catches regressions mechanically
- **Fallow pass:** `/harness-verify` cleans up debt without changing behavior
- **Session continuity:** Handoffs preserve verification state across sessions
- **Observability log:** Patterns of failure drive harness improvements
