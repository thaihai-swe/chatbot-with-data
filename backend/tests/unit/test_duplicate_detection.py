import tempfile
import unittest
from pathlib import Path

from backend.persistence.schema import init_schema
from backend.services.document_service import DocumentService
from backend.services.duplicate_detection_service import DuplicateDetectionService


class DuplicateDetectionTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.sqlite_path = Path(self.tempdir.name) / "app.sqlite3"
        init_schema(self.sqlite_path)
        self.document_service = DocumentService(str(self.sqlite_path))
        self.service = DuplicateDetectionService(str(self.sqlite_path))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_detects_exact_duplicate_by_file_hash(self):
        file_hash = self.service.compute_file_hash(b"same file")
        self.document_service.create_document(
            source_type="text",
            source_identity=file_hash,
            title="Doc One",
            raw_text="Alpha Beta",
            ingestion_status="completed",
            duplicate_status="unique",
            file_hash=file_hash,
            text_hash=self.service.compute_text_hash("Alpha Beta"),
        )

        result = self.service.detect(
            source_type="text",
            file_hash=file_hash,
            source_url=None,
            raw_text="Alpha Beta",
            title="Doc Two",
        )

        self.assertEqual(result["status"], "exact_duplicate")
        self.assertEqual(result["method"], "file_hash")
        self.assertEqual(result["similarity_score"], 1.0)

    def test_detects_same_url_after_canonicalization(self):
        self.document_service.create_document(
            source_type="url",
            source_url="https://example.com/docs/",
            source_identity=self.service.canonicalize_url("https://example.com/docs/"),
            title="Docs",
            raw_text="Original text",
            ingestion_status="completed",
            duplicate_status="unique",
            text_hash=self.service.compute_text_hash("Original text"),
        )

        result = self.service.detect(
            source_type="url",
            file_hash=None,
            source_url="http://example.com/docs?utm_source=test",
            raw_text="Changed text",
            title="Docs",
        )

        self.assertEqual(result["status"], "same_url")
        self.assertEqual(result["method"], "url_canonicalization")
        self.assertEqual(result["canonical_url"], "//example.com/docs")

    def test_detects_same_content_with_whitespace_and_case_changes(self):
        self.document_service.create_document(
            source_type="text",
            title="Doc One",
            raw_text="Alpha   Beta\nGamma",
            ingestion_status="completed",
            duplicate_status="unique",
            text_hash=self.service.compute_text_hash("Alpha   Beta\nGamma"),
        )

        result = self.service.detect(
            source_type="markdown",
            file_hash=None,
            source_url=None,
            raw_text="  alpha beta   gamma  ",
            title="Doc Two",
        )

        self.assertEqual(result["status"], "same_content_different_source")
        self.assertEqual(result["method"], "normalized_text_hash")
        self.assertEqual(result["similarity_score"], 1.0)

    def test_detects_near_duplicate_by_similarity(self):
        original_text = "This document explains alpha beta gamma delta epsilon for onboarding use"
        self.document_service.create_document(
            source_type="text",
            title="Doc One",
            raw_text=original_text,
            ingestion_status="completed",
            duplicate_status="unique",
            text_hash=self.service.compute_text_hash(original_text),
        )

        result = self.service.detect(
            source_type="text",
            file_hash=None,
            source_url=None,
            raw_text="This document explains alpha beta gamma delta epsilon for onboarding usage",
            title="Doc Variant",
        )

        self.assertEqual(result["status"], "near_duplicate")
        self.assertEqual(result["method"], "near_duplicate_overlap")
        self.assertGreaterEqual(result["similarity_score"], 0.92)

    def test_detects_same_title_when_content_differs(self):
        self.document_service.create_document(
            source_type="text",
            title="Release Notes",
            raw_text="Version one text",
            ingestion_status="completed",
            duplicate_status="unique",
            text_hash=self.service.compute_text_hash("Version one text"),
        )

        result = self.service.detect(
            source_type="text",
            file_hash=None,
            source_url=None,
            raw_text="Completely different payload for the next release",
            title="Release Notes",
        )

        self.assertEqual(result["status"], "same_title_different_content")
        self.assertEqual(result["method"], "title_metadata_match")


if __name__ == "__main__":
    unittest.main()
