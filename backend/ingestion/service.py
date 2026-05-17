from __future__ import annotations

import json

from fastapi import UploadFile

from duplicate_detection import DuplicateDetector
from extractors import ExtractorDispatcher
from models import DuplicateAction, DuplicateStatus, IngestionStatus, SourceType
from repositories import Repository
from storage import LocalStorage
from chunking.service import get_chunking_service
from indexing.indexing_service import get_indexing_service
from config import get_settings, get_config, get_settings_manager


class IngestionService:
    def __init__(self) -> None:
        self.repository = Repository()
        self.storage = LocalStorage()
        self.dispatcher = ExtractorDispatcher()
        self.detector = DuplicateDetector()
        self.chunking_service = get_chunking_service()
        self.indexing_service = get_indexing_service()

    async def submit_file_upload(
        self, *, file: UploadFile, collection_ids: list[str]
    ) -> dict:
        artifact_path, _ = await self.storage.save_upload(file)
        source_type = PathClassifier.classify_from_filename(file.filename or "")
        return self.repository.create_ingestion_attempt(
            source_type=source_type,
            status=IngestionStatus.SUBMITTED.value,
            submitted_filename=file.filename,
            mime_type=file.content_type,
            artifact_path=artifact_path,
            collection_ids=collection_ids,
        )

    def submit_url(self, url: str, collection_ids: list[str]) -> dict:
        return self.repository.create_ingestion_attempt(
            source_type=SourceType.URL.value,
            status=IngestionStatus.SUBMITTED.value,
            source_uri=url,
            collection_ids=collection_ids,
        )

    def process_ingestion_attempt(self, attempt_id: str) -> None:
        attempt = self.repository.get_ingestion_attempt(attempt_id)
        if not attempt:
            raise KeyError(f"Ingestion attempt {attempt_id} not found")
        try:
            # Capture run snapshot
            get_settings_manager().save_run_snapshot(attempt_id, domain="ingestion")

            self.repository.update_ingestion_attempt(
                attempt_id,
                status=IngestionStatus.PROCESSING.value,
            )
            extraction = self.dispatcher.extract(
                source_type=attempt["source_type"],
                artifact_path=attempt["artifact_path"],
                source_uri=attempt["source_uri"],
                fallback_title=attempt.get("submitted_filename"),
            )
            candidate = {
                **extraction,
                "source_type": attempt["source_type"],
            }
            duplicate_result = self.detector.detect(
                candidate,
                ignore_document_id=attempt["document_id"],
            )
            attempt = self.repository.update_ingestion_attempt(
                attempt_id,
                title=extraction["title"],
                extracted_text=extraction["extracted_text"],
                metadata=extraction["metadata"],
                source_uri=extraction["source_uri"] or attempt["source_uri"],
                canonical_source_uri=extraction["canonical_source_uri"],
                snapshot_path=extraction["snapshot_path"],
                file_hash=extraction["file_hash"],
                normalized_text_hash=extraction["normalized_text_hash"],
                duplicate_status=duplicate_result["classification"],
                duplicate_match_document_id=duplicate_result["matched_document_id"],
                duplicate_evidence=duplicate_result["evidence"]
                | {"detection_method": duplicate_result["detection_method"]},
            )
            if duplicate_result["classification"] != DuplicateStatus.UNIQUE.value:
                self.repository.update_ingestion_attempt(
                    attempt_id,
                    status=IngestionStatus.AWAITING_USER_ACTION.value,
                )
                return
            document_id = self._finalize_successful_ingestion(
                attempt_id,
                action=DuplicateAction.INGEST_ANYWAY.value,
            )

            # Start chunking and indexing
            self._chunk_and_index_document(document_id, attempt)

            self.repository.update_ingestion_attempt(
                attempt_id,
                document_id=document_id,
                status=IngestionStatus.COMPLETED.value,
                completed=True,
            )
        except Exception as exc:
            self.repository.update_ingestion_attempt(
                attempt_id,
                status=IngestionStatus.FAILED.value,
                error_message=str(exc),
                completed=True,
            )

    def apply_duplicate_decision(self, attempt_id: str, action: str) -> dict:
        attempt = self.repository.get_ingestion_attempt(attempt_id)
        if not attempt:
            raise KeyError(f"Ingestion attempt {attempt_id} not found")
        evidence = (
            json.loads(attempt["duplicate_evidence_json"])
            if attempt["duplicate_evidence_json"]
            else {}
        )
        if attempt["status"] != IngestionStatus.AWAITING_USER_ACTION.value:
            raise ValueError("Duplicate decision is not available for this attempt")

        final_status = (
            IngestionStatus.SKIPPED.value
            if action == DuplicateAction.SKIP_INGESTION.value
            else IngestionStatus.COMPLETED.value
        )
        document_id = None
        if final_status == IngestionStatus.COMPLETED.value:
            document_id = self._finalize_successful_ingestion(attempt_id, action=action)
        updated_attempt = self.repository.update_ingestion_attempt(
            attempt_id,
            document_id=document_id,
            status=final_status,
            completed=True,
        )

        # Start chunking and indexing if completed
        if final_status == IngestionStatus.COMPLETED.value and document_id:
            self._chunk_and_index_document(document_id, attempt)

        decision = self.repository.create_duplicate_decision(
            ingestion_attempt_id=attempt_id,
            document_id=document_id,
            matched_document_id=attempt["duplicate_match_document_id"],
            classification=attempt["duplicate_status"] or DuplicateStatus.UNIQUE.value,
            detection_method=evidence.get("detection_method", "pending"),
            evidence=evidence,
            action=action,
            final_status=final_status,
        )
        return {"decision": decision, "attempt": updated_attempt}

    def _finalize_successful_ingestion(self, attempt_id: str, *, action: str) -> str:
        attempt = self.repository.get_ingestion_attempt(attempt_id)
        if not attempt:
            raise KeyError(f"Ingestion attempt {attempt_id} not found")
        metadata = json.loads(attempt["metadata_json"])
        collection_ids = attempt["collection_ids"]
        matched_document_id = attempt["duplicate_match_document_id"]
        if action in {
            DuplicateAction.REPLACE_EXISTING.value,
            DuplicateAction.MERGE_METADATA.value,
        }:
            if not matched_document_id:
                raise ValueError("Matched document is required for this duplicate action")
            current = self.repository.get_document(matched_document_id)
            if not current:
                raise KeyError(f"Matched document {matched_document_id} not found")
            merged_metadata = {
                **current["metadata"],
                **metadata,
            }
            updated = self.repository.update_document(
                matched_document_id,
                title=attempt["title"] or current["title"],
                source_uri=attempt["source_uri"] or current["source_uri"],
                canonical_source_uri=attempt["canonical_source_uri"]
                or current["canonical_source_uri"],
                filename=attempt["submitted_filename"] or current["filename"],
                mime_type=attempt["mime_type"] or current["mime_type"],
                file_hash=attempt["file_hash"] or current["file_hash"],
                normalized_text_hash=attempt["normalized_text_hash"]
                or current["normalized_text_hash"],
                extracted_text=attempt["extracted_text"] or current["extracted_text"],
                metadata=merged_metadata,
            )
            union_collection_ids = sorted(
                set(collection_ids) | {item["id"] for item in current["collections"]}
            )
            self.repository.assign_document_to_collections(
                matched_document_id,
                union_collection_ids,
            )
            self.repository.update_ingestion_attempt(
                attempt_id,
                document_id=matched_document_id,
            )
            return updated["id"]
        if action == DuplicateAction.INGEST_AS_NEW_VERSION.value:
            version_of_document_id = matched_document_id
        else:
            version_of_document_id = None
        if attempt["document_id"]:
            updated = self.repository.update_document(
                attempt["document_id"],
                title=attempt["title"] or "Untitled",
                source_uri=attempt["source_uri"],
                canonical_source_uri=attempt["canonical_source_uri"],
                filename=attempt["submitted_filename"],
                mime_type=attempt["mime_type"],
                file_hash=attempt["file_hash"],
                normalized_text_hash=attempt["normalized_text_hash"],
                extracted_text=attempt["extracted_text"] or "",
                metadata=metadata,
            )
            self.repository.assign_document_to_collections(updated["id"], collection_ids)
            return updated["id"]
        created = self.repository.create_document(
            title=attempt["title"] or "Untitled",
            source_type=attempt["source_type"],
            source_uri=attempt["source_uri"],
            canonical_source_uri=attempt["canonical_source_uri"],
            filename=attempt["submitted_filename"],
            mime_type=attempt["mime_type"],
            file_hash=attempt["file_hash"],
            normalized_text_hash=attempt["normalized_text_hash"],
            extracted_text=attempt["extracted_text"] or "",
            metadata=metadata,
            collection_ids=collection_ids,
            version_of_document_id=version_of_document_id,
        )
        self.repository.update_ingestion_attempt(
            attempt_id,
            document_id=created["id"],
        )
        return created["id"]

    def _chunk_and_index_document(self, document_id: str, attempt: dict) -> None:
        """Trigger chunking and indexing for a document."""
        # Get extracted text
        # Note: we use attempt instead of re-fetching document for performance if available
        text = attempt.get("extracted_text")
        if not text:
            doc = self.repository.get_document(document_id)
            text = doc["extracted_text"]

        if not text:
            return

        # Determine strategy from config or source_type
        config = get_config()
        strategy = config.ingestion.chunking_strategy
        
        # Override strategy based on source type if it's "fixed" (default)
        if strategy == "fixed":
            if attempt["source_type"] == SourceType.PDF.value:
                strategy = "page_aware"
            elif attempt["source_type"] == SourceType.MARKDOWN.value:
                strategy = "heading_aware"

        # Step 1: Chunking
        collection_ids = attempt["collection_ids"]

        if not collection_ids:
            collection_ids = ["default"]

        for collection_id in collection_ids:
            self.chunking_service.chunk_document(
                document_id=document_id,
                collection_id=collection_id,
                text=text,
                strategy=strategy,
                source_type=attempt["source_type"],
                title=attempt.get("title") or attempt.get("submitted_filename"),
                chunk_size=config.ingestion.chunk_size,
                overlap=config.ingestion.chunk_overlap,
            )

            # Step 2: Indexing
            self.indexing_service.index_document(
                document_id=document_id,
                collection_id=collection_id,
                embedding_model=config.ingestion.embedding_model,
                strategy=strategy,
            )



class PathClassifier:
    @staticmethod
    def classify_from_filename(filename: str) -> str:
        lowered = filename.lower()
        if lowered.endswith(".pdf"):
            return SourceType.PDF.value
        if lowered.endswith(".md") or lowered.endswith(".markdown"):
            return SourceType.MARKDOWN.value
        return SourceType.TEXT.value
