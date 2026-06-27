# Session Lifecycle Bootstrap

Long-running agentic workflows require structured sessions to maintain continuity and prevent state corruption.

## 1. Initialization Phase (`starter-init`)
*   Must occur before any feature work.
*   Validates the baseline: Do tests pass? Is the build clean?
*   Establishes the routing infrastructure (`AGENTS.md`).

## 2. Session-Start Flow (`context-session`)
*   Load rules (`core-policies.md`).
*   Check for previous handoffs or progress logs to resume work accurately.
*   Re-validate the clean state.

## 3. Checkpointing
*   Periodically record progress to `progress.md`.
*   Acts as a save-state if the session crashes or the context window maxes out.

## 4. Session-End Flow
*   Verify clean state (no broken tests left behind).
*   Finalize the progress log.
*   Generate `handoff.md` for the next session.

## 5. Background Tasks and Hooks
*   Utilize pre-commit hooks or continuous CI to provide immediate, out-of-band feedback if the agent strays from the harness constraints.

## 6. Security And Evaluators
*   Repositories should define a durable `core-policies.md` `## Security Policy` before sensitive work begins.
*   Long-running flows should use explicit evaluator passes, not only a single generic closeout review.
