# Task Breakdown

## Metadata
- Feature name: Chunk Upgrade — Notebook LM Adaptive Tiering
- Feature slug: `8.0-chunk-upgrade`
- Date: 2026-06-30
- Status: Draft

## Heuristic Citations

- LH-001: Prefer additive/nullable fields over migrations — `ChunkData` new fields are optional, no schema migration needed.

---

### Phase 1: Config + AdaptiveChunker + Full-Doc Injection

Goal: Adaptive tiering decision + full-doc injection + Settings UI. A 500-token doc produces 1 chunk.
Story ID: US-001, US-003
Priority: P1
Acceptance criteria covered: AC-001, AC-002, AC-003, AC-005
Independent proof: `python -c "from chunking.adaptive_chunker import AdaptiveChunker; a = AdaptiveChunker(threshold=1000); assert a.should_inject('hello ' * 200); assert not a.should_inject('hello ' * 2000)"`
Completion criteria:
- [ ] CC-001 Config keys added to `IngestionSettings` + `settings.json`
- [ ] CC-002 `AdaptiveChunker.should_inject()` unit test passes
- [ ] CC-003 Full-doc injection produces `adaptive_tier="full_doc"` chunks indexed to Weaviate
- [ ] CC-004 Settings UI renders adaptive tiering fields

Tasks:
- [ ] TASK-001-Config schema keys
- [ ] TASK-002-AdaptiveChunker module + ChunkData fields
- [ ] TASK-003-Wire AdaptiveChunker into ingestion pipeline
- [ ] TASK-004-Settings UI adaptive tiering fields
- [ ] TASK-005-Phase 1 tests

#### TASK-001
  Status: Not Started
  Routing: AFK
  Summary: Add `adaptive_tiering_enabled`, `adaptive_tiering_threshold`, `adaptive_tiering_ratio` to `IngestionSettings` in `schemas/settings.py` and default values in `config/settings.json`
  Plan reference: Phase 1, CC-001
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `backend/schemas/settings.py`, `backend/config/settings.json`
  Depends on: None
  Can run in parallel: no
  Proving command or proof: `python -c "from schemas.settings import IngestionSettings; s = IngestionSettings(); assert s.adaptive_tiering_enabled == True; assert s.adaptive_tiering_threshold is None; assert s.adaptive_tiering_ratio == 0.3"`
  Validation evidence:
  Session note:

#### TASK-002
  Status: Not Started
  Routing: AFK
  Summary: Create `AdaptiveChunker` module with `should_inject()` and threshold computation. Add `heading_path`, `content_type`, `adaptive_tier` nullable fields to `ChunkData` dataclass.
  Plan reference: Phase 1, CC-002, CC-003
  Linked requirement(s): REQ-001, REQ-004
  Linked acceptance criteria: AC-001
  Affected file(s) or module(s): `backend/chunking/adaptive_chunker.py` (new), `backend/chunking/base.py` (ChunkData fields)
  Depends on: TASK-001 (needs IngestionSettings config)
  Can run in parallel: no
  Proving command or proof: `python -c "from chunking.adaptive_chunker import AdaptiveChunker; a = AdaptiveChunker(threshold=1000); assert a.should_inject('hello ' * 200); assert not a.should_inject('hello ' * 2000); assert a.threshold == 1000"`
  Validation evidence:
  Session note:

#### TASK-003
  Status: Not Started
  Routing: AFK
  Summary: Wire AdaptiveChunker into `chunk_and_index_document()` in `ingestion/service.py`. When `adaptive_tiering_enabled` and strategy is not explicit and doc is below threshold → create single `ChunkData(adaptive_tier="full_doc")` and index to Weaviate. When above threshold → proceed with normal strategy dispatch.
  Plan reference: Phase 1, CC-003
  Linked requirement(s): REQ-001, REQ-004
  Linked acceptance criteria: AC-002, AC-005
  Affected file(s) or module(s): `backend/ingestion/service.py`
  Depends on: TASK-002
  Can run in parallel: no
  Proving command or proof: Integration test: upload 500-token doc → verify 1 chunk in DB with `adaptive_tier="full_doc"` + 1 vector in Weaviate
  Validation evidence:
  Session note:

#### TASK-004
  Status: Not Started
  Routing: HITL
  Summary: Add adaptive tiering UI fields to "Ingestion & Chunking" section in SettingsScreen.jsx: toggle for `adaptive_tiering_enabled`, ratio slider (0.1–1.0), optional threshold number input. Show tooltip explaining threshold vs ratio.
  Plan reference: Phase 1, CC-004
  Linked requirement(s): REQ-002
  Linked acceptance criteria: AC-003
  Affected file(s) or module(s): `frontend/src/screens/SettingsScreen.jsx`
  Depends on: TASK-001
  Can run in parallel: no
  Proving command or proof: E2E: Open Settings → toggle adaptive tiering → change ratio → Save → reload → values persist
  Validation evidence:
  Session note:

#### TASK-005
  Status: Not Started
  Routing: AFK
  Summary: Unit tests for `AdaptiveChunker.should_inject()` (AC-001), integration test for full-doc upload → Weaviate verification (AC-002, AC-005), E2E test for settings persistence (AC-003).
  Plan reference: Phase 1 validation
  Linked requirement(s): REQ-001, REQ-002, REQ-004
  Linked acceptance criteria: AC-001, AC-002, AC-003, AC-005
  Affected file(s) or module(s): `backend/tests/chunking/test_adaptive_chunker.py` (new), `backend/tests/ingestion/` (new test file)
  Depends on: TASK-003, TASK-004
  Can run in parallel: no
  Proving command or proof: `pytest backend/tests/chunking/test_adaptive_chunker.py backend/tests/ingestion/ -v 2>&1 | tail -20`
  Validation evidence:
  Session note:

---

### Phase 2: Heading Context Preservation

Goal: Every chunk from heading-aware chunker includes full heading path in text.
Story ID: US-002
Priority: P2
Acceptance criteria covered: AC-004
Independent proof: `python -c "from chunking.heading_aware_chunker import HeadingAwareChunker; h = HeadingAwareChunker(50); chunks = h.chunk('# A\n## B\n### C\n' + 'word ' * 500); assert all('[A > B > C]' in c.text for c in chunks)"`
Completion criteria:
- [ ] CC-005 Heading path prepended to chunk text in `[Parent > Child]` format
- [ ] CC-006 Unit test with nested headings passes (AC-004)

Tasks:
- [ ] TASK-006-Recursive heading path
- [ ] TASK-007-Phase 2 tests

