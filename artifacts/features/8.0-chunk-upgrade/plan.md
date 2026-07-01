# Implementation Plan

## Metadata

- Feature slug: `8.0-chunk-upgrade`
- Date: 2026-06-30
- Status: Draft

---

## Part 1: Technical Design

### Comprehensive Design

#### Design Summary

Introduce an adaptive tiering layer (`AdaptiveChunker`) at the ingestion pipeline entry point that decides whether to inject a document whole (Tier 1) or dispatch to structure-aware chunking (Tier 2). Tier 1 creates a single `ChunkData` with `adaptive_tier="full_doc"` and indexes it to Weaviate. Tier 2 enhances the existing heading-aware, semantic, and parent-child chunkers with heading-path prepending, embedding-based boundary detection (with Jaccard fallback), and boundary-aware parent grouping. A "Re-chunk" button on the frontend reuses the existing `/documents/{id}/reindex` endpoint with an atomic delete-after-index pattern.

#### Current State

- `backend/chunking/dispatcher.py` routes to 5 strategies, each of which always splits text regardless of document size
- `SemanticChunker` uses Jaccard-only heuristics; `use_embeddings=False` is hardcoded
- `HeadingAwareChunker._extract_sections()` tracks only the immediate heading name, not the sibling/parent hierarchy
- `ParentChildChunker` groups by fixed `children_per_parent` count (default 4), not content boundaries
- `chunk_and_index_document()` in `ingestion/service.py` deletes old chunks before creating new ones (non-atomic for re-chunk)
- No config keys exist for adaptive tiering
- Settings UI shows chunk_size/overlap but no adaptive tiering controls
- `/documents/{id}/reindex` endpoint already exists and could serve as the re-chunk mechanism

#### Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│ chunk_and_index_document()                          │
│  ┌───────────────────────────────────────────────┐  │
│  │ 1. Resolve strategy from config                │  │
│  │    (if "fixed" → source-type default)          │  │
│  └──────────────┬────────────────────────────────┘  │
│                 ▼                                    │
│  ┌───────────────────────────────────────────────┐  │
│  │ 2. AdaptiveChunker.should_inject(text, config) │  │
│  │    (skipped if config.adaptive_tiering_enabled │  │
│  │     is False or chunking_strategy is explicit) │  │
│  └──────┬────────────────────┬───────────────────┘  │
│         ▼ True               ▼ False                 │
│  ┌──────────────┐   ┌───────────────────────────┐   │
│  │ Tier 1:      │   │ Tier 2: Dispatch to       │   │
│  │ Create single│   │ existing strategy with     │   │
│  │ ChunkData    │   │ enhancements:              │   │
│  │ adaptive_tier│   │ • heading_path prepended   │   │
│  │ ="full_doc"  │   │ • embedding boundary       │   │
│  │ Index → W.   │   │ • boundary parent-child    │   │
│  └──────────────┘   └───────────────────────────┘   │
│  ┌───────────────────────────────────────────────┐  │
│  │ 3. Safety check → Index to Weaviate           │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**New modules:**
- `backend/chunking/adaptive_chunker.py` — `AdaptiveChunker` class with `should_inject()` and threshold computation
- `backend/chunking/heading_utils.py` — shared heading hierarchy utilities (extract tree, build path string)

**Changes to existing modules:**
- `backend/chunking/base.py` — add `heading_path`, `adaptive_tier`, `content_type` fields to `ChunkData`
- `backend/chunking/heading_aware_chunker.py` — recursive heading extraction with full path prepending
- `backend/chunking/semantic_chunker.py` — accept optional `embedding_provider`, use cosine similarity when available
- `backend/chunking/parent_child_chunker.py` — use heading/semantic boundaries for parent grouping
- `backend/chunking/service.py` — (no changes needed; `ChunkingService` delegates to dispatcher)
- `backend/chunking/dispatcher.py` — add `"adaptive"` as a meta-strategy that dispatcher can route through
- `backend/ingestion/service.py` — integrate adaptive tiering check in `chunk_and_index_document()`; atomic re-chunk pattern
- `backend/schemas/settings.py` — add `adaptive_tiering_enabled`, `adaptive_tiering_threshold`, `adaptive_tiering_ratio` to `IngestionSettings`
- `frontend/src/screens/SettingsScreen.jsx` — add adaptive tiering UI fields
- `frontend/src/screens/DocumentLibrary/` — add "Re-chunk" button

