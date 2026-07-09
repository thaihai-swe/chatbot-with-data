from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock, patch
from chat.knowledge_products import KnowledgeProductService
from providers.base import BaseLLMProvider
from repositories.collection_repository import CollectionRepository

@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseLLMProvider)

@pytest.fixture
def mock_repo():
    return MagicMock(spec=CollectionRepository)

@pytest.fixture
def service(mock_llm, mock_repo):
    return KnowledgeProductService(llm_provider=mock_llm, collection_repository=mock_repo)

class TestKnowledgeProductService:
    def test_generate_study_guide_with_doc_understanding(self, service, mock_llm, mock_repo):
        doc = {
            "id": "doc-1",
            "title": "Doc 1",
            "metadata": {
                "doc_understanding": {
                    "summary": "This is a summary of doc 1.",
                    "topics": ["topic A", "topic B"]
                }
            }
        }
        mock_repo.get_collection_members.return_value = [doc]
        mock_llm.generate_completion.return_value = "# Synthesized Study Guide"

        result = service.generate_study_guide("col-123")
        assert result == "# Synthesized Study Guide"
        
        mock_llm.generate_completion.assert_called_once()
        prompt_content = mock_llm.generate_completion.call_args[0][0][0]["content"]
        assert "This is a summary of doc 1." in prompt_content
        assert "topic A, topic B" in prompt_content

    @patch("chat.knowledge_products.get_connection")
    def test_generate_study_guide_with_fallback_summary(self, mock_db, service, mock_llm, mock_repo):
        doc = {
            "id": "doc-2",
            "title": "Old Doc",
            "metadata": {}
        }
        mock_repo.get_collection_members.return_value = [doc]
        
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [("Chunk text 1",), ("Chunk text 2",)]
        mock_db.return_value.__enter__.return_value = mock_conn

        mock_llm.generate_completion.side_effect = ["Fallback summary.", "# Synthesized Guide with fallback"]

        result = service.generate_study_guide("col-123")
        assert result == "# Synthesized Guide with fallback"

        assert mock_llm.generate_completion.call_count == 2
        call0 = mock_llm.generate_completion.call_args_list[0]
        args, kwargs = call0[0], call0[1]
        messages = kwargs.get("messages", args[0] if args else [])
        fallback_prompt = messages[0]["content"]
        assert "Chunk text 1" in fallback_prompt
        assert "Old Doc" in fallback_prompt

    def test_generate_flashcards(self, service, mock_llm, mock_repo):
        doc = {
            "id": "doc-1",
            "title": "Doc 1",
            "metadata": {
                "doc_understanding": {
                    "summary": "This is a summary.",
                    "topics": []
                }
            }
        }
        mock_repo.get_collection_members.return_value = [doc]
        mock_llm.generate_completion.return_value = json.dumps([
            {"question": "Q1", "answer": "A1"},
            {"question": "Q2", "answer": "A2"}
        ])

        result = service.generate_flashcards("col-123")
        assert len(result) == 2
        assert result[0] == {"question": "Q1", "answer": "A1"}


def test_generate_endpoints_http():
    from fastapi.testclient import TestClient
    from main import app
    from providers.factory import get_llm_provider

    mock_prov = MagicMock()
    mock_prov.generate_completion.return_value = "Mock Markdown product"

    app.dependency_overrides[get_llm_provider] = lambda: mock_prov

    client = TestClient(app)
    try:
        with patch("chat.knowledge_products.CollectionRepository.get_collection_members") as mock_get_members:
            mock_get_members.return_value = [{
                "id": "doc-1",
                "title": "Doc 1",
                "metadata": {
                    "doc_understanding": {
                        "summary": "Doc summary",
                        "topics": []
                    }
                }
            }]
            
            resp = client.post("/collections/col-123/generate/study-guide")
            assert resp.status_code == 200
            assert resp.json()["content"] == "Mock Markdown product"

            mock_prov.generate_completion.return_value = '[{"question": "Q?", "answer": "A."}]'
            resp = client.post("/collections/col-123/generate/flashcards")
            assert resp.status_code == 200
            assert resp.json() == [{"question": "Q?", "answer": "A."}]

            # Test document_id query param
            resp = client.post("/collections/col-123/generate/study-guide?document_id=doc-1")
            assert resp.status_code == 200
            
            # Test non-existent document
            resp = client.post("/collections/col-123/generate/study-guide?document_id=doc-999")
            assert resp.status_code == 404
            assert "not found in collection" in resp.json()["detail"]
    finally:
        app.dependency_overrides.clear()

