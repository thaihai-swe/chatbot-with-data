# Domain — Patterns

> Ownership: Collaborative — skill-updated + user-maintained.
> Updated by: `/context-memory` post-ship sync when a new reusable pattern is confirmed by a completed feature.
> Read by: `/spec-plan`, `/spec-implement` to reuse proven approaches and avoid reinvention.

Proven implementation patterns for this domain.

## Gated SSE Stream Pipeline Pattern

When to use: When executing user chat queries that require citation extraction and grounding verification.

Key implementation notes:
- Hook the SSE endpoint router to call the `StreamingOrchestrator`.
- The orchestrator first verifies safety and checks grounding via the grounding service.
- If checks pass, it connects to the LLM completion API and yields token chunks, citations, and status messages following SSE serialization formatting.
- Cleanly capture cancellations at each yielding step.

---

## Strategy Pattern for Custom Chunkers

When to use: Splitting diverse uploaded document file types into semantic text blocks.

Key implementation notes:
- Implement a base chunker class `BaseChunker`.
- Create specialized implementations such as `AdaptiveChunker`, `HeadingAwareChunker`, `ParentChildChunker`, and `SemanticChunker`.
- Keep chunking strategy decoupled from ingestion storage logic.

