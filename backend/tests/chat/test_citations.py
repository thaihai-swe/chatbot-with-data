"""Tests for CitationService including quote extraction."""
from __future__ import annotations

import pytest
from chat.citations import CitationService


@pytest.fixture
def service():
    return CitationService()


class TestExtractCitations:
    def test_extracts_single_citation(self, service):
        text = "Revenue grew 15% in Q3 [Source 1]."
        assert service.extract_citations(text) == ["1"]

    def test_extracts_multiple_citations(self, service):
        text = "Revenue grew [Source 1]. Costs decreased [Source 2]."
        assert service.extract_citations(text) == ["1", "2"]

    def test_deduplicates_citations(self, service):
        text = "Revenue grew [Source 1]. It was strong [Source 1]."
        assert service.extract_citations(text) == ["1"]

    def test_handles_uuid_labels(self, service):
        text = "Revenue grew [Source abc-123]."
        assert service.extract_citations(text) == ["abc-123"]

    def test_no_citations(self, service):
        text = "Revenue grew."
        assert service.extract_citations(text) == []


class TestExtractQuote:
    def test_sentence_overlap_match(self, service):
        chunk_text = "Revenue grew 15% in Q3 2024. Costs decreased by 5%."
        answer_text = "The company reported strong growth. Revenue grew 15% in Q3 2024 [Source 1]."
        quote = service.extract_quote(chunk_text, answer_text, "1")
        assert quote == "Revenue grew 15% in Q3 2024."

    def test_prefers_best_sentence(self, service):
        chunk_text = "Costs decreased by 5%. Revenue grew 15% in Q3 2024. Operating margin expanded."
        answer_text = "Revenue grew 15% in Q3 2024 [Source 1]."
        quote = service.extract_quote(chunk_text, answer_text, "1")
        assert quote == "Revenue grew 15% in Q3 2024."

    def test_returns_empty_when_label_not_found(self, service):
        chunk_text = "Revenue grew 15%."
        answer_text = "Something else entirely."
        quote = service.extract_quote(chunk_text, answer_text, "1")
        assert quote == ""

    def test_below_threshold_returns_empty_without_llm(self, service):
        chunk_text = "The weather was sunny and warm."
        answer_text = "Revenue grew 15% in Q3 2024 [Source 1]."
        quote = service.extract_quote(chunk_text, answer_text, "1")
        assert quote == ""  # No overlap, no LLM provider

    def test_falls_back_to_llm_when_provided(self, service):
        chunk_text = "The financial results were positive."
        answer_text = "Revenue grew 15% in Q3 2024 [Source 1]."

        class FakeLLM:
            def generate_completion(self, messages, temperature=0.0):
                return "The financial results were positive."

        quote = service.extract_quote(chunk_text, answer_text, "1", llm_provider=FakeLLM())
        assert quote == "The financial results were positive."

    def test_llm_fallback_logs_and_returns_best_match(self, service):
        chunk_text = "The financial results were positive."
        answer_text = "Revenue grew 15% in Q3 2024 [Source 1]."

        class BrokenLLM:
            def generate_completion(self, messages, temperature=0.0):
                raise RuntimeError("LLM down")

        quote = service.extract_quote(chunk_text, answer_text, "1", llm_provider=BrokenLLM())
        assert quote == ""  # No overlap, LLM failed


class TestMapCitationsToChunks:
    def test_includes_quote_text_when_answer_provided(self, service):
        chunks = [
            {"chunk_id": "c1", "document_id": "d1", "text": "Revenue grew 15% in Q3 2024.", "title": "Report"},
        ]
        answer = "Revenue grew 15% in Q3 2024 [Source 1]."
        citations = service.map_citations_to_chunks(["1"], chunks, answer_text=answer)
        assert len(citations) == 1
        assert citations[0]["quote_text"] == "Revenue grew 15% in Q3 2024."

    def test_skips_quote_text_when_no_answer(self, service):
        chunks = [
            {"chunk_id": "c1", "document_id": "d1", "text": "Revenue grew 15%.", "title": "Report"},
        ]
        citations = service.map_citations_to_chunks(["1"], chunks)
        assert len(citations) == 1
        assert "quote_text" not in citations[0]

    def test_maps_by_index(self, service):
        chunks = [
            {"chunk_id": "c1", "document_id": "d1", "text": "First chunk.", "title": "Doc 1"},
            {"chunk_id": "c2", "document_id": "d2", "text": "Second chunk.", "title": "Doc 2"},
        ]
        citations = service.map_citations_to_chunks(["2"], chunks)
        assert len(citations) == 1
        assert citations[0]["chunk_id"] == "c2"

    def test_maps_by_uuid(self, service):
        chunks = [
            {"chunk_id": "abc-123", "document_id": "d1", "text": "Content.", "title": "Doc"},
        ]
        citations = service.map_citations_to_chunks(["abc-123"], chunks)
        assert len(citations) == 1
        assert citations[0]["chunk_id"] == "abc-123"

    def test_skips_invalid_labels(self, service):
        chunks = [
            {"chunk_id": "c1", "document_id": "d1", "text": "Content.", "title": "Doc"},
        ]
        citations = service.map_citations_to_chunks(["99"], chunks)
        assert len(citations) == 0


class TestFormatCitation:
    def test_includes_all_fields(self, service):
        chunk = {
            "chunk_id": "c1",
            "document_id": "d1",
            "title": "Report",
            "page_number": 5,
            "section_title": "Revenue",
            "source_url": "http://example.com",
        }
        result = service._format_citation(chunk)
        assert result["chunk_id"] == "c1"
        assert result["document_id"] == "d1"
        assert result["title"] == "Report"
        assert result["page_number"] == 5
        assert result["section_title"] == "Revenue"
        assert result["source_url"] == "http://example.com"
