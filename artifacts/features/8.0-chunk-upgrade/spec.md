# Feature Specification — Chunk Upgrade

## Metadata
- Feature name: Chunk Upgrade — Notebook LM Adaptive Tiering
- Feature slug: `8.0-chunk-upgrade`
- Delivery profile: Moderate
- Status: Draft
- Related knowledge artifact(s): `artifacts/features/8.0-chunk-upgrade/analysis.md`

## Problem Statement

Our chunking system always splits documents into fixed-size chunks regardless of document size. A 200-token document is unnecessarily fragmented; a 200K-token document is split without regard to structure. Heading context is lost during large-section splits. The semantic chunker uses Jaccard heuristics instead of real embedding similarity, and the parent-child merge is a naive fixed-count concatenation. These gaps degrade retrieval precision and LLM answer quality compared to Notebook LM's adaptive approach.

## Desired Outcomes

1. Documents below a configurable threshold are stored as single chunks (no fragmentation)
2. Every chunk carries its full heading lineage in its text (no orphaned context)
3. Semantic boundary detection uses real embedding similarity (not Jaccard)
4. Parent chunks align with actual content boundaries (not fixed-count groups)
5. Context window threshold is configurable via Settings UI and settings.json
6. Existing documents can be manually re-chunked via a document action

## Minimum Release Slice

**Ships first**: Adaptive tiering decision logic + full-doc injection (Tier 1) + context window config in Settings UI. This alone eliminates unnecessary chunking for small documents.
**Can wait**: Embedding-based semantic chunking, boundary-aware parent-child, re-chunk button.

## Success Criteria

- SC-001: A document with 500 tokens uploads as 1 chunk (was ~2 chunks with old strategy)
- SC-002: A document with nested headings produces chunks with heading paths in text
- SC-003: Changing `llm.context_window_size` in Settings UI changes chunking behavior on next upload
- SC-004: Full-doc injection chunks are queryable via vector search (indexed in Weaviate)
- SC-005: Existing documents can be re-chunked via a UI action

## In Scope

- Adaptive tiering: decision layer that chooses full-doc injection vs structural chunking
- `AdaptiveChunker` new module with `should_inject()` method
- Config: `adaptive_tiering_enabled`, `adaptive_tiering_threshold`, `adaptive_tiering_ratio` in settings.json
- Settings UI: new fields under "Ingestion & Chunking" section
- Full-doc chunks: persisted to SQLite + indexed to Weaviate (same as regular chunks)
- Heading context preservation: recursive extraction + heading path prepended to chunk text
- Embedding-based semantic boundary detection (with Jaccard fallback)
- Boundary-aware parent-child creation
- Manual "Re-chunk" button on document view (frontend + backend endpoint)
- Backward compatibility: existing documents unchanged; old `chunking_strategy` config overrides adaptive tiering

## Out Of Scope

- Content-specific chunkers (tables, code blocks, lists) — deferred to future feature
- Automatic re-chunking on ingestion pipeline upgrade

## Non-Goals

- Not replacing the existing 5 strategies; adaptive tiering is an opt-in layer on top
- Not changing the Weaviate schema or chunk repository contract
- Not adding new embedding providers — reuses existing `embedding_provider` abstraction

## Users And Stakeholders

- Primary users: Anyone uploading documents to the system (small docs benefit immediately)
- Secondary stakeholders: Users who query across multiple small documents (full-doc injection + Weaviate indexing preserves cross-doc search)

## User Stories And Key Scenarios

- US-001: As a user uploading a small FAQ document (300 words), I want it treated as a single unit so the LLM sees the full context without fragmentation.
- US-002: As a user uploading a technical manual with nested sections, I want each chunk to include its section heading so the LLM knows what topic it belongs to.
- US-003: As an admin switching to a smaller LLM model (smaller context window), I want to lower the adaptive tiering threshold via Settings so the system doesn't inject documents that exceed the new window.
- US-004: As a user who uploaded documents before the upgrade, I want to re-chunk a specific document so it benefits from the new strategy.

### Detailed Scenarios

