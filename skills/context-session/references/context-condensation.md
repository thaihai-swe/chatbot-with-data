# Context Condensation Strategies

As a session progresses, the context window fills up with conversation history, tool outputs, and loaded files. To prevent context degradation, apply these strategies:

1.  **Summarize, Don't Repeat:** Instead of carrying forward the full output of a failing test, summarize it: "Test X fails on line 42 due to a null pointer exception in user auth."
2.  **Prune Exploration:** If a subagent or tool was used to search the codebase, extract the findings and discard the raw search results (grep output, file listings).
3.  **Just-In-Time (JIT) Loading:** If you are working on Task B, do not load the technical design sections for Task D. Load only what is immediately necessary.
4.  **Offload to Memory:** If you discover a durable fact about the codebase, write it to `project-knowledge-base.md` or `progress.md` so you don't have to keep it "in mind."
5.  **Signal vs. Noise:** When running commands, drop verbose boilerplate output and retain only the specific pass/fail signals and relevant error stack traces.
6.  **Evict By Tier:** Drop transient logs before raw code, raw code before unrelated feature artifacts, and unrelated artifacts before repo memory.
7.  **Preserve The Resume Surface:** Keep the current task, proof state, blockers, and active files even when aggressively compacting.

## Token Budget Escalation

- **Amnesia Threshold**: As defined in `core-policies.md`, when the session token budget reaches 80% (approx. 160,000 tokens), you are at risk of amnesia. If condensation strategies are not enough to bring the budget down, you must end the session with `/context-session END` and hand off to a new session.
- **Persistent Memory Bloat**: If a `memories/repo/*.md` file itself exceeds the thresholds in `core-policies.md ## Memory Promotion Thresholds`, do not condense it in-session — route to `/context-compact` instead.
