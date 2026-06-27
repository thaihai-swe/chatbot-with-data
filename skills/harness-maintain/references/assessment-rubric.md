# Harness Assessment Rubric

Score the repository from 1 (Minimal) to 5 (Production) across the seven core subsystems: Instructions, State, Verification, Scope, Lifecycle, Security, and Context Engineering.

## 1. Instructions
*   **1:** No instructions. Agent guesses.
*   **3:** A monolithic `AGENTS.md` or prompt file exists.
*   **5:** Progressive disclosure. A short router points to a structured constitution and knowledge base.

## 2. State
*   **1:** State is entirely in the chat window.
*   **3:** A basic `tasks.md` exists but isn't updated reliably.
*   **5:** Persistent progress logs, explicit feature lists, and durable decision records exist.

## 3. Verification
*   **1:** Manual review only.
*   **3:** Tests exist, but the agent must remember to run them.
*   **5:** Strict gate policies (lint, type, test) mechanically block task completion if they fail.

## 4. Scope
*   **1:** Agent is asked to "build the feature" in one shot.
*   **3:** Basic task breakdown exists.
*   **5:** Strict task ID discipline; small, independently provable task slices; zero drift tolerance.

## 5. Lifecycle
*   **1:** Ad-hoc prompting.
*   **3:** Some end-of-session handoff occurs.
*   **5:** Formal initialization, checkpointing, context condensation, and clean-state guarantees are enforced.

## 6. Security
*   **1:** No permission model. Agent guesses what is allowed.
*   **3:** Some safety rules exist, but trust boundaries and confirmations are inconsistent.
*   **5:** Security policy is explicit; permission tiers, sandbox expectations, and prompt-injection handling are enforced.

## 7. Context Engineering
*   **1:** All context loaded at once. No eviction. Agent drowns in noise after a few turns.
*   **3:** Some JIT loading but no eviction rules. Stale logs and superseded designs accumulate.
*   **5:** Tiered JIT loading with explicit eviction rules, compaction triggers, and stale-context discipline. Subagents used for broad exploration to keep main context lean.

## Overall Maturity
*   **7-14:** Minimal. High risk of failure on complex tasks.
*   **15-21:** Basic. Suitable for simple scripts.
*   **22-28:** Moderate. Can handle moderate feature work.
*   **29-35:** Production. Highly reliable for autonomous, long-running engineering.
