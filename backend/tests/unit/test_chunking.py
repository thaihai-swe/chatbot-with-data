import unittest

from backend.services.chunking_service import ChunkingService


class ChunkingTests(unittest.TestCase):
    def test_fixed_size_chunking_respects_overlap(self):
        service = ChunkingService(chunk_size=10, chunk_overlap=2)
        document = {
            "document_id": "doc_1",
            "collection_id": "col_1",
            "source_type": "text",
            "title": "Plain",
            "source_url": None,
            "raw_text": "abcdefghijKLMNOPQRstuvwxyz",
        }

        chunks = service.create_chunks(document)

        self.assertEqual([chunk["chunk_order"] for chunk in chunks], [1, 2, 3])
        self.assertEqual(chunks[0]["chunk_text"], "abcdefghij")
        self.assertEqual(chunks[1]["chunk_text"], "ijKLMNOPQR")
        self.assertEqual(chunks[2]["chunk_text"], "QRstuvwxyz")

    def test_markdown_chunking_preserves_heading_context(self):
        service = ChunkingService(chunk_size=80, chunk_overlap=10)
        document = {
            "document_id": "doc_2",
            "collection_id": "col_1",
            "source_type": "markdown",
            "title": "Guide",
            "source_url": None,
            "raw_text": "# Intro\nAlpha body\n## Deep Dive\nBeta body",
        }

        chunks = service.create_chunks(document)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["section_name"], "Intro")
        self.assertIn("Alpha body", chunks[0]["chunk_text"])
        self.assertEqual(chunks[1]["section_name"], "Deep Dive")
        self.assertIn("Beta body", chunks[1]["chunk_text"])

    def test_pdf_chunking_uses_page_boundaries(self):
        service = ChunkingService(chunk_size=20, chunk_overlap=4)
        document = {
            "document_id": "doc_3",
            "collection_id": "col_2",
            "source_type": "pdf",
            "title": "Pages",
            "source_url": None,
            "raw_text": "Page one text\nPage two text",
            "freshness_metadata": '{"page_texts": ["Page one text", "Page two text"]}',
        }

        chunks = service.create_chunks(document)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["page_number"], 1)
        self.assertEqual(chunks[1]["page_number"], 2)
        self.assertEqual(chunks[0]["chunk_order"], 1)
        self.assertEqual(chunks[1]["chunk_order"], 2)

    def test_empty_text_yields_no_chunks(self):
        service = ChunkingService(chunk_size=20, chunk_overlap=4)
        document = {
            "document_id": "doc_4",
            "collection_id": None,
            "source_type": "text",
            "title": "Empty",
            "source_url": None,
            "raw_text": "   ",
        }

        self.assertEqual(service.create_chunks(document), [])


if __name__ == "__main__":
    unittest.main()
