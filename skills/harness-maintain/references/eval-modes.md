# Harness Eval Modes

`harness-maintain` Eval Mode uses four evaluator passes. They can be run together or selectively.

## 1. Mechanical Gate Audit

- Confirm the feature or repo gate is explicit, reproducible, and fresh
- Check install, lint, typecheck, test, and build commands
- Record missing or stale proof surfaces

## 2. Alignment Audit

- Compare artifact claims against actual code and task state
- Detect spec drift, ghost behavior, weak traceability, and unverifiable completion claims

## 3. Adversarial And Security Review

- Check whether the harness exposes unsafe tool paths, weak approval rules, or prompt-injection risk
- Review sandbox assumptions, network/file permissions, and dangerous-command handling

## 4. Continuity And Context Audit

- Check whether session start/end, compaction, handoff, and resume behaviors are durable
- Detect stale context, weak checkpointing, or context pollution from raw logs

## Output

Write `artifacts/features/<slug>/eval-report.md` with:

- scope
- modes run
- findings by severity
- direct evidence
- recommended route (`harness-verify`, `context-session`, `context-memory`, or `harness-maintain Improve Mode`)