#### Data Flow & Interfaces

**Adaptive tiering decision flow (new upload):**
1. `process_ingestion_attempt()` → `_finalize_successful_ingestion()` → `chunk_and_index_document()`
2. `chunk_and_index_document()` resolves `strategy` from config
3. If `adaptive_tiering_enabled` and strategy is not explicit: check `AdaptiveChunker.should_inject(text)`
4. If inject → create single `ChunkData` with `adaptive_tier="full_doc"`, persist via `ChunkRepository`, index via `IndexingService`
5. If not inject → proceed with normal strategy dispatch (heading_aware, semantic, etc.)

**ChunkData schema additions:**
```python
@dataclass
class ChunkData:
    ...
    heading_path: str | None = None
    content_type: str | None = None    # "text", "table", "code"
    adaptive_tier: str | None = None   # "full_doc", None for regular chunks
```

**Settings schema additions (`IngestionSettings`):**
```python
adaptive_tiering_enabled: bool = True
adaptive_tiering_threshold: int | None = None   # explicit, >0 overrides ratio
adaptive_tiering_ratio: float = 0.3             # 0.1–1.0, fraction of context_window_size
```

**Threshold computation:**
```python
if adaptive_tiering_threshold is not None and adaptive_tiering_threshold > 0:
    return adaptive_tiering_threshold
return max(1000, context_window_size * adaptive_tiering_ratio)
```

**Re-chunk flow:**
1. Frontend calls `POST /documents/{id}/reindex` (existing endpoint)
2. `reindex_document()` saves existing chunks/vectors, calls `chunk_and_index_document()`
3. Inside `chunk_and_index_document()`: try new chunk+index, if OK delete old, if fail restore old
4. Returns updated chunk count

#### Key Decisions & Tradeoffs

| Decision | Why | Tradeoff |
|----------|-----|----------|
| AdaptiveChunker as separate module | Clean separation of concerns, independently testable | One extra file; could have been a method on dispatcher |
| Reuse `/reindex` endpoint for re-chunk | Zero new backend surface; existing endpoint already does chunk-and-index | Endpoint name says "reindex" not "rechunk" — frontend can call it with user-facing label "Re-chunk" |
| Heading path prepended to chunk text (not separate field) | LLM sees heading context directly in the input text; no special handling needed | Duplicates heading info if stored separately; `heading_path` field is available for metadata queries |
| Embedding semantic chunking reuses existing `embedding_provider` abstraction | No new provider plumbing; same retry/timeout logic applies | Embedding latency for sentence-pair similarity adds overhead; 5s timeout before Jaccard fallback mitigates this |
| Boundary parent-child uses existing section/group boundaries | Simple: sections from heading/semantic chunker become parents instead of fixed-count groups | Section boundaries may be uneven; fine for RAG where parent context is a full section |
| Atomic re-chunk = save old, try new, cleanup | Prevents data loss on re-chunk failure | Slightly more complex; only matters for re-chunk (new uploads have no old chunks) |
| Configurable ratio (0.1–1.0) independent of explicit threshold | Users can rely on ratio for auto-scaling or set an exact number for precision | Two competing configs; priority rule is clear (explicit wins) |

#### Non-Functional Considerations

- **Performance:** Embedding-based semantic chunking may add latency; 5s timeout with Jaccard fallback (NFR-001, AC-006)
- **Backward Compatibility:** All new `ChunkData` fields are optional/nullable; existing chunks render unchanged (NFR-002, AC-007)
- **Config Persistence:** Settings UI writes to `settings.json` via existing `SettingsManager.update()` (NFR-003, AC-003)
- **Safety:** Re-chunk goes through same safety check as new uploads (injected full-doc chunks are also safety-checked)

#### Protected Behavior

