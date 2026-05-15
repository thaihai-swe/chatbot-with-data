import asyncio
from types import SimpleNamespace
from unittest.mock import Mock, patch

from chat.retrieval import AdvancedRetrievalService
from chat.streaming import StreamingOrchestrator
from routers.chat import submit_turn_stream
from schemas.chat import AdvancedRetrievalConfig, ChatTurnCreate


def test_streaming_orchestrator_uses_advanced_retrieval_service():
    advanced_retrieval_service = Mock(spec=AdvancedRetrievalService)
    advanced_retrieval_service.retrieve.return_value = (
        [{"chunk_id": "c1", "document_id": "d1", "similarity_score": 0.9}],
        Mock(),
    )
    context_service = Mock()
    context_service.assemble_context.return_value = {"chunks": 1}
    generation_service = Mock()
    citation_service = Mock()
    grounding_service = Mock()
    grounding_service.evaluate_evidence.return_value = (False, "Not enough evidence")

    orchestrator = StreamingOrchestrator(
        advanced_retrieval_service,
        context_service,
        generation_service,
        citation_service,
        grounding_service,
    )
    config = AdvancedRetrievalConfig(enable_expansion=True)

    with patch("chat.streaming.ChatRepository.get_session", return_value=SimpleNamespace(collection_id="col1")), \
         patch("chat.streaming.ChatRepository.list_turns_by_session", return_value=[]), \
         patch("chat.streaming.ChatRepository.create_turn"), \
         patch("chat.streaming.ChatRepository.update_turn_status"):

        async def collect_events():
            return [
                event
                async for event in orchestrator.stream_turn(
                    "session-1",
                    "Where is the answer?",
                    advanced_config=config,
                )
            ]

        events = asyncio.run(collect_events())

    advanced_retrieval_service.retrieve.assert_called_once_with(
        query_text="Where is the answer?",
        config=config,
        collection_id="col1",
    )
    assert any("event: done" in event for event in events)


def test_stream_route_forwards_advanced_config():
    class StubOrchestrator:
        def __init__(self):
            self.calls = []

        async def stream_turn(self, session_id, query_text, advanced_config=None):
            self.calls.append((session_id, query_text, advanced_config))
            yield "event: done\ndata: {}\n\n"

    orchestrator = StubOrchestrator()
    payload = ChatTurnCreate(
        query_text="Explain this",
        advanced_config=AdvancedRetrievalConfig(enable_hyde=True),
    )

    async def invoke_route():
        response = await submit_turn_stream("session-2", payload, orchestrator)
        body = []
        async for chunk in response.body_iterator:
            body.append(chunk.decode() if isinstance(chunk, bytes) else chunk)
        return response, "".join(body)

    response, body = asyncio.run(invoke_route())

    assert response.media_type == "text/event-stream"
    assert body == "event: done\ndata: {}\n\n"
    assert len(orchestrator.calls) == 1
    session_id, query_text, advanced_config = orchestrator.calls[0]
    assert session_id == "session-2"
    assert query_text == "Explain this"
    assert advanced_config is not None
    assert advanced_config.enable_hyde is True