- Scenario 1 (Happy Path — Small doc):
  - Given: adaptive tiering is enabled with threshold 38400 (30% of 128K context)
  - When: I upload a 500-token text document
  - Then: it is stored as a single chunk with `adaptive_tier="full_doc"` and indexed in Weaviate

- Scenario 2 (Happy Path — Large doc with headings):
  - Given: a document with `# Introduction > ## Background > ### Historical Context`
  - When: the system chunks it
  - Then: the chunk containing "Historical Context" text starts with `[Introduction > Background > Historical Context]`

- Scenario 3 (Config change):
  - Given: `llm.context_window_size` is set to 128000 and `adaptive_tiering_ratio` is 0.3
  - When: I upload a 40000-token document
  - Then: Tier 1 (inject) — 40000 < 38400 threshold → single chunk
  - When: I change ratio to 0.2 (threshold = 25600) via Settings UI and upload the same document
  - Then: Tier 2 (chunk) — 40000 >= 25600 → structural chunking

- Scenario 4 (Edge case — threshold override):
  - Given: user sets `adaptive_tiering_threshold` to 10000 in settings.json
  - When: `adaptive_tiering_ratio` is also set
  - Then: explicit `adaptive_tiering_threshold` wins; ratio is ignored

- Scenario 5 (Re-chunk existing document):
  - Given: a document was uploaded before the chunk upgrade
  - When: user clicks "Re-chunk" on the document page
  - Then: old chunks are deleted, document is re-chunked with the current strategy, new vectors are indexed

- Scenario 6 (Error state — embedding provider unavailable):
  - Given: semantic chunking is enabled but no embedding provider is configured
  - When: the system attempts semantic boundary detection
  - Then: falls back to Jaccard heuristic silently (no crash)

## Current Context

- Current behavior summary: 5 chunking strategies, all always-chunk, heading context lost on split, semantic chunker is Jaccard-only, parent-child is fixed-count merge
- Impacted boundaries: `backend/chunking/` (new AdaptiveChunker, changes to heading/semantic/parent-child), `backend/ingestion/service.py` (integration point), `backend/config/settings.json` (new keys), `frontend/src/screens/SettingsScreen.jsx` (new fields), `frontend/src/screens/DocumentLibrary/` (re-chunk button)
- Preserved behavior: All 5 old strategies remain; `chunking_strategy` config overrides adaptive tiering; chunk repository schema backward-compatible; Weaviate indexing unchanged
- Brownfield risk rating: Medium
  - Medium: touches 3 boundaries (chunking, ingestion, frontend), partial test coverage on chunkers, but no external API changes and no data migration needed

## Gray-Area Decisions

- Locked decisions:
  - Full-doc injection chunks are indexed to Weaviate (cross-document search preserved)
  - New uploads use new strategy; existing docs get manual "Re-chunk" action
  - Adaptive tiering threshold defaults to `max(1000, llm.context_window_size * 0.3)`
  - Explicit `adaptive_tiering_threshold` overrides the ratio calculation
- Remaining decisions that still block approval: None

## Dependencies And External Touchpoints

- DEP-001: `config.ingestion.chunking_strategy` — if set to explicit strategy (not "auto"), adaptive tiering is bypassed entirely
- DEP-002: `config.llm.context_window_size` — drives the default adaptive threshold
- DEP-003: `llm_provider` for embedding-based semantic chunking — must be available or fallback to Jaccard

## Functional Requirements

### REQ-001: Adaptive Tiering Decision
- Requirement: System decides inject-vs-chunk based on document token count vs configurable threshold
- Why it matters: Small docs shouldn't be fragmented; large docs need structural splitting
- Impacted users or scenarios: US-001, US-003
- Related success criteria: SC-001, SC-003
- Priority: Must Have
- Acceptance notes: Threshold is `max(1000, context_window_size * ratio)` when ratio-based; explicit threshold overrides
- Validation surface: Unit test on `AdaptiveChunker.should_inject()` + integration test on full ingestion pipeline

