# Readiness Scoring

<!-- Used by /spec-requirements during the requirements review step. Scores the spec across 6 dimensions to produce a quantified readiness assessment, not just pass/fail. -->

## Scoring Dimensions

Each dimension is scored 1-5:

| Score | Meaning |
|-------|---------|
| 1 | Critical gaps — cannot proceed |
| 2 | Significant gaps — needs rework |
| 3 | Adequate — minor gaps acceptable for Simple work |
| 4 | Good — ready for Moderate work |
| 5 | Excellent — ready for Complex or high-risk work |

## Dimensions

### 1. Clarity (Requirements are specific and unambiguous)

| Score | Criteria |
|-------|----------|
| 1 | Requirements use vague language ("should be fast", "user-friendly"), no concrete definitions |
| 2 | Some requirements are specific but key terms are undefined or ambiguous |
| 3 | Most requirements are specific; remaining ambiguity is low-risk |
| 4 | All requirements are specific with defined terms; edge cases acknowledged |
| 5 | Requirements are precise, measurable, and leave no room for interpretation |

**Check:** Can two different implementers read this spec and build the same thing?

### 2. Completeness (All required sections are filled)

| Score | Criteria |
|-------|----------|
| 1 | Missing problem statement, users, or acceptance criteria |
| 2 | Core sections exist but scenarios or verification surface is missing |
| 3 | All sections present; some acceptance criteria lack proof surfaces |
| 4 | All sections complete; verification surface covers all requirements |
| 5 | Complete with gray-area decisions, non-goals, and brownfield observations |

**Check:** Could an implementer start work without asking clarifying questions?

### 3. Testability (Acceptance criteria are measurable)

| Score | Criteria |
|-------|----------|
| 1 | No acceptance criteria, or criteria are subjective ("looks good") |
| 2 | Some criteria are testable but most lack a named proof surface |
| 3 | Most criteria name a proof surface (unit test, integration test, manual check) |
| 4 | All criteria have named proof surfaces; mechanical verification is possible |
| 5 | All criteria have proof surfaces with specific commands or test names; Complex specs add a Gherkin `Given / When / Then` block per AC with a named `Test path:` |

**Check:** Can the verification gate be run mechanically without human judgment? For Complex, can a tester read the AC's scenario and the named test path together to reproduce the proof?

### 4. Feasibility (Technical approach is realistic)

| Score | Criteria |
|-------|----------|
| 1 | Requirements contradict technical constraints or are impossible |
| 2 | Feasibility is uncertain; key technical questions are unresolved |
| 3 | Feasible with known technology; some risk areas identified |
| 4 | Clearly feasible; risks are documented with mitigation strategies |
| 5 | Feasible, low-risk, and aligned with existing architecture patterns |

**Check:** Does the spec respect `docs/project/project-constraints.md` and `docs/project/architecture.md`?

### 5. Safety (Risks and controls are documented)

| Score | Criteria |
|-------|----------|
| 1 | No risk consideration; touches auth/data/payments without safeguards |
| 2 | Risks acknowledged but no controls or mitigation documented |
| 3 | Key risks identified with basic controls |
| 4 | Comprehensive risk assessment with controls and rollback strategy |
| 5 | Full risk matrix with controls, monitoring, and incident response |

**Check:** If this feature fails in production, is the blast radius understood?

### 6. Traceability (Requirements map to tasks and tests)

| Score | Criteria |
|-------|----------|
| 1 | No requirement IDs; no mapping to acceptance criteria |
| 2 | Requirements exist but AC coverage is incomplete |
| 3 | REQ → AC mapping is complete; task mapping not yet done (acceptable pre-planning) |
| 4 | REQ → AC mapping complete; verification surface names proof for each |
| 5 | Full REQ → AC → proof chain with no orphaned requirements |

**Check:** Can you trace every requirement to its proof?

## Readiness Verdict

| Total Score | Verdict | Action |
|-------------|---------|--------|
| 25-30 | Ready | Proceed to planning |
| 19-24 | Ready with caveats | Proceed for Moderate/Simple; iterate for Complex |
| 13-18 | Not ready | Iterate on weak dimensions before planning |
| 6-12 | Critical gaps | Major rework required |

## Output Format

```markdown
## Readiness Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity | X/5 | |
| Completeness | X/5 | |
| Testability | X/5 | |
| Feasibility | X/5 | |
| Safety | X/5 | |
| Traceability | X/5 | |
| **Total** | **XX/30** | |

**Verdict:** [Ready | Ready with caveats | Not ready | Critical gaps]
**Blocking issues:** [List any dimension scored 1-2]
```
