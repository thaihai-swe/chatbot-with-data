# 15 Harness Gotchas & Failure Modes

1.  **Giant AGENTS.md:** Overwhelms the context window. *Fix: Use a short router that points to specific files.*
2.  **No Init Phase:** Agent starts from wrong assumptions about the stack. *Fix: Require `starter-init` to baseline the repo.*
3.  **No Feature List:** Agent declares victory after writing code, before verifying all requirements. *Fix: Use explicit JSON/Markdown feature lists.*
4.  **No Progress Log:** Continuity is lost when sessions restart. *Fix: Maintain a durable `progress.md`.*
5.  **No Gate Policy:** Tasks are marked done without mechanical proof. *Fix: Enforce `harness-verify` mechanical gate checks before closing tasks.*
6.  **No Clean-State Check:** Next session inherits a broken build. *Fix: Require passing tests before session end.*
7.  **No Context Condensation:** Context window exhausted mid-task. *Fix: Summarize and prune actively.*
8.  **No Scope Constraint:** Agent drifts and refactors unrelated code. *Fix: Strict adherence to exact Task IDs.*
9.  **No Decision Durability:** Same architectural debates happen every session. *Fix: Record decisions in `spec.md` or `core-policies.md`.*
10. **No Mechanical Enforcement:** Rules in prompts are forgotten. *Fix: Translate rules into lint checks or gate policies.*
11. **Monolithic Test Suite:** Slow feedback loops cause the agent to skip testing. *Fix: Run targeted unit tests during implementation.*
12. **No Error Taxonomy:** Model hallucination is blamed when the harness simply lacked documentation. *Fix: Use `harness-maintain` Improve Mode to classify errors correctly.*
13. **No Subagent Delegation:** Main context gets cluttered with thousands of lines of grep output. *Fix: Isolate research.*
14. **No Handoff Template:** Next session starts completely blind. *Fix: Always generate `handoff.md`.*
15. **No Architecture Rules:** Structural patterns erode into spaghetti code over time. *Fix: Document boundaries in `project-knowledge-base.md`.*