- Existing `chunking_strategy` config (if set to an explicit strategy like "semantic", "parent_child") bypasses adaptive tiering entirely — backward compat for users with custom strategies
- All 5 old chunking strategies remain unchanged and selectable via `chunking_strategy`
- Chunk repository schema unchanged; new fields are additive
- Weaviate indexing unchanged; full-doc injection chunks follow the same embed + insert path

---

## Part 2: Delivery Strategy

### Execution Context
- Delivery profile: Moderate
- Locked spec decisions:
  - Full-doc injection chunks indexed to Weaviate (AC-005)
  - Re-chunk is manual per-document (AC-008)
  - Threshold = `max(1000, context_window_size * ratio)` with explicit override
  - Embedding semantic has Jaccard fallback (AC-006)
  - Old `chunking_strategy` config overrides adaptive tiering

### First Delivery Slice
- Smallest useful slice: Adaptive tiering decision logic + full-doc injection + config keys
- Why this slice goes first: Eliminates unnecessary chunking for small documents immediately; highest value, lowest risk
- Proof when done: Upload a 500-token doc → 1 chunk with `adaptive_tier="full_doc"` in Weaviate

### Execution Phases

#### Phase 1: Config + AdaptiveChunker + Full-Doc Injection
- Goal: Ship adaptive tiering decision + full-doc injection + Settings UI. A 500-token doc produces 1 chunk.
- Enabled scenario: US-001 (small docs), US-003 (configurable threshold)
- Entry proof: Config schema compiles, new keys load from settings.json
- Exit proof: Upload 500-token doc → 1 chunk in DB + 1 vector in Weaviate
- Completion criteria:
  - CC-001: `adaptive_tiering_enabled`, `adaptive_tiering_threshold`, `adaptive_tiering_ratio` added to `IngestionSettings`
  - CC-002: `AdaptiveChunker.should_inject()` passes unit tests
  - CC-003: `ChunkData` has new fields (`heading_path`, `adaptive_tier`, `content_type`)
  - CC-004: Ingestion pipeline routes small docs through Tier 1 (single chunk)
  - CC-005: Full-doc chunks indexed to Weaviate with `adaptive_tier="full_doc"`
  - CC-006: Settings UI shows new fields under "Ingestion & Chunking" section
  - CC-007: E2E: change ratio → save → reload → value persists
  - CC-DOC-001: `documents/CHUNKING_STRATEGIES.md` updated with adaptive tiering overview + new config table
  - CC-DOC-002: `documents/system-architecture.md` chunking section updated with adaptive tiering description
  - CC-DOC-003: `documents/api-flows.md` settings response example includes new adaptive tiering fields

#### Phase 2: Heading Context Preservation
- Goal: Every chunk from heading-aware chunker includes full heading path in text.
- Enabled scenario: US-002 (heading context)
- Entry proof: Preexisting heading-aware chunker with `_extract_sections()`
- Exit proof: Chunk for "Historical Context" under "Introduction > Background" starts with `[Introduction > Background > Historical Context]`
- Completion criteria:
  - CC-008: `HeadingAwareChunker._extract_sections()` uses recursive hierarchy tracking
  - CC-009: Heading path prepended to chunk text in format `[Parent > Child]`
  - CC-010: Unit test with nested headings passes (AC-004)
  - CC-DOC-004: `documents/CHUNKING_STRATEGIES.md` heading-aware section updated with recursive heading path + heading context example

#### Phase 3: Embedding-Based Semantic + Boundary Parent-Child
- Goal: Semantic boundary detection uses real embeddings when available; parent-child uses content boundaries.
- Enabled scenario: US-002 (indirect — better boundaries)
- Entry proof: Embedding provider available or falls back gracefully
- Exit proof: Multi-section doc produces 3 parent chunks; semantic chunker works with and without provider
- Completion criteria:
  - CC-011: `SemanticChunker` accepts optional `embedding_provider`, uses cosine similarity for boundaries
  - CC-012: Falls back to Jaccard silently when provider is None or exceeds 5s (AC-006)
  - CC-013: `ParentChildChunker` groups by section boundaries instead of fixed count (AC-009)
  - CC-014: Unit tests pass for both providers
  - CC-DOC-005: `documents/CHUNKING_STRATEGIES.md` semantic + parent-child sections updated with embedding-based boundaries + boundary-aware grouping

