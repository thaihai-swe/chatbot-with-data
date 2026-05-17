import pytest
from unittest.mock import MagicMock, patch
from ingestion.service import IngestionService
from models import IngestionStatus, SourceType

def test_ingestion_service_passes_filename_to_dispatcher():
    # Setup
    service = IngestionService()
    service.repository = MagicMock()
    service.dispatcher = MagicMock()
    service.detector = MagicMock()
    
    attempt_id = "test-attempt"
    mock_attempt = {
        "id": attempt_id,
        "source_type": SourceType.TEXT.value,
        "artifact_path": "/tmp/uuid.txt",
        "source_uri": None,
        "submitted_filename": "Real Name.txt",
        "document_id": None,
        "collection_ids": [],
        "metadata_json": "{}",
        "status": IngestionStatus.SUBMITTED.value
    }
    
    service.repository.get_ingestion_attempt.return_value = mock_attempt
    service.dispatcher.extract.return_value = {
        "title": "Real Name",
        "extracted_text": "content",
        "metadata": {},
        "source_uri": None,
        "canonical_source_uri": None,
        "snapshot_path": None,
        "file_hash": "hash",
        "normalized_text_hash": "norm-hash",
        "mime_type": "text/plain"
    }
    service.detector.detect.return_value = {
        "classification": "unique",
        "matched_document_id": None,
        "evidence": {},
        "detection_method": "none"
    }
    
    # Execute
    service.process_ingestion_attempt(attempt_id)
    
    # Verify: fallback_title was passed correctly
    service.dispatcher.extract.assert_called_once_with(
        source_type=SourceType.TEXT.value,
        artifact_path="/tmp/uuid.txt",
        source_uri=None,
        fallback_title="Real Name.txt"
    )
    
    # Verify: title was updated in repository
    # First call is status=PROCESSING, second is update with extraction data
    # Let's check the second update call (or any call that sets title)
    update_calls = service.repository.update_ingestion_attempt.call_args_list
    title_updated = any(call.kwargs.get("title") == "Real Name" for call in update_calls)
    assert title_updated
