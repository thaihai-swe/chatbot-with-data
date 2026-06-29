from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock
from chat.conflict import ConflictDetectionService
from providers.base import BaseLLMProvider

@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseLLMProvider)

@pytest.fixture
def service(mock_llm):
    return ConflictDetectionService(mock_llm)

class TestConflictDetectionService:
    def test_no_conflict_scenario(self, service, mock_llm):
        answer = "Revenue grew 15% in Q3."
        chunks = [{"title": "Doc A", "text": "Revenue grew 15% in Q3."}]
        
        mock_llm.generate_completion.return_value = json.dumps({
            "has_conflict": False,
            "surfaced_correctly": True,
            "conflict_details": ""
        })
        
        result = service.detect_conflict(answer, chunks)
        assert result["has_conflict"] is False
        assert result["surfaced_correctly"] is True
        assert result["conflict_details"] == ""

    def test_conflict_surfaced_correctly(self, service, mock_llm):
        answer = "Document A states revenue is $10M, while Document B states it is $12M."
        chunks = [
            {"title": "Doc A", "text": "revenue is $10M"},
            {"title": "Doc B", "text": "revenue is $12M"}
        ]
        
        mock_llm.generate_completion.return_value = json.dumps({
            "has_conflict": True,
            "surfaced_correctly": True,
            "conflict_details": "Doc A says $10M, Doc B says $12M"
        })
        
        result = service.detect_conflict(answer, chunks)
        assert result["has_conflict"] is True
        assert result["surfaced_correctly"] is True
        assert "Doc A says $10M" in result["conflict_details"]

    def test_conflict_unresolved(self, service, mock_llm):
        answer = "Revenue is $10M."
        chunks = [
            {"title": "Doc A", "text": "revenue is $10M"},
            {"title": "Doc B", "text": "revenue is $12M"}
        ]
        
        mock_llm.generate_completion.return_value = json.dumps({
            "has_conflict": True,
            "surfaced_correctly": False,
            "conflict_details": "Doc A says $10M, Doc B says $12M"
        })
        
        result = service.detect_conflict(answer, chunks)
        assert result["has_conflict"] is True
        assert result["surfaced_correctly"] is False
        assert result["conflict_details"] != ""


class TestChatServiceConflictIntegration:
    def test_chat_service_triggers_conflict_check_on_multiple_documents(self, monkeypatch):
        from chat.service import ChatService
        from models.chat import ChatTurn
        from schemas.chat import RetrievalTrace, SafetyTrace, SafetyGroundedness, SafetyAnswerability

        # 1. Mock ChatRepository static methods
        mock_session = MagicMock()
        mock_session.collection_id = None
        monkeypatch.setattr("chat.service.ChatRepository.get_session", MagicMock(return_value=mock_session))
        monkeypatch.setattr("chat.service.ChatRepository.list_turns_by_session", MagicMock(return_value=[]))
        
        mock_turn = ChatTurn(
            id="turn-123",
            session_id="session-123",
            query_text="Query text",
            answer_text="Answer asserting Claim A.",
            retrieved_chunks_json="[]",
            context_used_json=json.dumps({
                "conflict_status": "unresolved_conflict",
                "conflict_details": "Doc A vs Doc B"
            }),
            status="completed",
            safety_status="safe",
            safety_risk_score=0.0,
            safety_reason="",
            groundedness_score=1.0,
            created_at="2026-06-28",
            updated_at="2026-06-28"
        )
        monkeypatch.setattr("chat.service.ChatRepository.create_turn", MagicMock(return_value=mock_turn))
        monkeypatch.setattr("chat.service.ChatRepository.update_turn_status", MagicMock())
        monkeypatch.setattr("chat.service.ChatRepository.get_turn", MagicMock(return_value=mock_turn))
        monkeypatch.setattr("chat.service.ChatRepository.list_citations_by_turn", MagicMock(return_value=[]))

        # 2. Mock dependent services
        mock_retrieval = MagicMock()
        mock_chunks = [
            {"document_id": "doc-a", "title": "Doc A", "text": "Claim A"},
            {"document_id": "doc-b", "title": "Doc B", "text": "Claim B"}
        ]
        mock_trace = RetrievalTrace(
            original_query="Query text",
            classification=None,
            classification_confidence=None,
            transformations={"expanded_queries": [], "sub_questions": [], "synonym_expansions": {}},
            routing={"selected_strategy": "baseline", "reason": None, "fallback_triggered": False},
            retrieval_runs=[],
            merged_candidates_count=0,
            reranking=None,
            collection_routing=None,
            reasoning_chain=None,
            parent_child_expansions_count=0,
            execution_time_ms={}
        )
        mock_retrieval.retrieve.return_value = (mock_chunks, mock_trace)

        mock_context = MagicMock()
        mock_context.assemble_context.return_value = {"prompt": "Context prompt"}

        mock_generation = MagicMock()
        mock_generation.generate_answer.return_value = "Answer asserting Claim A."
        
        mock_citation = MagicMock()
        mock_citation.extract_citations.return_value = []
        mock_citation.map_citations_to_chunks.return_value = []

        mock_grounding = MagicMock()
        mock_grounding.evaluate_evidence.return_value = (True, "")
        mock_grounding.calculate_groundedness.return_value = (1.0, "Grounded")

        mock_safety = MagicMock()
        mock_safety.check_chunks = lambda x: x
        
        mock_safety_trace = SafetyTrace(
            query_classification=None,
            injection_risk="low",
            matched_patterns=[],
            classifier_reason=None,
            groundedness=SafetyGroundedness(score=1.0, status="supported"),
            answerability=SafetyAnswerability(is_answerable=True, refusal_reason=None)
        )
        mock_safety.check_query.return_value = mock_safety_trace

        mock_conflict = MagicMock()
        mock_conflict.detect_conflict.return_value = {
            "has_conflict": True,
            "surfaced_correctly": False,
            "conflict_details": "Doc A vs Doc B"
        }

        # 3. Instantiate ChatService
        chat_service = ChatService(
            advanced_retrieval_service=mock_retrieval,
            context_service=mock_context,
            generation_service=mock_generation,
            citation_service=mock_citation,
            grounding_service=mock_grounding,
            safety_service=mock_safety,
            conflict_service=mock_conflict
        )

        # 4. Process Turn
        response = chat_service.process_turn("session-123", "Query text")

        # 5. Verify conflict detection was called and mapped
        mock_conflict.detect_conflict.assert_called_once_with("Answer asserting Claim A.", mock_chunks)
        assert response.conflict_status == "unresolved_conflict"
        assert response.conflict_details == "Doc A vs Doc B"


