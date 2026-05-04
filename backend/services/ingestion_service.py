import json
from pathlib import Path

from werkzeug.utils import secure_filename

from backend.parsers.markdown_parser import parse_markdown_file
from backend.parsers.pdf_parser import parse_pdf_file
from backend.parsers.text_parser import parse_text_file
from backend.parsers.url_parser import parse_url
from backend.persistence.db import get_connection
from backend.services.chunking_service import ChunkingService
from backend.services.document_service import DocumentService
from backend.services.duplicate_detection_service import DuplicateDetectionService
from backend.services.indexing_service import IndexingService
from backend.utils import generate_id, json_dumps, utcnow_iso


class IngestionService:
    def __init__(
        self,
        sqlite_path,
        upload_dir,
        chroma_client,
        collection_prefix,
        embedding_model,
        embedding_dimensions,
        chunk_size,
        chunk_overlap,
        url_timeout_seconds,
    ):
        self.sqlite_path = sqlite_path
        self.upload_dir = Path(upload_dir)
        self.document_service = DocumentService(sqlite_path)
        self.duplicate_service = DuplicateDetectionService(sqlite_path)
        self.chunking_service = ChunkingService(chunk_size, chunk_overlap)
        self.indexing_service = IndexingService(
            chroma_client,
            collection_prefix=collection_prefix,
            embedding_model=embedding_model,
            dimensions=embedding_dimensions,
        )
        self.url_timeout_seconds = url_timeout_seconds

    def _create_attempt(self, document_id, source_type, source_identifier, status, duplicate_class=None, error_message=None, payload=None):
        attempt_id = generate_id("attempt")
        now = utcnow_iso()
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO ingestion_attempts (
                    attempt_id, document_id, source_type, source_identifier, status,
                    duplicate_class, error_message, user_decision, payload_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt_id,
                    document_id,
                    source_type,
                    source_identifier,
                    status,
                    duplicate_class,
                    error_message,
                    None,
                    json_dumps(payload or {}),
                    now,
                    now,
                ),
            )
        return attempt_id

    def _log_duplicate(self, attempt_id, detection):
        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO duplicate_logs (
                    attempt_id, matched_document_id, detection_method, duplicate_status,
                    similarity_score, decision, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt_id,
                    detection["matched_document_id"],
                    detection["method"],
                    detection["status"],
                    detection["similarity_score"],
                    None,
                    utcnow_iso(),
                ),
            )

    def _update_attempt(self, attempt_id, **fields):
        assignments = []
        values = []
        for key, value in fields.items():
            assignments.append(f"{key} = ?")
            values.append(value)
        assignments.append("updated_at = ?")
        values.append(utcnow_iso())
        values.append(attempt_id)

        with get_connection(self.sqlite_path) as connection:
            connection.execute(
                f"UPDATE ingestion_attempts SET {', '.join(assignments)} WHERE attempt_id = ?",
                values,
            )

    def _get_latest_attempt(self, document_id):
        with get_connection(self.sqlite_path) as connection:
            row = connection.execute(
                """
                SELECT * FROM ingestion_attempts
                WHERE document_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (document_id,),
            ).fetchone()
        return row

    def _parse_saved_file(self, path, source_type):
        if source_type == "pdf":
            return parse_pdf_file(path)
        if source_type == "markdown":
            return parse_markdown_file(path)
        return parse_text_file(path)

    def _finalize_document(self, document_id):
        document = self.document_service.get_document(document_id)
        chunks = self.chunking_service.create_chunks(document)
        self.document_service.replace_chunks(document_id, chunks)
        self.indexing_service.delete_document(document)
        self.indexing_service.index_chunks(document, chunks)
        return self.document_service.mark_last_indexed(document_id)

    def ingest_uploaded_file(self, file_storage, collection_id=None):
        filename = secure_filename(file_storage.filename or "upload")
        extension = Path(filename).suffix.lower()
        if extension == ".pdf":
            source_type = "pdf"
        elif extension in {".md", ".markdown"}:
            source_type = "markdown"
        elif extension == ".txt":
            source_type = "text"
        else:
            return {"status": "failed", "errors": ["Unsupported file type"]}

        stored_name = f"{generate_id('upload')}{extension}"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        stored_path = self.upload_dir / stored_name
        file_storage.save(stored_path)
        file_bytes = stored_path.read_bytes()

        parse_result = self._parse_saved_file(stored_path, source_type)
        raw_text = parse_result["text"]
        metadata = parse_result["metadata"]

        file_hash = self.duplicate_service.compute_file_hash(file_bytes)
        detection = self.duplicate_service.detect(
            source_type=source_type,
            file_hash=file_hash,
            source_url=None,
            raw_text=raw_text,
            title=metadata.get("title"),
        )

        document = self.document_service.create_document(
            source_type=source_type,
            collection_id=collection_id,
            source_path=str(stored_path),
            source_identity=file_hash,
            source_filename=filename,
            title=metadata.get("title"),
            raw_text=raw_text,
            ingestion_status="pending",
            duplicate_status=detection["status"],
            file_hash=file_hash,
            text_hash=detection["text_hash"],
            freshness_metadata=json_dumps(metadata),
        )

        payload = {
            "raw_text": raw_text,
            "metadata": metadata,
            "file_hash": file_hash,
            "text_hash": detection["text_hash"],
        }
        attempt_id = self._create_attempt(
            document["document_id"],
            source_type,
            str(stored_path),
            "pending",
            duplicate_class=detection["status"],
            payload=payload,
        )

        if detection["status"] != "unique":
            self.document_service.update_document(
                document["document_id"],
                ingestion_status="duplicate_detected",
            )
            self._update_attempt(attempt_id, status="duplicate_detected")
            self._log_duplicate(attempt_id, detection)
            updated = self.document_service.get_document(document["document_id"])
            return {
                "document_id": updated["document_id"],
                "status": updated["ingestion_status"],
                "duplicate_class": detection["status"],
                "matched_document_id": detection["matched_document_id"],
                "detection_method": detection["method"],
                "similarity_score": detection["similarity_score"],
            }

        finalized = self._finalize_document(document["document_id"])
        self.document_service.update_document(finalized["document_id"], ingestion_status="completed")
        self._update_attempt(attempt_id, status="completed")
        return {
            "document_id": finalized["document_id"],
            "status": "completed",
            "duplicate_class": detection["status"],
        }

    def ingest_url(self, url, collection_id=None):
        parse_result = parse_url(url, timeout_seconds=self.url_timeout_seconds)
        raw_text = parse_result["text"]
        metadata = parse_result["metadata"]
        canonical_url = self.duplicate_service.canonicalize_url(url)

        detection = self.duplicate_service.detect(
            source_type="url",
            file_hash=None,
            source_url=url,
            raw_text=raw_text,
            title=metadata.get("title"),
        )

        document = self.document_service.create_document(
            source_type="url",
            collection_id=collection_id,
            source_url=url,
            source_identity=canonical_url,
            title=metadata.get("title"),
            raw_text=raw_text,
            ingestion_status="pending",
            duplicate_status=detection["status"],
            text_hash=detection["text_hash"],
            freshness_metadata=json_dumps(metadata),
        )

        payload = {
            "raw_text": raw_text,
            "metadata": metadata,
            "text_hash": detection["text_hash"],
        }
        attempt_id = self._create_attempt(
            document["document_id"],
            "url",
            url,
            "pending",
            duplicate_class=detection["status"],
            payload=payload,
        )

        if detection["status"] != "unique":
            self.document_service.update_document(
                document["document_id"],
                ingestion_status="duplicate_detected",
            )
            self._update_attempt(attempt_id, status="duplicate_detected")
            self._log_duplicate(attempt_id, detection)
            updated = self.document_service.get_document(document["document_id"])
            return {
                "document_id": updated["document_id"],
                "status": updated["ingestion_status"],
                "duplicate_class": detection["status"],
                "matched_document_id": detection["matched_document_id"],
                "detection_method": detection["method"],
                "similarity_score": detection["similarity_score"],
            }

        finalized = self._finalize_document(document["document_id"])
        self.document_service.update_document(finalized["document_id"], ingestion_status="completed")
        self._update_attempt(attempt_id, status="completed")
        return {
            "document_id": finalized["document_id"],
            "status": "completed",
            "duplicate_class": detection["status"],
        }

    def apply_duplicate_decision(self, document_id, decision):
        document = self.document_service.get_document(document_id)
        if not document:
            return None, "Document not found"
        attempt = self._get_latest_attempt(document_id)
        if not attempt:
            return None, "Ingestion attempt not found"
        payload = json.loads(attempt["payload_json"] or "{}")

        if decision == "skip":
            self.document_service.update_document(
                document_id,
                ingestion_status="skipped",
                deletion_state="skipped",
            )
            self._update_attempt(attempt["attempt_id"], status="skipped", user_decision=decision)
            return self.document_service.get_document(document_id), None

        if decision == "replace":
            with get_connection(self.sqlite_path) as connection:
                duplicate_log = connection.execute(
                    """
                    SELECT matched_document_id
                    FROM duplicate_logs
                    WHERE attempt_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (attempt["attempt_id"],),
                ).fetchone()
            if not duplicate_log or not duplicate_log["matched_document_id"]:
                return None, "Matched document not found for replace decision"
            matched_id = duplicate_log["matched_document_id"]
            self.document_service.update_document(
                matched_id,
                raw_text=payload.get("raw_text"),
                title=(payload.get("metadata") or {}).get("title"),
                text_hash=payload.get("text_hash"),
            )
            self._finalize_document(matched_id)
            self.document_service.update_document(
                document_id,
                ingestion_status="skipped",
                deletion_state="replaced",
            )
            self._update_attempt(attempt["attempt_id"], status="completed", user_decision=decision)
            return self.document_service.get_document(matched_id), None

        if decision in {"version-as-new", "ingest-anyway"}:
            finalized = self._finalize_document(document_id)
            self.document_service.update_document(
                finalized["document_id"],
                ingestion_status="completed",
            )
            self._update_attempt(attempt["attempt_id"], status="completed", user_decision=decision)
            return self.document_service.get_document(document_id), None

        return None, "Unsupported duplicate decision"

    def reindex_document(self, document_id):
        document = self.document_service.get_document(document_id)
        if not document:
            return None, "Document not found"
        finalized = self._finalize_document(document_id)
        self.document_service.update_document(document_id, ingestion_status="completed")
        return finalized, None

    def delete_document(self, document_id):
        document = self.document_service.get_document(document_id)
        if not document:
            return False, "Document not found"
        self.indexing_service.delete_document(document)
        source_path = document.get("source_path")
        self.document_service.delete_document_record(document_id)
        if source_path and Path(source_path).exists():
            Path(source_path).unlink()
        return True, None

    def list_logs(self):
        with get_connection(self.sqlite_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    ia.attempt_id,
                    ia.document_id,
                    ia.source_type,
                    ia.source_identifier,
                    ia.status,
                    ia.duplicate_class,
                    ia.error_message,
                    ia.user_decision,
                    ia.created_at,
                    dl.matched_document_id,
                    dl.detection_method,
                    dl.similarity_score,
                    dl.decision
                FROM ingestion_attempts ia
                LEFT JOIN duplicate_logs dl ON dl.attempt_id = ia.attempt_id
                ORDER BY ia.created_at DESC
                """
            ).fetchall()
        return rows