### REQ-002: Context Window Configurability
- Requirement: User can adjust `llm.context_window_size`, `adaptive_tiering_enabled`, `adaptive_tiering_ratio`, and `adaptive_tiering_threshold` via Settings UI; changes persist to settings.json
- Why it matters: Different models have different context windows; users must tune without editing JSON
- Impacted users or scenarios: US-003
- Related success criteria: SC-003
- Priority: Must Have
- Acceptance notes: `adaptive_tiering_ratio` is a slider (0.1–1.0); `adaptive_tiering_threshold` is a number input; if threshold is set (>0), ratio is ignored
- Validation surface: E2E: Settings UI → Save → reload page → values persist

### REQ-003: Heading Context Preservation
- Requirement: Multi-level heading hierarchy is extracted recursively; every child chunk's text starts with its full heading path when a section is split
- Why it matters: Without heading context, retrieved chunks are semantically orphaned
- Impacted users or scenarios: US-002, Scenario 2
- Related success criteria: SC-002
- Priority: Must Have
- Acceptance notes: Heading path format is `[Parent > Child > Grandchild]` prepended to text. Only applies to heading-aware chunker path.
- Validation surface: Unit test on `HeadingAwareChunker` with nested markdown

### REQ-004: Full-Doc Chunk Indexing
- Requirement: Full-doc injection chunks are indexed into Weaviate (same as regular chunks), preserving cross-document search capability
- Why it matters: Users should be able to find information across multiple small documents via vector search
- Impacted users or scenarios: US-001
- Related success criteria: SC-004
- Priority: Should Have
- Acceptance notes: Chunk has `adaptive_tier="full_doc"` in metadata. Embedding + Weaviate insert happens as usual.
- Validation surface: Integration test: upload small doc → verify Weaviate has 1 entry for that document

### REQ-005: Embedding-Based Semantic Chunking
- Requirement: Semantic chunker uses embedding cosine similarity for boundary detection when an embedding provider is available; falls back to Jaccard otherwise
- Why it matters: Jaccard misses synonyms and topic shifts; real embeddings produce better chunk boundaries
- Impacted users or scenarios: US-002 (indirect — better boundaries = better retrieval)
- Related success criteria: None directly (quality improvement, not a ship gate)
- Priority: Should Have
- Acceptance notes: Embedding provider is optional; no crash if unavailable. Fallback is transparent.
- Validation surface: Unit test with mock embedding provider + test with provider=None

### REQ-006: Boundary-Aware Parent-Child
- Requirement: Parent chunks are created at semantic/heading boundaries, not by fixed-count merging
- Why it matters: Current naive merge creates semantically incoherent parent chunks by concatenating unrelated content
- Impacted users or scenarios: US-002 (indirect — better parent context = better RAG)
- Related success criteria: None directly
- Priority: Could Have
- Acceptance notes: A document with 3 distinct sections produces exactly 3 parent chunks (not ceil(N/4))
- Validation surface: Unit test on `ParentChildChunker` with multi-section document

### REQ-007: Manual Re-Chunk
- Requirement: User can trigger re-chunking of an existing document from the document view page
- Why it matters: Documents uploaded before the upgrade benefit from the new strategy
- Impacted users or scenarios: US-004, Scenario 5
- Related success criteria: SC-005
- Priority: Should Have
- Acceptance notes: Re-chunk deletes old chunks + old vectors, then re-runs ingestion pipeline's chunk-and-index step
- Validation surface: E2E: upload old doc → upgrade chunker → click Re-chunk → verify new chunk count

## Non-Functional Requirements

- NFR-001 Performance: Embedding-based semantic chunking must not exceed 5s per document on average. If provider latency exceeds this, fallback to Jaccard silently.
  - Linked ACs: AC-006

- NFR-002 Backward Compatibility: All existing chunk data must remain readable and renderable in the chat UI and X-Ray panel after upgrade. New `ChunkData` fields (`heading_path`, `content_type`, `adaptive_tier`) must be optional/nullable.
  - Linked ACs: AC-007, AC-008

- NFR-003 Config Persistence: Settings UI changes must persist across page reloads and server restarts (saved to settings.json).
  - Linked ACs: AC-003

## Constraints

