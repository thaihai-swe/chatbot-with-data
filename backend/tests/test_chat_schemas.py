import pytest
from schemas.chat import AdvancedRetrievalConfig, ChatTurnCreate, RetrievalTrace, ChatTurnResponse

def test_advanced_retrieval_config_defaults():
    config = AdvancedRetrievalConfig()
    assert config.enable_intelligence is False
    assert config.expansion_count == 3

def test_chat_turn_create_accepts_config():
    turn = ChatTurnCreate(query_text="What is this?", advanced_config=AdvancedRetrievalConfig(enable_expansion=True))
    assert turn.query_text == "What is this?"
    assert turn.advanced_config.enable_expansion is True

def test_chat_turn_create_default_config():
    turn = ChatTurnCreate(query_text="What is this?")
    assert turn.advanced_config is not None
    assert turn.advanced_config.enable_expansion is False

def test_retrieval_trace_creation():
    trace = RetrievalTrace(original_query="What is RAG?")
    assert trace.original_query == "What is RAG?"
    assert trace.merged_candidates_count == 0

def test_chat_turn_response_accepts_trace():
    trace = RetrievalTrace(original_query="Hello")
    response = ChatTurnResponse(
        id="1",
        session_id="2",
        query_text="Hello",
        answer_text=None,
        retrieved_chunks_json="[]",
        context_used_json="[]",
        status="done",
        error_message=None,
        created_at="now",
        updated_at="now",
        retrieval_trace=trace
    )
    assert response.retrieval_trace.original_query == "Hello"
