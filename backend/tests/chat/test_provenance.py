"""Tests for claim-level provenance graph (TASK-004)."""
from __future__ import annotations

import pytest
from chat.citations import CitationService, split_paragraphs


@pytest.fixture
def service():
    return CitationService()


@pytest.fixture
def chunks():
    return [
        {
            "chunk_id": "c1",
            "document_id": "d1",
            "title": "Doc One",
            "text": "Revenue grew 15% in Q3 2024. Operating margin expanded.",
        },
        {
            "chunk_id": "c2",
            "document_id": "d2",
            "title": "Doc Two",
            "text": "Costs decreased by 5% year over year.",
        },
    ]


class TestSplitParagraphs:
    def test_single_paragraph(self):
        text = "One paragraph only."
        blocks = split_paragraphs(text)
        assert len(blocks) == 1
        assert blocks[0]["text"] == "One paragraph only."
        assert blocks[0]["start"] == 0
        assert blocks[0]["end"] == len(text)

    def test_multiple_paragraphs(self):
        text = "First para.\n\nSecond para.\n\nThird para."
        blocks = split_paragraphs(text)
        assert len(blocks) == 3
        assert blocks[0]["text"] == "First para."
        assert blocks[1]["text"] == "Second para."
        assert blocks[2]["text"] == "Third para."

    def test_empty_text(self):
        assert split_paragraphs("") == []
        assert split_paragraphs(None) == []  # type: ignore[arg-type]

    def test_leading_trailing_whitespace(self):
        text = "\n\nFirst.\n\nSecond.\n\n"
        blocks = split_paragraphs(text)
        assert len(blocks) == 2
        assert blocks[0]["text"] == "First."
        assert blocks[1]["text"] == "Second."


class TestBuildProvenance:
    def test_fully_cited(self, service, chunks):
        answer = (
            "Revenue grew 15% in Q3 2024 [Source 1].\n\n"
            "Costs decreased by 5% [Source 2]."
        )
        result = service.build_provenance(answer, chunks)
        assert result["coverage"]["total"] == 2
        assert result["coverage"]["cited"] == 2
        assert result["coverage"]["uncited_indices"] == []
        assert all(c["cited"] for c in result["claims"])
        assert result["claims"][0]["chunks"] == ["c1"]
        assert result["claims"][1]["chunks"] == ["c2"]

    def test_partially_cited(self, service, chunks):
        answer = (
            "Revenue grew 15% in Q3 2024 [Source 1].\n\n"
            "This paragraph has no citation at all."
        )
        result = service.build_provenance(answer, chunks)
        assert result["coverage"]["total"] == 2
        assert result["coverage"]["cited"] == 1
        assert result["coverage"]["uncited_indices"] == [1]
        assert result["claims"][0]["cited"] is True
        assert result["claims"][1]["cited"] is False
        assert result["claims"][1]["labels"] == []
        assert result["claims"][1]["chunks"] == []

    def test_no_citations(self, service, chunks):
        answer = "All free text.\n\nStill free text."
        result = service.build_provenance(answer, chunks)
        assert result["coverage"]["total"] == 2
        assert result["coverage"]["cited"] == 0
        assert result["coverage"]["uncited_indices"] == [0, 1]

    def test_invalid_labels_dropped(self, service, chunks):
        answer = "Claim with bad label [Source 9]."
        result = service.build_provenance(answer, chunks)
        assert result["coverage"]["total"] == 1
        # Label extracted but not mapped → uncited
        assert result["claims"][0]["cited"] is False
        assert result["claims"][0]["labels"] == ["9"]
        assert result["claims"][0]["chunks"] == []

    def test_short_format_citations(self, service, chunks):
        answer = "Revenue grew 15% [1]."
        result = service.build_provenance(answer, chunks)
        assert result["claims"][0]["cited"] is True
        assert result["claims"][0]["chunks"] == ["c1"]

    def test_empty_answer(self, service, chunks):
        result = service.build_provenance("", chunks)
        assert result["coverage"]["total"] == 0
        assert result["claims"] == []
