# Prototype Technique

A research technique for resolving logic, algorithm, or data-flow questions that cannot be answered by reading the code. Write a throwaway script in isolation, prove the behavior, then bring the answer back into `analysis.md`.

## When to Use

- The question is about *logic shape*, not code shape — "does this approach actually work?", "what does this algorithm produce on edge inputs?", "what does this state machine look like under load?"
- Reading the code keeps surfacing the same uncertainty.
- You need to compare 2-3 candidate approaches before committing in `spec.md` or `plan.md`.
- A bug hypothesis can be confirmed faster by reproducing the logic in isolation than by instrumenting the live system.

## When NOT to Use

- The answer lives in the codebase — use `grep` / Read / Explore agent instead.
- The question is product/UX — that's a grilling-phase question, not a prototype question.
- The work is straightforward enough that the prototype would be the implementation.

## Rules

- *Throwaway by design:* The prototype is a terminal app, a single file, or a notebook. No integration into the real codebase. No imports from production modules unless you are deliberately testing one in isolation.
- *One question per prototype:* A prototype that is testing more than one hypothesis is a feature. Split it.
- *Stage outside the repo (or in a clearly disposable folder):* Prefer `/tmp/<feature>-prototype.py` or a `.gitignore`d `prototypes/` folder. Never check the prototype into a feature branch as if it were the answer.
- *Capture the answer, not the code:* Write the conclusion into `analysis.md`. The prototype's value is the conclusion it produced; the script itself is disposable.
- *Cleanup is part of the technique:* Delete the prototype after the answer is captured. Leftover prototypes drift into "I might use this later" debt.

## Anti-Patterns

| Anti-Pattern | Why It's Bad |
|---|---|
| Prototype quietly becomes prod code | Prototypes are written without the constraints prod code needs (error handling, types, security, tests). Promoting one creates a hidden quality drop. |
| Prototype tries to test 5 things at once | Each variable confounds the others. The conclusion is unfalsifiable. |
| Running the prototype but not writing down what it proved | The next agent (or future you) repeats the work. |
| Keeping the prototype around "just in case" | It rots. By the time you need it again, the assumptions it embedded are stale. |

## Output

After running a prototype, the deliverable is a section in `analysis.md`:

```
## Prototype: <one-line question>

*Question:* <the single hypothesis being tested>
*Setup:* <what was simulated, what was held constant>
*Result:* <what happened, with concrete numbers/outputs>
*Decision unlocked:* <what this lets the next skill commit to>
*Disposed:* <yes/no — and where the prototype lived if it survives short-term>
```

The prototype script itself is *not* an artifact. The conclusion is.
