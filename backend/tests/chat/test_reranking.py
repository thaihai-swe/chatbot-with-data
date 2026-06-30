import pytest
from unittest.mock import patch, MagicMock

from providers.reranker import DummyRerankingProvider, FlashRankProvider
from chat.reranking import RerankingService


def test_dummy_reranking_provider():
    provider = DummyRerankingProvider()
    
    chunks = [
        {"chunk_id": "1", "similarity_score": 0.5},
        {"chunk_id": "2", "similarity_score": 0.9},
        {"chunk_id": "3", "similarity_score": 0.2},
    ]
    
    sorted_chunks = provider.rerank("query", chunks, top_k=2)
    
    assert len(sorted_chunks) == 2
    assert sorted_chunks[0]["chunk_id"] == "2"
    assert sorted_chunks[1]["chunk_id"] == "1"
    assert provider.get_model_name() == "dummy-reranker"


@patch("flashrank.Ranker")
def test_flashrank_provider_initialization_and_rerank(mock_ranker_class):
    # Mock the ranker instance and its rerank method
    mock_ranker_instance = MagicMock()
    mock_ranker_class.return_value = mock_ranker_instance
    
    mock_ranker_instance.rerank.return_value = [
        {"id": "2", "text": "high score text", "score": 0.99, "original_chunk": {"chunk_id": "2", "text": "high score text"}},
        {"id": "1", "text": "low score text", "score": 0.10, "original_chunk": {"chunk_id": "1", "text": "low score text"}},
    ]
    
    provider = FlashRankProvider(model_name="test-model")
    assert provider.get_model_name() == "test-model"
    
    chunks = [
        {"chunk_id": "1", "text": "low score text"},
        {"chunk_id": "2", "text": "high score text"},
    ]
    
    sorted_chunks = provider.rerank("query", chunks, top_k=2)
    
    # Assertions on the output mapping
    assert len(sorted_chunks) == 2
    assert sorted_chunks[0]["chunk_id"] == "2"
    assert sorted_chunks[0]["rerank_score"] == 0.99
    assert sorted_chunks[1]["chunk_id"] == "1"
    assert sorted_chunks[1]["rerank_score"] == 0.10


def test_reranking_service_delegates_to_provider():
    mock_provider = MagicMock()
    mock_provider.get_model_name.return_value = "mock-model"
    mock_provider.rerank.return_value = [
        {"chunk_id": "2", "rerank_score": 0.99},
        {"chunk_id": "1", "rerank_score": 0.50},
    ]
    
    service = RerankingService(provider=mock_provider)
    
    chunks = [{"chunk_id": "1"}, {"chunk_id": "2"}, {"chunk_id": "3"}]
    
    sorted_chunks, trace = service.rerank("test query", chunks, top_k=2)
    
    mock_provider.rerank.assert_called_once_with("test query", chunks, 2)
    
    assert len(sorted_chunks) == 2
    assert trace.model == "mock-model"
    assert trace.pre_order_ids == ["1", "2", "3"]
    assert trace.post_order_ids == ["2", "1"]
    assert trace.latency_ms >= 0
