---
name: memory-promotion
description: Decide whether a finding should be promoted into durable repository memory, escalated into the constitution, or left in feature artifacts. Use when reviewing analysis output or other feature artifacts and deciding what deserves durable reuse.
compatibility: Designed for Claude, Codex, and other Agent Skills-compatible tools working in spec-driven repositories that use memories/repo/ and artifacts/features/<slug>/.
metadata:
  author: spec-driven-development-kit
---

# Memory Promotion

## Overview

Use this skill to decide where a repository finding belongs after analysis, implementation, review, or cleanup work.

This skill classifies findings. It does not replace the owning update skills for `constitution.md` or `project-knowledge-base.md`.

## When to Use

Use this skill when the user needs to:

- decide whether a finding should become durable repo memory
- choose between `memories/repo/project-knowledge-base.md`, `memories/repo/constitution.md`, or feature artifacts
- review whether a lesson learned is stable enough to keep

Do not use this skill for:

- writing the promoted content directly without a placement decision
- forcing promotion when the evidence is weak
- feature-local notes that are obviously temporary

## Read First

Read these inputs when they exist:

- `memories/repo/constitution.md`
- `memories/repo/project-knowledge-base.md`
- the feature artifact or review output that produced the finding
- any repository evidence needed to confirm the finding is real and durable
- `references/decision-template.md`

## Workflow

1. Identify the candidate finding and its source artifact.
2. Check whether the finding is evidence-based, durable, and useful beyond the current feature.
3. Decide whether it is descriptive knowledge, a repo-wide rule, or still feature-local.
4. Recommend exactly one destination: `project-knowledge-base.md`, `constitution.md`, or the existing feature artifact.
5. State the short reason for the decision and route to the owning update skill when promotion is warranted.

## Stop Conditions

Stop and keep the finding in feature artifacts when:

- the finding is still uncertain or speculative
- the evidence does not show that the pattern is durable
- the finding matters only to the current feature or incident

When stopping, say:

- what the finding is
- why it is not ready for durable memory
- what evidence or reuse signal would justify promotion later

## Core Rules

- Promote only findings that future work is likely to need again.
- Use `project-knowledge-base.md` for durable descriptive patterns, boundaries, and watchouts.
- Use `constitution.md` only for true repository-wide rules or guardrails.
- Keep feature-local discoveries in feature artifacts until they clear the promotion bar.
- When the destination is unclear, err toward leaving the finding local instead of over-promoting it.
- Route to `project-knowledge-base` or `constitution` after the decision instead of silently editing both in the same step.

## References

- Use [references/decision-template.md](references/decision-template.md) when a structured decision record would help.
- Use [references/example-decision.md](references/example-decision.md) to calibrate what a concise, evidence-based promotion decision should look like.
- Keep the output short and decisive.
- Prefer one clearly justified destination over a hedge list of possibilities.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "This was useful once, so it belongs in repo memory." | Durable memory is for reusable knowledge, not every interesting note. |
| "If it sounds important, put it in the constitution." | The constitution is for rules, not for descriptive context. |
| "We can always clean it up later." | Over-promotion creates noise that future agents will trust too much. |

## Red Flags

- a temporary workaround is being promoted as durable knowledge
- a descriptive note is being framed as a rule
- the same finding could not be explained without reference to one specific feature

## Verification

Before finalizing the decision, verify:

- the finding is grounded in repository evidence
- the recommended destination matches the type of knowledge
- the reason explains why the finding is durable, normative, or still local
- no promotion is recommended just to avoid losing chat context

## Output Standard

The decision is ready only when it:

- names exactly one destination
- cites the evidence that makes the finding durable, normative, or still local
- gives a short reason future maintainers can trust without chat history

## Output Rules

- Return exactly one recommendation: promote to `project-knowledge-base.md`, promote to `constitution.md`, or keep in feature artifacts.
- Include a short reason with the recommendation.
- Use the template shape when a maintainer asks for a reusable decision record.
- Do not update repo memory files directly unless the user separately asked for that change.
