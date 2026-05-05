from __future__ import annotations

from typing import Any

from models import DuplicateStatus


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = set(token for token in left.lower().split() if token)
    right_tokens = set(token for token in right.lower().split() if token)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return intersection / union


def classify_by_metadata(candidate: dict[str, Any], existing: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    if candidate.get("file_hash") and candidate["file_hash"] == existing.get("file_hash"):
        return (
            DuplicateStatus.EXACT_DUPLICATE.value,
            {"detection_method": "file_hash", "similarity_score": 1.0},
        )
    if (
        candidate.get("canonical_source_uri")
        and candidate["canonical_source_uri"] == existing.get("canonical_source_uri")
    ):
        return (
            DuplicateStatus.SAME_URL.value,
            {"detection_method": "canonical_url", "similarity_score": 1.0},
        )
    if (
        candidate.get("normalized_text_hash")
        and candidate["normalized_text_hash"] == existing.get("normalized_text_hash")
    ):
        classification = (
            DuplicateStatus.SAME_CONTENT_DIFFERENT_SOURCE.value
            if candidate.get("source_uri") != existing.get("source_uri")
            or candidate.get("source_type") != existing.get("source_type")
            else DuplicateStatus.NEAR_DUPLICATE.value
        )
        return (
            classification,
            {"detection_method": "normalized_text_hash", "similarity_score": 1.0},
        )
    if candidate["title"].strip().lower() == existing["title"].strip().lower():
        return (
            DuplicateStatus.SAME_TITLE_DIFFERENT_CONTENT.value,
            {"detection_method": "title_match", "similarity_score": 0.5},
        )
    similarity = jaccard_similarity(
        candidate.get("extracted_text") or "",
        existing.get("extracted_text") or "",
    )
    if similarity >= 0.75:
        return (
            DuplicateStatus.NEAR_DUPLICATE.value,
            {"detection_method": "text_overlap", "similarity_score": similarity},
        )
    return None
