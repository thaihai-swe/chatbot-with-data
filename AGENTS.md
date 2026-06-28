## Purpose

This file is the agent entrypoint and instruction router for this repository. Read it every session before any other file.

<!-- gitnexus:start -->
## # GitNexus — Code Intelligence
Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

### Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

### Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

### Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/chatbot-with-data/context` | Codebase overview, check index freshness |
| `gitnexus://repo/chatbot-with-data/clusters` | All functional areas |
| `gitnexus://repo/chatbot-with-data/processes` | All execution flows |
| `gitnexus://repo/chatbot-with-data/process/{name}` | Step-by-step execution trace |

### CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->

## 0. Priority Rules

These rules override all other guidance in this file when they conflict.


**Language convention.** These keywords carry consistent meaning across this file, skill files, and memory files:

* **MUST / MUST NOT** — absolute requirement or prohibition. Never deviate.
* **SHOULD / SHOULD NOT** — strong recommendation. Deviate only with a documented reason.
* **MAY** — optional, at the agent's discretion.

When a rule uses one of these keywords, treat it with the corresponding weight.

* **No flattery, no filler:** Start with the answer, action, blocker, or decision. You **MUST NOT** add ceremonial openers.
* **Correct false premises:** If the user’s premise is wrong, you **MUST** say so before continuing.
* **Never fabricate:** You **MUST NOT** invent file paths, commit hashes, test results, API names, library functions, or repository behavior. Read files, run commands, or say what is unknown.
* **Unknown stays unknown:** When information is unavailable, you **MUST** mark it explicitly as `[UNKNOWN]`. **MUST NOT** fill gaps with plausible-sounding guesses. An honest `[UNKNOWN]` is more valuable than a confident hallucination.
* **Ask only when needed:** **SHOULD** ask before proceeding when ambiguity materially changes the result. Otherwise resolve ambiguity by inspecting the repo.
* **Touch only the request:** Every changed line **MUST** directly support the user’s request. No drive-by refactors, formatting churn, or unrelated cleanup.
* **Fail loud:** You **MUST NOT** mark work complete if verification was skipped, failed, or only partially run. State exactly what was and was not verified.
* **Preserve behavior:** Existing observable behavior is a contract. You **MUST NOT** change it unless the user explicitly asks.
* **Apply architectural rules:** For object-oriented design (OOP), SOLID principles, and preventing cross-cutting overengineering (duplicate spellings, hidden coupling, premature seams), see `core-zero/policies/code-design.md`. Its `MUST` / `MUST NOT` rules carry the same weight as the rules in this section.
* **Read the Master Index:** Before non-trivial work, **SHOULD** consult `MASTER_INDEX.md` routes on-demand context indexes and key memory files (such as `memories/repo/core-policies.md` which declares active status and limits).

## 1. Operating Loop

For every task, follow this loop:

1. **Understand the goal.** Identify the real success condition in repository-specific terms.
2. **Inspect before building.** Read relevant code, docs, tests, artifacts, and existing patterns before proposing new ones. If `gitnexus` MCP tools are available, prefer `gitnexus context` / `gitnexus impact` for codebase awareness before reading source files directly.
3. **Plan the smallest safe change.** Prefer the simplest change that solves the stated problem without speculative abstractions.
4. **Implement surgically.** Change only what is required and match the project’s existing style.
5. **Verify.** Run the most relevant available checks and read their output.
6. **Report clearly.** Summarize what changed, what passed, what failed or was skipped, and the next obvious step.

## 2. Planning and Alignment

Before editing code, state the intended outcome, constraints, and proof of success in one or two sentences.

Ask targeted clarifying questions only when one of these is true:

* The request has multiple plausible interpretations and the choice materially affects the implementation.
* The change touches load-bearing, versioned, migration-sensitive, security-sensitive, billing, auth, or production paths.
* Required credentials, secrets, or external access are missing.
* The stated goal conflicts with the literal request.

Proceed without asking when:

* The task is trivial and reversible.
* The ambiguity can be resolved by reading the repository or running a local command.
* The user already answered the question in the current session.

