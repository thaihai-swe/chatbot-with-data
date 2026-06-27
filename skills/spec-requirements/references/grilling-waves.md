# Grilling Waves

<!-- Explicit structure for the Socratic grilling phase in /spec-requirements. Defines wave patterns, question categories, escalation triggers, and conflict resolution. -->

## Purpose

The grilling phase eliminates product ambiguity before spec authoring begins. It uses targeted questions proportional to the work's complexity to surface hidden assumptions, contradictions, and missing context.

## Wave Structure

### Wave 1: Problem & Scope (Always run)

Goal: Confirm the problem is real, bounded, and worth solving.

Question categories:
- **Who:** Who experiences this problem? How often? How painful is it?
- **What:** What does success look like? What's the smallest useful outcome?
- **Boundary:** What's explicitly NOT in scope? What's adjacent but separate?

Minimum: 2 questions. Maximum: 3.

### Wave 2: Behavior & Decisions (Moderate + Complex)

Goal: Surface user-facing choices and interaction decisions that affect implementation.

Question categories:
- **Behavior:** What happens when [edge case]? What's the expected behavior for [boundary condition]?
- **Decisions:** Has the team already decided [X]? Is there a preference between [A] and [B]?
- **Preservation:** What existing behavior must NOT change?

Minimum: 2 questions. Maximum: 4.

### Wave 3: Risk & Verification (Complex only)

Goal: Identify risks, constraints, and proof requirements before committing to a plan.

Question categories:
- **Risk:** What could go wrong? What's the blast radius if this fails?
- **Constraints:** Are there performance budgets, compliance requirements, or deadlines?
- **Proof:** How will we know this works? What does "verified" mean for this feature?
- **Scenario shape:** For each AC under discussion, what are the exact `Given / When / Then` steps and which test file or check exercises them?
- **Brownfield:** What existing systems does this touch? What's fragile?

Minimum: 2 questions. Maximum: 4.

## Complexity → Wave Mapping

| Complexity | Waves | Total Questions |
|------------|-------|-----------------|
| Simple | Wave 1 only | 2-3 |
| Moderate | Waves 1 + 2 | 4-7 |
| Complex | Waves 1 + 2 + 3 | 6-11 |

## Question Quality Rules

- **High-signal:** Each question must reduce ambiguity that would materially affect implementation
- **Concrete:** Ask about specific scenarios, not abstract preferences
- **Non-leading:** Don't embed assumptions in the question
- **Actionable:** The answer must change what you'd write in the spec
- **Proportional:** Don't ask Complex-level questions for Simple work
- **Batch by wave:** Send the wave's full 2-4 questions together as a numbered list, then wait for answers. Do not send one question, wait, then send the next — that triples the round trips and breaks the user's flow. The dependency-ordered walking happens *across waves*, not within a wave.
- **Pair every question with your recommended answer:** Format: *"My recommendation: X, because [reason]. Disagree?"* Committing to a best guess is faster than neutral interviewing and reveals where the user actually disagrees.
- **Don't ask what the codebase can answer:** If `grep`, file reads, or `git log` would resolve the question in seconds, investigate first. Reserve questions for user-owned decisions (intent, priority, UX, scope) — not facts that already exist in the repo.
- **Walk the decision tree in dependency order:** Resolve foundational forks before leaves *across waves*. Architecture before UX, integration boundary before payload shape, in-scope vs out-of-scope before AC wording.

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Instead |
|--------------|-------------|---------|
| "Do you want me to add tests?" | Obvious answer, wastes a question | Ask about WHAT to test, not WHETHER |
| "Should I follow best practices?" | Vague, non-actionable | Ask about specific tradeoffs |
| "Is there anything else?" | Open-ended, low-signal | Ask about a specific gap you noticed |
| Asking 10 questions for a Simple change | Disproportionate ceremony | Scale to complexity |
| Asking only 1 question for Complex work | Insufficient coverage | Minimum 6 for Complex |

## Escalation Triggers

Stop grilling and escalate when:

- **Contradictory answers:** User's answers to Wave 1 and Wave 2 conflict. Surface the contradiction explicitly.
- **Missing stakeholder:** Answers require input from someone not in the conversation.
- **Scope explosion:** Answers reveal the work is much larger than initially presented. Recommend decomposition.
- **Unresolvable ambiguity:** After 2 attempts to clarify, the ambiguity remains. Record it as an open question in the spec.

## Conflict Resolution

When user answers contradict each other:

1. **Name the conflict explicitly:** "Earlier you said X, but now you're saying Y. These conflict because..."
2. **Present the tradeoff:** "If we go with X, then [consequence]. If we go with Y, then [consequence]."
3. **Ask for a decision:** "Which direction should we lock in the spec?"
4. **Record the decision:** Capture in the Gray-Area Decisions section of spec.md with the rationale.

## Term Coining Triggers

Update `docs/project/glossary.md` inline (in the same turn the term is resolved, not batched at the end) when any of these fire:

| Trigger | Example | Action |
|---|---|---|
| **Clash** — user term conflicts with an existing glossary entry | User says "account" but glossary defines `Account` differently | Surface the conflict, propose canonical form, update the entry |
| **Vagueness** — overloaded word causes repeated re-clarification | `user`, `event`, `process`, `record` keep needing context | Propose a precise replacement (e.g. `Subscriber` vs `User`) and add it |
| **Compression** — multi-word concept used 3+ times in the session | "the path where a draft becomes a published document" | Coin a single canonical term ("publish cascade"), add it, then use it |
| **Forbidden term** — user reaches for a deprecated or banned term | Saying "client" in a repo that banned the word | Add to `## Forbidden Terms` table with the canonical replacement |

Discipline:

- **Definitions only.** No implementation detail, no rationale, no design choices in glossary entries. If it explains *why*, it belongs in `spec.md` or an ADR, not the glossary.
- **One-line `Used in` pointer max.** Naming where the term first appears is fine. Quoting paragraphs is not.
- **Use what you coin.** A term coined and never used in `spec.md` or `plan.md` is glossary debt — either drop it or commit to it.
- **Skip if no glossary exists.** If the adopting project has not initialized `docs/project/glossary.md` into a project glossary, do not silently create one — flag the gap and continue.

## Output

After grilling completes, the agent should have:
- Clear problem statement
- Bounded scope (in/out/non-goals)
- Key user-facing decisions resolved
- Risk awareness proportional to complexity
- Enough context to write the spec without further questions

If any of these are missing after the appropriate waves, run one more targeted question before proceeding.
