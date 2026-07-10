## TASK-009
- Completed chunk_id injection into ContextService.assemble_context().
- Wrote and passed test backend/tests/chat/test_context_chunk_id_injection.py.
- Fixed existing test failures caused by old syntax in test_context_annotations.py.
- Fixed test_handles_uuid_labels in test_citations.py to use a valid UUID.

## TASK-010
- Added matched_chunk_id to ClaimItem schema.
- Verified pydantic model accepts fields correctly.

## TASK-011
- Updated CitationService.build_provenance to compute Jaccard match score per chunk and select the best match.
- Passed backend/tests/chat/test_provenance_match_metadata.py.

## TASK-012
- Added conflict_score field to CONFLICT_DETECTION_EVALUATION_PROMPT.

## TASK-013 & TASK-014
- Updated ConflictDetectionService to read conflict_score_threshold from config.
- Parsed conflict_score from LLM response.
- Derived has_conflict using threshold if score is present.
- Added and passed test_conflict_threshold.py.

