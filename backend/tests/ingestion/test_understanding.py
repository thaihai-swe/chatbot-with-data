"""Tests for DocumentUnderstandingService."""
from __future__ import annotations

import pytest
from indexing.understanding import DocumentUnderstandingService


class FakeLLM:
    def __init__(self, response: str = '{"summary": "Test summary.", "topics": ["topic1"], "sections": [{"heading": "Intro", "level": 1}]}'):
        self.response = response

    def generate_completion(self, messages, temperature=0.0):
        return self.response


class BrokenLLM:
    def generate_completion(self, messages, temperature=0.0):
        raise RuntimeError("LLM unavailable")


@pytest.fixture
def service():
    return DocumentUnderstandingService(llm_provider=FakeLLM())


class TestUnderstand:
    def test_returns_structured_dict(self, service):
        result = service.understand("Some document text.", title="Test Doc")
        assert isinstance(result, dict)
        assert "summary" in result
        assert "topics" in result
        assert "sections" in result

    def test_summary_is_string(self, service):
        result = service.understand("Text.", "Doc")
        assert isinstance(result["summary"], str)

    def test_topics_is_list(self, service):
        result = service.understand("Text.", "Doc")
        assert isinstance(result["topics"], list)

    def test_sections_is_list(self, service):
        result = service.understand("Text.", "Doc")
        assert isinstance(result["sections"], list)

    def test_handles_empty_text(self, service):
        result = service.understand("", "Empty Doc")
        assert result is not None

    def test_handles_none_title(self, service):
        result = service.understand("Some text.", title=None)
        assert result is not None

    def test_parses_json_with_markdown_fences(self, service):
        svc = DocumentUnderstandingService(llm_provider=FakeLLM(
            response='```json\n{"summary": "S", "topics": ["t"], "sections": []}\n```'
        ))
        result = svc.understand("Text.", "Doc")
        assert result["summary"] == "S"

    def test_llm_failure_returns_none(self):
        svc = DocumentUnderstandingService(llm_provider=BrokenLLM())
        result = svc.understand("Text.", "Doc")
        assert result is None

    def test_invalid_json_returns_none(self, service):
        svc = DocumentUnderstandingService(llm_provider=FakeLLM(response="not json"))
        result = svc.understand("Text.", "Doc")
        assert result is None

    def test_missing_fields_default_to_empty(self, service):
        svc = DocumentUnderstandingService(llm_provider=FakeLLM(response='{"summary": "S"}'))
        result = svc.understand("Text.", "Doc")
        assert result["summary"] == "S"
        assert result["topics"] == []
        assert result["sections"] == []

    def test_uses_title_in_prompt(self):
        captured = {}

        class CapturingLLM:
            def generate_completion(self, messages, temperature=0.0):
                captured["prompt"] = messages[0]["content"]
                return '{"summary": "S", "topics": [], "sections": []}'

        svc = DocumentUnderstandingService(llm_provider=CapturingLLM())
        svc.understand("body text", title="My Title")
        assert "My Title" in captured["prompt"]

    def test_defaults_title_to_untitled(self):
        captured = {}

        class CapturingLLM:
            def generate_completion(self, messages, temperature=0.0):
                captured["prompt"] = messages[0]["content"]
                return '{"summary": "S", "topics": [], "sections": []}'

        svc = DocumentUnderstandingService(llm_provider=CapturingLLM())
        svc.understand("body text", title=None)
        assert "Untitled" in captured["prompt"]
