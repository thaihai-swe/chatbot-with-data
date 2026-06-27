# Session Start Flow

Every session for an existing feature slug must follow this exact sequence to ensure context continuity.

If the feature slug does not exist yet or `artifacts/features/<slug>/status.md` is missing, stop immediately:

- route to `/spec-requirements` when the behavior can be specified directly
- route to `/spec-research` when the codebase is brownfield or the current behavior is still unknown

1.  **Load Memory Router:** Read `MASTER_INDEX.md` first. It declares which files are always loaded, which load by intent, and which load only on debug. If `MASTER_INDEX.md` is missing, load every memory file and route the gap to `context-memory` for index repair.
2.  **Load Always Group:** Read every file in the `MASTER_INDEX.md` **Always** section. By default this is `core-policies.md` — it holds normative rules, security policy, and memory promotion thresholds needed every session.
3.  **Resolve Intent And Load By-Intent Groups:** Match the active task (user request + feature `spec.md` + active `tasks.md` row when present) against the trigger keywords and semantic concepts listed in `MASTER_INDEX.md`. Evaluate if the conceptual intent of the task aligns with any of the intent groups (e.g. system architecture structure, heuristics, debugging context). Load only the groups whose triggers hit or whose semantic relevance matches. Record loaded groups and intentionally skipped groups in the readiness summary — silent skipping is not allowed.
4.  **Load Debug Group When Applicable:** If the task is debugging, retro, regression analysis, or post-mortem, also load the **By Debug** group (`memories/repo/harness-telemetry.md` and any prior `session-extracts.md` for the active feature).

5.  **Check Handoff:** Look for `.corezero/sessions/<slug>/handoff.md`. If it exists, read it to understand the exact state left by the previous session.
6.  **Check Progress:** Read `.corezero/sessions/<slug>/progress.md` to understand the broader history of the feature work.
7.  **Validate State:** Ensure the repository is in the state described by the handoff (e.g., if handoff says tests pass, verify they do).
7.5 **Integrity Cross-Check**: Perform these mechanical checks:
    * Verify every task ID in `tasks.md` traces to an AC ID in `spec.md`. Flag orphaned task IDs as `[STALE TASK]`.
    * Grep 3–5 key file paths mentioned in `plan.md` against `git ls-files`. Flag missing paths as `[STALE PLAN]`.
    * If stale markers are found, surface them as a `## ⚠️ Stale Context` section in the session readiness summary before proceeding. Do not silently continue.
8.  **Report Context:** Output a summary to the user indicating readiness:
    *   **Feature:** [slug]
    *   **Phase:** [current phase]
    *   **Next Task:** [task ID]
    *   **Blockers:** [None, or list them]
    *   **Context Loaded:** [Always group + by-intent groups loaded with the keywords that matched]
    *   **Context Skipped:** [by-intent groups intentionally skipped, with one-line reason each]
    *   **Stale Context:** [None, or describe stale tasks/plans found in Step 7.5]
