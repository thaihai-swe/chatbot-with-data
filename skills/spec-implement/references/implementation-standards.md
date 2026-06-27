# Implementation Standards

Non-UI implementation rules for `spec-implement`. These apply to all backend, API,
data model, CLI, and infrastructure work. For UI/UX work, use `design-standards.md`
instead.

## Module Boundary Discipline

- A module owns one coherent responsibility. If a file does two unrelated things,
  it is two modules incorrectly collapsed.
- Do not reach across module boundaries to access private state. Prefer explicit
  interfaces (function arguments, return values, published types).
- If you find yourself adding a function to a module "just for this task," ask whether
  the function's caller belongs there or whether it should call a public method on the
  owning module instead.
- When a module grows beyond ~400 lines, investigate whether a responsibility split is
  warranted — not mandatory, but a signal worth checking.

## Error Handling Patterns

- Every error must be either handled or explicitly propagated. Silent swallowing is
  not acceptable: `catch (e) {}` with no rethrow or log is a red flag.
- Prefer returning typed errors over throwing exceptions for expected failure paths
  (validation failures, not-found, permission denied).
- Only throw/raise exceptions for truly unexpected states. If a caller can predict
  the failure mode, the function should return a typed result.
- Do not convert a specific error into a generic one (e.g., `throw new Error("failed")`
  instead of propagating the original).
- Log at the point closest to the source. Don't re-log the same error at every
  caller level unless adding new context.

## Naming for Non-UI Code

- Functions: verb phrase that describes what the function does, not what it returns.
  `getUserById` ✓, `user` ✗, `doUserThing` ✗.
- Variables: nouns that describe the data they hold. Avoid single-letter names outside
  tight loops. Avoid `temp`, `result`, `data` without qualification.
- Boolean variables/functions: prefix with `is`, `has`, `can`, `should`.
- Constants: SCREAMING_SNAKE_CASE for true constants; camelCase for module-level
  configuration values.
- Avoid abbreviations unless they are universally understood in the domain (e.g.,
  `id`, `url`, `api`). `usr` for `user` is not acceptable.

## The One-Task = One-Reviewable-Diff Contract

- Each task in `tasks.md` should produce one diff that a reviewer can understand in
  isolation. If a diff touches more than 3 unrelated files, the task was too broad.
- Proof-before-code & Pre-Flight Execution: record the exact verification command or test target before making any edits, and execute it at least once to establish a baseline in the execution log. If you cannot name and run the proof first, the task boundary is still unclear.
- A task is done when: the baseline is run, the code change is committed, the proof passes, and the result is recorded in `tasks.md`. Not before.

## Preserved Behavior

- When modifying brownfield code, name the behavior you are preserving at the top
  of the task. If the test suite covers that behavior, run it before and after.
- Do not refactor adjacent code while implementing a task. If refactoring is needed,
  add a separate task to `tasks.md` and get it approved before touching unrelated code.

## Referencing

- `design-standards.md` — UI/UX implementation rules (parallel to this file)
- `../_shared/status-phases.md` — lifecycle state machine