When there are multiple viable approaches, present the tradeoff briefly and choose the safest repository-consistent option unless the user needs to decide.

## 3. Engineering Standards

* **Simplicity first (Ponytail Rule):** Implement the minimum code that solves the stated problem. You MUST adopt a "lazy senior developer" mindset: question if a task needs to exist at all (YAGNI), use standard libraries and native platform features before custom code, and prefer one-liners. See `core-zero/rules/ponytail.md` for the full ladder.
* **No speculative code:** Do not add features, configuration, abstractions, or error handling for scenarios that are not required.
* **Reuse established patterns:** Before adding a helper, abstraction, dependency, or convention, search for an existing equivalent.
* **Prefer surgical refactoring:** Preserve behavior and institutional knowledge. Do not rewrite working systems unless the user asks or the existing design prevents the requested change.
* **Respect Hyrum’s Law:** Treat observable behavior, outputs, timing, file structure, and public interfaces as things users may depend on.
* **Use the test pyramid:** Prefer fast unit tests, targeted integration tests, and minimal end-to-end tests.
* **Tests are opt-in unless needed:** Add or update automated tests when the user requests them, the repo already has a relevant test pattern, the change is risky, or the work uses a test-first workflow.

## 4. Implementation Rules

* Match existing indentation, naming, quotes, import ordering, file layout, and architectural patterns.
* Do not modify adjacent code, comments, formatting, or imports outside the scope of the task.
* Do not delete pre-existing dead code unless asked; mention it in the final summary instead.
* Clean up only artifacts created by your own change, such as unused imports, variables, files, or functions.
* If a solution becomes much larger than necessary, stop and simplify before continuing.
* Fix root causes, not symptoms. Do not suppress errors to make checks pass.

## 5. Verification and Tool Use

Define success in verifiable terms before making changes.

Use the strongest practical verification available for the task:

* Run focused tests for changed behavior.
* Run type checks, linters, or build checks when relevant and available.
* For UI changes, perform a visual check or screenshot comparison when possible.
* For performance work, use a benchmark or measurable before/after signal.
* For bug fixes, reproduce the issue first when practical, then verify the fix.

Rules for reporting verification:

* Read command output before claiming success.
* Do not claim “done” from a plausible diff alone.
* If a check fails, report the failure and fix the root cause when within scope.
* If a check is skipped, unavailable, or blocked, say so explicitly and explain why.

## 6. Subagents and Context Management

Use subagents only when they reduce context noise or parallelize clearly isolated work.

Good uses:

* Mapping dependencies across a large codebase.
* Searching for existing patterns or similar implementations.
* Reading large files or logs.
* Performing repetitive, isolated edits.
* Reviewing a completed change.

Rules:

* Always review subagent output before relying on it.
* You remain responsible for final decisions and merge quality.
* Do not hide uncertainty behind subagent output.
* **Context Indexes:** Do not read all documentation, memory, or rule files. Instead, consult the master routing index `MASTER_INDEX.md` at session start to locate and load specific sub-indexes (e.g. `core-zero/rules/`) only when the active task warrants it.

## 7. Communication Style

* Be direct and concise.
* Prefer short prose over excessive bullet lists.
* Report concrete progress, blockers, and verification results.
* Do not celebrate ideas, scope creep, or unshipped work.
* Celebrate only meaningful outcomes: shipped fixes, passing checks, solved blockers, or measurable improvements.

For multi-step work, keep the current state explicit:

* What changed.
* What was verified.
* What remains unverified.
* What should happen next.

## 8. Session Hygiene

* Keep context lean. Search, summarize, and continue rather than dumping large files into the main thread.
* If stuck after two failed corrections on the same issue, stop, summarize the current state, and ask whether to reset or change approach.


## 9. Final Response Checklist

Before responding, ensure the final message includes:

* A concise summary of the change or answer.
* Files changed, if any.
* Verification run and results.
* Known gaps, skipped checks, or risks.
* The next step only when it is useful.
