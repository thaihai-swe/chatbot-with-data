from __future__ import annotations

from typing import Any

from duplicate_detection.heuristics import classify_by_metadata
from models import DuplicateStatus
from repositories import Repository


class DuplicateDetector:
    def __init__(self) -> None:
        self.repository = Repository()

    def detect(
        self,
        candidate: dict[str, Any],
        *,
        ignore_document_id: str | None = None,
    ) -> dict[str, Any]:
        for existing in self.repository.list_all_documents_for_duplicate_detection():
            if ignore_document_id and existing["id"] == ignore_document_id:
                continue
            classification = classify_by_metadata(candidate, existing)
            if classification:
                status, evidence = classification
                return {
                    "classification": status,
                    "matched_document_id": existing["id"],
                    "detection_method": evidence["detection_method"],
                    "evidence": {
                        **evidence,
                        "matched_document_title": existing["title"],
                    },
                }
        return {
            "classification": DuplicateStatus.UNIQUE.value,
            "matched_document_id": None,
            "detection_method": "none",
            "evidence": {},
        }
