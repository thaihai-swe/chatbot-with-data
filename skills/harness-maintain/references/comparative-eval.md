# Comparative Evaluation

<!-- Used by /harness-maintain Eval Mode to measure whether the harness actually improves output quality. Provides A/B methodology for with-harness vs without-harness comparison. -->

## Purpose

Quantify the value of the harness by comparing agent output quality with and without harness constraints. This answers the question: "Is the harness actually helping, or just adding ceremony?"

## Methodology

### Setup

1. **Select a task** — Choose a representative feature or bug fix that has already been completed with the harness.
2. **Define the baseline** — The same task attempted without harness constraints (no spec, no plan, no gates).
3. **Define the treatment** — The same task with full harness workflow.
4. **Control variables** — Same agent, same model, same repository state, same prompt.

### Execution

| Condition | What the Agent Gets | What It Produces |
|-----------|--------------------|--------------------|
| **Without harness** | Raw task description only | Code changes, chat explanation |
| **With harness** | Full workflow (spec → plan → implement → verify) | Artifacts + code + verification evidence |

### Measurement Dimensions

| Dimension | Without Harness | With Harness | How to Measure |
|-----------|----------------|--------------|----------------|
| **Correctness** | Does the code work? | Does the code pass the mechanical gate? | Run tests, check behavior |
| **Completeness** | Are all requirements met? | REQ → AC → TASK → proof chain intact? | Trace requirements to implementation |
| **Drift** | Did the agent add unrequested features? | Is scope bounded to spec? | Compare output to original request |
| **Hallucination** | Did the agent fabricate claims? | Are all claims backed by evidence? | Audit verification evidence |
| **Resumability** | Can another agent continue this work? | Is the handoff artifact complete? | Attempt cold-start resume |
| **Security** | Were security concerns addressed? | Did the security lens catch issues? | Review auth, input validation, secrets |
| **Consistency** | Is output quality predictable? | Is variance reduced across runs? | Repeat 3x, measure variance |

## Scoring Rubric

Each dimension is scored 1-5:

| Score | Meaning |
|-------|---------|
| 1 | Critical failure — wrong, incomplete, or dangerous |
| 2 | Significant gaps — partially works but unreliable |
| 3 | Adequate — works but with notable issues |
| 4 | Good — works well with minor gaps |
| 5 | Excellent — correct, complete, and verifiable |

## Running a Comparative Eval

### Step 1: Select Tasks

Choose 3-5 tasks that represent your typical workload:
- 1 tiny change (config update, typo fix)
- 1 standard feature (new endpoint, UI component)
- 1 complex change (cross-boundary, brownfield)
- 1 bug fix (reproduction + fix)
- 1 refactor (behavior-preserving change)

### Step 2: Run Without Harness

For each task, give the agent only:
- The task description (1-3 sentences)
- Access to the repository
- No skills, no templates, no memory files, no workflow

Record: what it produced, how long it took, what it got wrong.

### Step 3: Run With Harness

For each task, use the full workflow:
- `/spec-requirements` → `/spec-plan` → `/spec-implement` → `/harness-verify`
- Full memory context loaded
- All gates enforced

Record: artifacts produced, verification results, time spent.

### Step 4: Score and Compare

```markdown
## Comparative Results

| Task | Dimension | Without (1-5) | With (1-5) | Delta |
|------|-----------|---------------|------------|-------|
| [task] | Correctness | | | |
| [task] | Completeness | | | |
| [task] | Drift | | | |
| [task] | Hallucination | | | |
| [task] | Resumability | | | |
| [task] | Security | | | |
| [task] | Consistency | | | |

### Summary

- Average without harness: X/5
- Average with harness: X/5
- Improvement: +X% 
- Variance without: ±X
- Variance with: ±X
- Tasks where harness hurt (added ceremony without value): X/N
```

### Step 5: Interpret

| Result | Interpretation | Action |
|--------|---------------|--------|
| With > Without by 20%+ | Harness is adding clear value | Continue, consider expanding |
| With > Without by 5-20% | Marginal improvement | Check if ceremony is proportional |
| With ≈ Without | Harness isn't helping | Simplify — reduce ceremony for this task type |
| With < Without | Harness is hurting | The workflow is over-constraining; adjust delivery profile |

## When to Run

- After initial adoption (validate the kit is helping)
- Quarterly (check for ceremony creep)
- After major harness changes (verify improvements)
- When team complains about overhead (data over opinions)

## Limitations

- Author-measured evals are biased — seek third-party replication
- Small sample sizes (< 10 tasks) have high variance
- Task selection affects results — use representative mix
- Time-to-complete is a valid dimension but hard to control for
