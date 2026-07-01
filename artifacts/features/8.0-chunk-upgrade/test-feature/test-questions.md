# Test Questions for Chunk Upgrade Feature

## Adaptive Tiering (Tier 1 — Full-Doc Injection)

Upload: `small-faq.md` (under adaptive threshold)

Questions to verify single-chunk indexing:
1. "What is Retrieval-Augmented Generation?"
   - Expected: Single answer citing the full FAQ doc
   - Verify: Only 1 chunk exists for this document in the DB
   - Verify: Chunk metadata shows `adaptive_tier="full_doc"`

2. "What chunking strategies are available?"
   - Expected: Lists all 6 strategies including adaptive tiering

## Heading-Aware with Path Preservation (Tier 2)

Upload: `large-manual.md` (over adaptive threshold)

Questions to verify heading paths in chunks:
3. "What are the four stages of the data processing pipeline?"
   - Expected: Answer citing chunks that include `[Introduction]` or `[Technical Reference Manual]` heading path

4. "How does PDF extraction work?"
   - Expected: Answer from the `[Extraction Stage > PDF Extraction]` section
   - Verify: The chunk text starts with `[Extraction Stage > PDF Extraction]`

5. "What is the adaptive tiering ratio default value?"
   - Expected: Answer from `[Chunking Stage > Adaptive Tiering]` or `[Configuration > Key Parameters]`
   - Verify: Heading paths are present in retrieved chunks

## Semantic Chunking (Embedding Boundaries)

Upload: `topic-shifts.txt` (multi-topic document)

Questions to verify topic-aware boundaries:
6. "How is machine learning used in climate research?"
   - Expected: Focused answer from the ML + climate paragraph (paragraph 2)
   - Verify: Chunk boundaries align with topic shifts, not arbitrary splits

7. "Describe the history of computing generations."
   - Expected: Answer from the computing history paragraph (paragraph 3)
   - Should NOT include climate or ML content (demonstrates clean topic boundaries)

8. "What international agreements address climate change?"
   - Expected: Answer from the international agreements paragraph (paragraph 6)
   - Should combine with climate content but NOT computing history content

## Boundary-Aware Parent-Child

Upload: `structured-report.md` (multi-section document)

Questions to verify parent grouping:
9. "What are the key findings of the technology assessment?"
   - Expected: Answer from Executive Summary sections or Knowledge Management sections
   - Verify: Parent chunks align with section boundaries, not arbitrary N-chunk groups

10. "What security measures are in place?"
    - Expected: Answer from Security Assessment section
    - Verify: Parent chunk contains only Security Assessment content, not mixed with other sections

## Re-chunk Button

11. "How do I re-chunk an existing document?"
    - Steps: Open any document → Click "Re-chunk" → Verify new chunk count
    - Verify: Chunks are replaced atomically (count changes, IDs change)

## Cross-Document Search (Full-Doc Injection + Weaviate)

12. "What embedding model is used by default?"
    - Expected: Should find answer across documents (mentioned in both large-manual.md and structured-report.md)
    - Verify: Full-doc injection chunks are indexed and searchable in Weaviate

## Configuration Change

13. What happens if I set the adaptive_tiering_threshold explicitly?
    - Steps: Set `adaptive_tiering_threshold: 500` → Upload small-faq.md (should now be chunked instead of injected)
    - Verify: Document produces multiple chunks instead of 1

## Verification Checklist

- [ ] Small FAQ stored as single chunk (`adaptive_tier="full_doc"`)
- [ ] Large manual chunks have `[Parent > Child]` heading paths prepended
- [ ] Topic-shifts document chunks align with semantic boundaries
- [ ] Structured report parent chunks align with sections
- [ ] Re-chunk button atomically replaces old chunks with new ones
- [ ] Full-doc injection chunks are searchable via Weaviate
- [ ] Changing adaptive threshold affects chunk count on next upload