- Technical: Must reuse existing `embedding_provider` abstraction; no new external dependencies
- Business: Must be backward-compatible with existing data
- Delivery: Phased rollout — each phase independently shippable and testable

## Assumptions

- ASM-001: The existing embedding provider (OpenAI-compatible) can efficiently embed short sentences for semantic boundary detection
- ASM-002: The Weaviate schema accepts new metadata fields without migration (schema-less)
- ASM-003: Users will accept a manual re-chunk action rather than automatic migration

## Risks

- RISK-001: Embedding-based semantic chunking increases ingestion latency / Risk: Low — Jaccard fallback exists; threshold of 5s before fallback
- RISK-002: Full-doc injection may overflow context window in complex sessions / Risk: Low — threshold is 30% of context window by default; user-configurable
- RISK-003: Re-chunking deletes old vectors — if re-chunk fails, document has no index / Risk: Medium — implement as atomic operation (delete old, if new fails, don't delete old)

## Open Questions

- Q-001: Should the re-chunk button appear on the document list or only on the document detail view?
  - Type: Non-blocking
  - Owner: UX
  - Next step: Decide during implementation — recommended: both (icon on list row + button on detail)

## Acceptance Criteria

- [ ] AC-001 Linked REQ: REQ-001
  - Validation method: Unit test
  - Proof target: `python -c "from chunking.adaptive_chunker import AdaptiveChunker; a = AdaptiveChunker(threshold=1000); assert a.should_inject('hello ' * 200); assert not a.should_inject('hello ' * 2000)"`

- [ ] AC-002 Linked REQ: REQ-001
  - Validation method: Integration test
  - Proof target: Upload a 500-token document via ingestion endpoint → verify 1 chunk with `adaptive_tier="full_doc"`

- [ ] AC-003 Linked REQ: REQ-002
  - Validation method: E2E test
  - Proof target: Open Settings → change `adaptive_tiering_ratio` from 0.3 to 0.2 → Save → reload → verify value persists in settings.json and re-renders in UI

- [ ] AC-004 Linked REQ: REQ-003
  - Validation method: Unit test
  - Proof target: `python -c "from chunking.heading_aware_chunker import HeadingAwareChunker; h = HeadingAwareChunker(50); chunks = h.chunk('# A\n## B\n### C\n' + 'word ' * 500); assert all('[A > B > C]' in c.text for c in chunks)"`

- [ ] AC-005 Linked REQ: REQ-004
  - Validation method: Integration test
  - Proof target: Upload small doc → query Weaviate for its chunk → verify result returned (not empty)

- [ ] AC-006 Linked REQ: REQ-005 / NFR-001
  - Validation method: Unit test with mock
  - Proof target: `python -c "from chunking.semantic_chunker import SemanticChunker; s = SemanticChunker(512, embedding_provider=None); chunks = s.chunk('Some text. Different topic now. Back to original.')"` — no crash

- [ ] AC-007 Linked REQ: NFR-002
  - Validation method: Schema check
  - Proof target: Existing tests for citation, context assembly, and X-Ray pass without modification after new fields added

- [ ] AC-008 Linked REQ: REQ-007
  - Validation method: E2E test
  - Proof target: Upload document → verify chunk count N → click "Re-chunk" → verify different chunk count (or same count with different chunk IDs)

- [ ] AC-009 Linked REQ: REQ-006
  - Validation method: Unit test
  - Proof target: `python -c "from chunking.parent_child_chunker import ParentChildChunker; p = ParentChildChunker(512); chunks = p.chunk('# A\n...\n## B\n...\n# C\n...'); parents = [c for c in chunks if c.metadata.get('parent_chunk')]; assert len(parents) == 3"`

## Related ADRs

None — no ADR conflicts found (ADR log is empty).

## Notes

This spec was written after the research phase (analysis.md) and plan phase (plan.md, tasks.md) were already completed. The spec formalizes the requirements that the existing plan already covers. The plan's 4-phase delivery sequence remains valid. The spec adds:
- Explicit acceptance criteria with proof commands
- NFR-AC linkage
- Formal scenario definitions (Gherkin style)
- Decision records from grilling (full-doc → Weaviate, re-chunk button)
