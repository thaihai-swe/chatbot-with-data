# Spec Quality Scoring

<!-- Used by /harness-maintain Eval Mode to automatically score spec quality. This rubric evaluates whether a spec is well-formed, complete, and ready for implementation. -->

## Purpose

Provide a mechanical scoring rubric that can be applied to any `spec.md` to assess its quality without subjective judgment. Each criterion is binary (present/absent) or scored on a clear scale.

## Scoring Categories

### Structure (Max 10 points)

| Criterion | Points | Check |
|-----------|--------|-------|
| Problem statement present and specific | 2 | Not vague or generic |
| Target users identified with goals | 2 | At least 1 persona with a goal |
| Scenarios cover happy path + error cases | 2 | Minimum 2 scenarios |
| Requirements use REQ-* identifiers | 2 | Consistent numbering |
| Scope section with In/Out/Non-Goals | 2 | All three subsections present |

### Quality (Max 10 points)

| Criterion | Points | Check |
|-----------|--------|-------|
| Each requirement is testable (has AC) | 2 | No requirement without AC |
| Each AC names a proof surface | 2 | Unit test, integration test, manual, etc. |
| Gray-area decisions are captured | 2 | Or explicitly stated as "none" |
| No implementation details in spec | 2 | "What" not "how" |
| Verification surface section exists | 2 | Names the proof strategy |

### Completeness (Max 10 points)

| Criterion | Points | Check |
|-----------|--------|-------|
| No placeholder text remaining | 2 | No "TBD", "TODO", empty sections |
| Brownfield behavior documented (if applicable) | 2 | Or "greenfield" stated |
| Non-goals prevent scope creep | 2 | At least 1 explicit non-goal |
| Requirements cover all scenarios | 2 | No scenario without a requirement |
| Acceptance criteria are measurable | 2 | No subjective criteria ("looks good") |

## Scoring

| Total | Grade | Interpretation |
|-------|-------|----------------|
| 27-30 | A | Production-ready spec |
| 22-26 | B | Good spec, minor gaps acceptable |
| 16-21 | C | Needs iteration before planning |
| 10-15 | D | Significant rework required |
| 0-9 | F | Not a spec — restart from grilling |

## Red Flags (Auto-Fail)

Any of these present = spec is not ready regardless of score:

- Requirements contradict each other
- No acceptance criteria at all
- Spec prescribes implementation ("use React", "add a column") without a "why"
- Missing problem statement
- No scenarios

## Application

Run this scoring:
1. After `/spec-requirements` completes the requirements review
2. During `/harness-maintain` Eval Mode (Alignment Audit)
3. When reviewing specs from other teams or sessions