#### Phase 4: Re-chunk Button
- Goal: Users can re-chunk existing documents from the UI.
- Enabled scenario: US-004 (re-chunk legacy docs)
- Entry proof: `/documents/{id}/reindex` endpoint exists
- Exit proof: Upload old doc → click Re-chunk → verify new chunk count
- Completion criteria:
  - CC-015: Re-chunk is atomic (preserves old chunks on failure)
  - CC-016: Frontend "Re-chunk" button on document detail view
  - CC-017: E2E test passes (AC-008)
  - CC-DOC-006: `documents/system-architecture.md` component map + data flow updated for adaptive tiering
  - CC-DOC-007: `documents/api-flows.md` reindex endpoint updated with re-chunk context
  - CC-DOC-008: `documents/database-schema.md` notes new `metadata_json` fields: `heading_path`, `adaptive_tier`, `content_type`

### Validation Strategy
- Unit tests: `AdaptiveChunker.should_inject()` (AC-001), heading path (AC-004), semantic fallback (AC-006), parent-child boundaries (AC-009)
- Integration tests: Full-doc upload path with Weaviate verification (AC-002, AC-005)
- E2E tests: Settings persistence (AC-003), re-chunk workflow (AC-008)
- Manual verification: Upload small doc → check chunk count (Scenario 1), upload large doc → check heading path (Scenario 2)
- Observability: `adaptive_tier` metadata in Weaviate lets us query how many full-doc chunks exist

### Traceability Matrix
- US-001 (small doc inject) → Phase 1
- US-002 (heading context) → Phase 2
- US-003 (config threshold) → Phase 1
- US-004 (re-chunk) → Phase 4
- REQ-001 (adaptive tiering) → Phase 1 (TASK-002)
- REQ-002 (configurability) → Phase 1 (TASK-001, TASK-005)
- REQ-003 (heading context) → Phase 2 (TASK-006)
- REQ-004 (full-doc indexing) → Phase 1 (TASK-003)
- REQ-005 (embedding semantic) → Phase 3 (TASK-008)
- REQ-006 (boundary parent-child) → Phase 3 (TASK-010)
- REQ-007 (manual re-chunk) → Phase 4 (TASK-012, TASK-013)
- AC-001 / AC-002 / AC-003 / AC-005 → Phase 1 tests
- AC-004 → Phase 2 tests
- AC-006 / AC-009 → Phase 3 tests
- AC-007 → All phases (backward compat guard)
- AC-008 → Phase 4 tests

### Rollout Plan
- Release approach: Feature-flagged via `adaptive_tiering_enabled` config (default: true)
- Feature flags: `config.ingestion.adaptive_tiering_enabled` — set to false to restore old behavior entirely
- Migration needs: None (new chunks only; existing untouched until manual re-chunk)
- Backward compatibility notes: Old `chunking_strategy` overrides adaptive tiering; new `ChunkData` fields are nullable

### Rollback Plan
- Disable: Set `adaptive_tiering_enabled: false` and re-deploy
- Full revert: Revert commit + re-index any documents that were re-chunked
- Data safety: Old chunks persist until re-chunk is triggered; re-chunk preserves old on failure

### Risks And Mitigations
- RISK-001 Embedding semantic slows ingestion / Mitigation: 5s timeout + Jaccard fallback; configurable via NFR
- RISK-002 Full-doc injection could overflow context / Mitigation: Threshold defaults to 30% of window; user-configurable
- RISK-003 Re-chunk failure loses data / Mitigation: Save + restore pattern; old chunks preserved until new ones succeed
- RISK-004 Settings UI fields confuse users / Mitigation: Tooltips explain threshold = ratio * context window; explicit threshold overrides

### Open Questions
- Q-001: Should re-chunk button appear on document list row or only detail view?
  - Next step: Both — icon on list row, button on detail. Deferred to implementation.
