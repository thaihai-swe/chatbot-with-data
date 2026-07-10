# Proposal: RAG Accuracy Fixes

## In Scope
Five surgical patches to improve accuracy and verifiability of document-based chat answers:

| # | Area | File(s) | Change |
|---|------|---------|--------|
| 1 | Similarity config | `config.py`, `grounding.py` | Per-collection `min_similarity_threshold` |
| 2 | Grounding | `grounding.py` | Jaccard pre-filter → LLM judge on top-k |
| 3 | Citation schema | `citations.py`, prompts | Enforce `[Source <chunk_id>]` format |
| 4 | Provenance schema | `citations.py` | Add `match_score`, `match_method` to ClaimNode |
| 5 | Conflict threshold | `conflict.py` | Return numeric `conflict_score`; threshold at 0.8 |

## Out of Scope
- New retrieval strategies or chunking methods
- Front-end UI changes
- Database schema migrations
- New API endpoints
- Evaluation framework changes

## Non-Goals
- Replacing LLM provider abstraction
- Multi-turn conversation context compression
- Cost tracking / budgeting

## Rationale
Current chat answers are sometimes:
- Refused when valid evidence exists (similarity threshold too high)
- Generated without adequate evidence (similarity threshold too low)
- Cited with fuzzy `[Source N]` that can't be traced to specific chunks
- Missing provenance detail to verify grounding
- Conflict detection is binary (`has_conflict`/`surfaced_correctly`) without score

These patches directly improve factual correctness, traceability, and user trust.

## Dependencies
- Existing config system (`config.py` / `settings.py`)
- Current `GroundingService`, `CitationService`, `ConflictDetectionService`
- `ChunkRepository` for chunk ID lookups

## Acceptance Criteria (Preview)
Each patch will have a testable AC in the full spec. Example:
- **AC-01**: Collection-level `min_similarity` overrides global default.
- **AC-02**: Groundedness score returns ≥0.8 when answer is fully supported.
- **AC-03**: Citations regex only matches `[Source <uuid>]`.
- **AC-04**: Provenance `claims[*].match_score` ∈ [0,1] present.
- **AC-05**: `conflict_score` returned; `has_conflict` true iff score ≥ 0.8.