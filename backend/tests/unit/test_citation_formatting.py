import unittest

from backend.services.citation_service import CitationFormattingService


class CitationFormattingUnitTests(unittest.TestCase):
    def setUp(self):
        self.service = CitationFormattingService()

    def test_maps_chunks_to_citation_objects_without_synthesizing_content(self):
        citations = self.service.format_citations(
            [
                {
                    "chunk_id": "chunk_1",
                    "document_id": "doc_1",
                    "document_title": "Guide",
                    "page_or_section": "page 2",
                    "source_url": "https://example.com",
                    "full_text": "Grounded chunk content.",
                    "retrieval_score": 0.87,
                    "retrieval_mode": "semantic",
                }
            ],
            citation_indices=[0],
            retrieval_mode="semantic",
        )
        self.assertEqual(len(citations), 1)
        citation = citations[0]
        self.assertEqual(citation["chunk_id"], "chunk_1")
        self.assertEqual(citation["document_id"], "doc_1")
        self.assertEqual(citation["content_snippet"], "Grounded chunk content.")
        self.assertEqual(citation["retrieval_mode"], "semantic")


if __name__ == "__main__":
    unittest.main()
