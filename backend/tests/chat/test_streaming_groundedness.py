"""Tests for streaming groundedness calculation and persistence parity with service.py."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from chat.streaming import StreamingOrchestrator
from models.chat import ChatTurn, ChatSession, Citation
from schemas.chat import (
    RetrievalTrace,
    RetrievalTransformations,
    RetrievalRouting,
    SafetyTrace,
    SafetyGroundedness,
    SafetyAnswerability,
)


def _parse_sse(raw: str) -> tuple[str, dict]:
    """Parse one SSE event string into (event, data)."""
    event = None
    data = None
    for line in raw.strip().split("\n"):
        if line.startswith("event: "):
            event = line[len("event: "):]
        elif line.startswith("data: "):
            data = json.loads(line[len("data: "):])
    return event, data


@pytest.fixture
def mock_trace():
    return RetrievalTrace(
        original_query="Test query",
        classification=None,
        classification_confidence=None,
        transformations=RetrievalTransformations(),
        routing=RetrievalRouting(),
        retrieval_runs=[],
        merged_candidates_count=0,
        reranking=None,
        collection_routing=None,
        reasoning_chain=None,
        parent_child_expansions_count=0,
        execution_time_ms={},
    )


@pytest.fixture
def mock_chunks():
    return [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "title": "Doc 1",
            "text": "Content about topic A",
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-2",
            "title": "Doc 2",
            "text": "Content about topic B",
        },
    ]


@pytest.fixture
def mock_safety_trace():
    return SafetyTrace(
        query_classification=None,
        injection_risk="low",
        matched_patterns=[],
        classifier_reason=None,
        groundedness=SafetyGroundedness(score=None, status="unchecked"),
        answerability=SafetyAnswerability(is_answerable=True, refusal_reason=None),
    )


@pytest.mark.asyncio
async def test_streaming_persists_groundedness_score(mock_chunks, mock_trace, mock_safety_trace):
    """Streaming path must calculate + persist groundedness_score like service.py."""
    answer_text = "Grounded answer based on sources."
    expected_score = 0.85
    expected_reason = "Answer is well supported by sources"
    session_id = "session-123"

    mock_retrieval = MagicMock()
    mock_retrieval.retrieve.return_value = (mock_chunks, mock_trace)

    mock_context = MagicMock()
    mock_context.assemble_context.return_value = {"prompt": "Context prompt"}

    mock_generation = MagicMock()
    mock_generation.generate_answer.return_value = iter(list(answer_text))
    mock_generation.llm_provider = MagicMock()

    mock_citation = MagicMock()
    mock_citation.extract_citations.return_value = []
    mock_citation.map_citations_to_chunks.return_value = []

    mock_grounding = MagicMock()
    mock_grounding.evaluate_evidence.return_value = (True, "")
    mock_grounding.calculate_groundedness.return_value = (expected_score, expected_reason)

    mock_safety = MagicMock()
    mock_safety.check_query.return_value = mock_safety_trace
    mock_safety.check_chunks.side_effect = lambda x: x

    mock_conflict = MagicMock()
    mock_conflict.detect_conflict.return_value = {
        "has_conflict": False,
        "surfaced_correctly": True,
        "conflict_details": "",
    }

    orchestrator = StreamingOrchestrator(
        advanced_retrieval_service=mock_retrieval,
        context_service=mock_context,
        generation_service=mock_generation,
        citation_service=mock_citation,
        grounding_service=mock_grounding,
        safety_service=mock_safety,
        conflict_service=mock_conflict,
    )

    update_calls = []

    def capture_update(turn_id, status, **kwargs):
        update_calls.append({"turn_id": turn_id, "status": status, **kwargs})
        return MagicMock()

    mock_session = ChatSession(id=session_id, collection_id=None)
    mock_turn = ChatTurn(
        id="turn-placeholder",
        session_id=session_id,
        query_text="Test query",
        status="generating",
    )

    with (
        patch("chat.streaming.ChatRepository.get_session", return_value=mock_session),
        patch("chat.streaming.ChatRepository.list_turns_by_session", return_value=[]),
        patch("chat.streaming.ChatRepository.create_turn", return_value=mock_turn),
        patch("chat.streaming.ChatRepository.update_turn_status", side_effect=capture_update),
        patch("chat.streaming.ChatRepository.create_citation") as mock_create_cit,
        patch("chat.streaming.load_chunk_notes", return_value={}),
        patch("chat.streaming.get_config") as mock_config,
        patch("chat.streaming.is_cancelled", return_value=False),
        patch("chat.streaming.clear_cancellation"),
    ):
        mock_config.return_value.retrieval = MagicMock()

        events = []
        async for raw in orchestrator.stream_turn(session_id, "Test query"):
            events.append(_parse_sse(raw))

    # calculate_groundedness called with full answer + chunks
    mock_grounding.calculate_groundedness.assert_called_once()
    call_args = mock_grounding.calculate_groundedness.call_args
    assert call_args[0][0] == answer_text
    assert call_args[0][1] == mock_chunks

    # update_turn_status on completed must include groundedness_score
    completed = [c for c in update_calls if c["status"] == "completed"]
    assert len(completed) == 1
    assert completed[0].get("groundedness_score") == expected_score

    # citations SSE event includes groundedness_score for client parity
    citation_events = [data for event, data in events if event == "citations"]
    assert len(citation_events) == 1
    assert citation_events[0].get("groundedness_score") == expected_score


@pytest.mark.asyncio
async def test_streaming_groundedness_when_empty_chunks(mock_trace, mock_safety_trace):
    """Empty chunks still call calculate_groundedness; score is persisted."""
    answer_text = "I don't have enough information."
    expected_score = 0.0
    expected_reason = "Missing answer or context."
    session_id = "session-empty"
    empty_chunks: list = []

    mock_retrieval = MagicMock()
    mock_retrieval.retrieve.return_value = (empty_chunks, mock_trace)

    mock_context = MagicMock()
    mock_context.assemble_context.return_value = {"prompt": "Context prompt"}

    mock_generation = MagicMock()
    mock_generation.generate_answer.return_value = iter(list(answer_text))
    mock_generation.llm_provider = MagicMock()

    mock_citation = MagicMock()
    mock_citation.extract_citations.return_value = []
    mock_citation.map_citations_to_chunks.return_value = []

    mock_grounding = MagicMock()
    # evaluate_evidence True so we reach generation + groundedness calc
    mock_grounding.evaluate_evidence.return_value = (True, "")
    mock_grounding.calculate_groundedness.return_value = (expected_score, expected_reason)

    mock_safety = MagicMock()
    mock_safety.check_query.return_value = mock_safety_trace
    mock_safety.check_chunks.side_effect = lambda x: x

    mock_conflict = MagicMock()
    mock_conflict.detect_conflict.return_value = {
        "has_conflict": False,
        "surfaced_correctly": True,
        "conflict_details": "",
    }

    orchestrator = StreamingOrchestrator(
        advanced_retrieval_service=mock_retrieval,
        context_service=mock_context,
        generation_service=mock_generation,
        citation_service=mock_citation,
        grounding_service=mock_grounding,
        safety_service=mock_safety,
        conflict_service=mock_conflict,
    )

    update_calls = []

    def capture_update(turn_id, status, **kwargs):
        update_calls.append({"turn_id": turn_id, "status": status, **kwargs})
        return MagicMock()

    mock_session = ChatSession(id=session_id, collection_id=None)
    mock_turn = ChatTurn(
        id="turn-placeholder",
        session_id=session_id,
        query_text="Test query",
        status="generating",
    )

    with (
        patch("chat.streaming.ChatRepository.get_session", return_value=mock_session),
        patch("chat.streaming.ChatRepository.list_turns_by_session", return_value=[]),
        patch("chat.streaming.ChatRepository.create_turn", return_value=mock_turn),
        patch("chat.streaming.ChatRepository.update_turn_status", side_effect=capture_update),
        patch("chat.streaming.ChatRepository.create_citation"),
        patch("chat.streaming.load_chunk_notes", return_value={}),
        patch("chat.streaming.get_config") as mock_config,
        patch("chat.streaming.is_cancelled", return_value=False),
        patch("chat.streaming.clear_cancellation"),
    ):
        mock_config.return_value.retrieval = MagicMock()

        async for _ in orchestrator.stream_turn(session_id, "Test query"):
            pass

    mock_grounding.calculate_groundedness.assert_called_once()
    completed = [c for c in update_calls if c["status"] == "completed"]
    assert len(completed) == 1
    assert completed[0].get("groundedness_score") == expected_score
