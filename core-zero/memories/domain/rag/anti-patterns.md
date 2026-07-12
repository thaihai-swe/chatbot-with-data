# Domain — Anti-Patterns

> Ownership: Collaborative — skill-updated + user-maintained.
> Updated by: `/context-memory` post-ship sync when a failure mode is observed during a completed feature.
> Read by: `/spec-plan`, `/harness-verify` to prevent known failure modes from recurring.

Known failure modes for this domain.

## Bypassing Pre-generation Safety and Grounding Check

Why it fails: Calling the OpenAI client directly or bypassing the safety/grounding validation steps can result in hallucinated or unsafe responses being delivered to the user, defeating the RAG constraints.

What to do instead: Always route LLM completions through the `StreamingOrchestrator` which systematically executes `safety_service.check_query` and `grounding_service.evaluate_evidence` before starting LLM text generation.

---

## Direct Database Manipulation in Route Handlers

Why it fails: Directly executing raw SQL queries or DB connection management inside API endpoints without relying on established repository patterns leads to resource leakage (connections left unclosed) and duplicated queries.

What to do instead: Encapsulate database retrieval/commits inside dedicated service or repository modules, and use the `@contextmanager def get_connection()` connection manager for thread-safe access.