#### TASK-006
  Status: Not Started
  Routing: AFK
  Summary: Refactor `HeadingAwareChunker._extract_sections()` to track heading hierarchy recursively using a stack of `(level, heading_name)` pairs. When a new heading is encountered, build the full path by popping headings at deeper levels and pushing the new one. Prepend path string `[A > B > C]` to each chunk's text. Update `ChunkData.heading_path` metadata.
  Plan reference: Phase 2, CC-005
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/chunking/heading_aware_chunker.py`
  Depends on: Phase 1 complete (ChunkData fields exist)
  Can run in parallel: no
  Proving command or proof: `python -c "from chunking.heading_aware_chunker import HeadingAwareChunker; h = HeadingAwareChunker(50); chunks = h.chunk('# A\n## B\n### C\n' + 'word ' * 500); assert all('[A > B > C]' in c.text for c in chunks); print(f'Chunks: {len(chunks)}, Path present: OK')"`
  Validation evidence:
  Session note:

#### TASK-007
  Status: Not Started
  Routing: AFK
  Summary: Unit test verifying heading path prepending for multi-level nested markdown, single-level documents, and documents without headings (fallback). Uses proof command from AC-004.
  Plan reference: Phase 2 validation
  Linked requirement(s): REQ-003
  Linked acceptance criteria: AC-004
  Affected file(s) or module(s): `backend/tests/chunking/test_heading_chunker.py` (new)
  Depends on: TASK-006
  Can run in parallel: no
  Proving command or proof: `pytest backend/tests/chunking/test_heading_chunker.py -v 2>&1 | tail -10`
  Validation evidence:
  Session note:

---

### Phase 3: Embedding-Based Semantic + Boundary Parent-Child

Goal: Semantic boundary detection uses real embeddings when available; parent-child uses content boundaries.
Priority: P2
Acceptance criteria covered: AC-006, AC-009
Independent proof: `python -c "from chunking.semantic_chunker import SemanticChunker; s = SemanticChunker(512, embedding_provider=None); chunks = s.chunk('Some text. Different topic now. Back to original.')"` — no crash
Completion criteria:
- [ ] CC-007 SemanticChunker accepts optional `embedding_provider`, falls back to Jaccard
- [ ] CC-008 ParentChildChunker groups by section boundaries
- [ ] CC-009 Unit tests pass for both (AC-006, AC-009)

Tasks:
- [P] TASK-008-Semantic embedding boundaries
- [P] TASK-009-Boundary parent-child
- [ ] TASK-010-Phase 3 tests

#### TASK-008 `[P]`
  Status: Not Started
  Routing: AFK
  Ownership boundary: semantic_chunker.py + embedding_provider integration
  Summary: Update `SemanticChunker` to accept optional `embedding_provider` parameter. When provider is available: split text into sentences, embed adjacent sentence pairs, compute cosine similarity, create boundaries at low-similarity points. When provider is None or embedding exceeds 5s: fall back to existing Jaccard heuristic silently. Integrate with existing `get_embedding_provider()` from `providers.factory`.
  Plan reference: Phase 3, CC-007
  Linked requirement(s): REQ-005
  Linked acceptance criteria: AC-006
  Linked NFRs: NFR-001 (5s timeout → fallback)
  Affected file(s) or module(s): `backend/chunking/semantic_chunker.py`
  Depends on: Phase 1 complete (ChunkData fields exist)
  Can run in parallel: yes (independent of TASK-009)
  Proving command or proof: `python -c "from chunking.semantic_chunker import SemanticChunker; s1 = SemanticChunker(512, embedding_provider=None); c1 = s1.chunk('A. B. C.'); assert not s1.fallback_applied; print('OK: Jaccard path'); s2 = SemanticChunker(512, embedding_provider=MockProvider()); c2 = s2.chunk('A. B. C.'); print('OK: embedding path')"`
  Validation evidence:
  Session note:

#### TASK-009 `[P]`
  Status: Not Started
  Routing: AFK
  Ownership boundary: parent_child_chunker.py
  Summary: Update `ParentChildChunker` to create parent groups from heading/semantic boundaries instead of fixed `children_per_parent`. When text has N distinct sections (heading- or semantically-derived), produce exactly N parent chunks. Use section boundaries from heading extraction or semantic boundary detection. Keep the `create_parent_child_relationships()` method for linking.
  Plan reference: Phase 3, CC-008
  Linked requirement(s): REQ-006
  Linked acceptance criteria: AC-009
  Affected file(s) or module(s): `backend/chunking/parent_child_chunker.py`
  Depends on: Phase 2 (heading utils) — minimal dependency: can use basic boundary detection
  Can run in parallel: yes (independent of TASK-008)
  Proving command or proof: `python -c "from chunking.parent_child_chunker import ParentChildChunker; p = ParentChildChunker(512); chunks = p.chunk('# A\n...\n## B\n...\n# C\n...'); parents = [c for c in chunks if c.metadata.get('parent_chunk')]; assert len(parents) == 3; print(f'OK: {len(parents)} parent chunks')"`
  Validation evidence:
  Session note:

#### TASK-010
  Status: Not Started
  Routing: AFK
  Summary: Unit tests for embedding-based semantic fallback (AC-006) and boundary parent-child (AC-009). Mock provider for embedding path. Test multi-section document with exactly 3 parent groups.
  Plan reference: Phase 3 validation
  Linked requirement(s): REQ-005, REQ-006
  Linked acceptance criteria: AC-006, AC-009
  Linked NFRs: NFR-001 (5s timeout)
  Affected file(s) or module(s): `backend/tests/chunking/test_semantic_chunker.py` (new), `backend/tests/chunking/test_parent_child_chunker.py` (new)
  Depends on: TASK-008, TASK-009
  Can run in parallel: no
  Proving command or proof: `pytest backend/tests/chunking/test_semantic_chunker.py backend/tests/chunking/test_parent_child_chunker.py -v 2>&1 | tail -10`
  Validation evidence:
  Session note:

---

### Phase 4: Re-chunk Button

Goal: Users can re-chunk existing documents from the UI.
Story ID: US-004
Priority: P2
Acceptance criteria covered: AC-008
Independent proof: Upload document → verify chunk count N → click "Re-chunk" → verify different chunk count (or same count with different chunk IDs)
Completion criteria:
- [ ] CC-010 Re-chunk is atomic (preserves old chunks on failure)
- [ ] CC-011 Frontend "Re-chunk" button on document detail view
- [ ] CC-012 E2E test passes (AC-008)

Tasks:
- [ ] TASK-011-Atomic re-chunk
- [ ] TASK-012-Frontend button + E2E test

#### TASK-011
  Status: Not Started
  Routing: AFK
  Summary: Make `chunk_and_index_document()` safe for re-chunk: save old chunks/vectors before deletion, attempt new chunk+index, delete old only on success. On failure, restore old state. The simplest approach: in `reindex_document()` in `routers/documents.py`, read existing chunk count before calling `chunk_and_index_document()`, and if the result has 0 chunks, restore from backup.
  Plan reference: Phase 4, CC-010
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-008
  Risk addressed: RISK-003 (re-chunk failure loses data)
  Affected file(s) or module(s): `backend/routers/documents.py`, `backend/ingestion/service.py`, `backend/repositories/chunk_repository.py`
  Depends on: Phase 1 (AdaptiveChunker wired in pipeline)
  Can run in parallel: no
  Proving command or proof: Unit test: mock `chunk_and_index_document` to raise → verify old chunks still present. Integration test: re-chunk a document → verify chunk IDs changed.
  Validation evidence:
  Session note:

#### TASK-012
  Status: Not Started
  Routing: HITL
  Summary: Add "Re-chunk" button to document detail view (and optionally document list row icon). Button calls existing `POST /documents/{id}/reindex` endpoint. Show loading state during re-chunk, then refresh chunk count. Add E2E test (AC-008).
  Plan reference: Phase 4, CC-011, CC-012
  Linked requirement(s): REQ-007
  Linked acceptance criteria: AC-008
  Affected file(s) or module(s): `frontend/src/screens/DocumentDetail.jsx` (or equivalent), `frontend/src/api/documents.js`
  Depends on: TASK-011
  Can run in parallel: no
  Proving command or proof: E2E: upload doc → verify chunk count → click Re-chunk → verify new chunk count → check old chunks removed from Weaviate
  Validation evidence:
  Session note:

---

### Phase 5: Documentation Update

Goal: All chunking-related docs in `documents/` reflect the upgraded system.
Priority: P3
Acceptance criteria covered: NFR-002 (backward compat docs)
Independent proof: Grep each doc for outdated strategy references
Completion criteria:
- [ ] CC-DOC-001 CHUNKING_STRATEGIES.md has adaptive tiering, heading context, embedding semantic, boundary parent-child, re-chunk
- [ ] CC-DOC-002 system-architecture.md chunking section updated
- [ ] CC-DOC-003 api-flows.md settings + reindex updated
- [ ] CC-DOC-004 database-schema.md notes new metadata fields

Tasks:
- [ ] TASK-013-Documentation update

#### TASK-013
  Status: Not Started
  Routing: AFK
  Summary: Update `documents/CHUNKING_STRATEGIES.md` (add adaptive tiering section, update each strategy with new behavior, new config param table), `documents/system-architecture.md` (update component map + chunking description), `documents/api-flows.md` (add adaptive tiering fields to settings example, update reindex endpoint), `documents/database-schema.md` (note new metadata_json fields: `heading_path`, `adaptive_tier`, `content_type`).
  Plan reference: Phase 5 (CC-DOC-001 through CC-DOC-004)
  Linked requirement(s): NFR-002 (backward compatibility — docs reflect new fields)
  Affected file(s) or module(s): `documents/CHUNKING_STRATEGIES.md`, `documents/system-architecture.md`, `documents/api-flows.md`, `documents/database-schema.md`
  Depends on: TASK-012 (Phase 4 complete — full feature set shipped)
  Can run in parallel: no
  Proving command or proof: `grep -c "adaptive_tiering\|heading_path\|boundary-aware\|AdaptiveChunker" documents/*.md` — verify all 4 docs have new content
  Validation evidence:
  Session note:

## Notes Per Task

No additional notes.

## Completion Notes

- What was delivered:
- What was deferred:
- What needs follow-up:

## Resume Notes

- Current phase:
- Next recommended task:
- Active blocker:
- Last validation evidence added:
- Exact next command or proof to run:
