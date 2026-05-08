import pytest
from unittest.mock import Mock, MagicMock, patch
from schemas.chat import AdvancedRetrievalConfig, RerankingTrace
from chat.retrieval import AdvancedRetrievalService, RetrievalService, QueryIntelligenceService, CandidateMerger, RerankingService

def test_auto_collection_detection():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.return_value = []
    intel_service = Mock(spec=QueryIntelligenceService)
    intel_service.detect_collection.return_value = "col_x"
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(auto_collection_detection=True)
    
    with patch('chat.retrieval.Repository') as mock_repo_cls:
        mock_repo = mock_repo_cls.return_value
        mock_repo.list_collections.return_value = [{"id": "col_x", "name": "Test Col"}]
        
        _, trace = advanced_service.retrieve(query_text="Find x", config=config)
        
        intel_service.detect_collection.assert_called_once_with("Find x", [{"id": "col_x", "name": "Test Col"}])
        assert trace.routing.inferred_collections == ["col_x"]
        assert trace.routing.reason == "Auto-detected collection: col_x"

def test_candidate_merger():
    merger = CandidateMerger(rrf_k=60)
    list1 = [{"chunk_id": "c1", "similarity_score": 0.9}, {"chunk_id": "c2", "similarity_score": 0.8}]
    list2 = [{"chunk_id": "c2", "similarity_score": 0.85}, {"chunk_id": "c3", "similarity_score": 0.7}]
    list3 = [{"chunk_id": "c1", "similarity_score": 0.88}]
    
    merged = merger.merge([list1, list2, list3], top_k=2)
    assert len(merged) == 2
    assert merged[0]["chunk_id"] == "c1"

def test_advanced_retrieval_passthrough():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.return_value = [{"chunk_id": "c1", "similarity_score": 0.9}]
    intel_service = Mock(spec=QueryIntelligenceService)
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig()
    
    query = "What is the capital of France?"
    chunks, trace = advanced_service.retrieve(query_text=query, config=config, collection_id="col1", k=5)
    
    baseline_service.retrieve_relevant_chunks.assert_called_once_with(query_text=query, collection_id="col1", k=5)
    assert len(chunks) == 1

def test_multi_query_merging():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.side_effect = [
        [{"chunk_id": "c1", "similarity_score": 0.9}],
        [{"chunk_id": "c2", "similarity_score": 0.8}]
    ]
    intel_service = Mock(spec=QueryIntelligenceService)
    intel_service.expand_query.return_value = ["Expanded query"]
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(enable_expansion=True, expansion_count=1)
    
    chunks, trace = advanced_service.retrieve(query_text="Original", config=config, k=10)
    
    assert baseline_service.retrieve_relevant_chunks.call_count == 2
    assert "merging" in trace.execution_time_ms

def test_advanced_retrieval_transformations():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.return_value = []
    intel_service = Mock(spec=QueryIntelligenceService)
    intel_service.classify_query.return_value = "multi_hop"
    intel_service.expand_query.return_value = ["Q1", "Q2"]
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(enable_intelligence=True, enable_expansion=True, expansion_count=2)
    
    query = "Test query"
    _, trace = advanced_service.retrieve(query_text=query, config=config)
    assert trace.classification == "multi_hop"

def test_dynamic_routing_simple():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.return_value = []
    intel_service = Mock(spec=QueryIntelligenceService)
    intel_service.classify_query.return_value = "simple"
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(enable_intelligence=True, enable_dynamic_routing=True, enable_expansion=True)
    
    _, trace = advanced_service.retrieve(query_text="Query", config=config)
    assert trace.routing.selected_strategy == "baseline"

def test_dynamic_routing_multihop():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.return_value = []
    intel_service = Mock(spec=QueryIntelligenceService)
    intel_service.classify_query.return_value = "multi_hop"
    intel_service.decompose_query.return_value = ["sub q"]
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(enable_intelligence=True, enable_dynamic_routing=True)
    
    _, trace = advanced_service.retrieve(query_text="Query", config=config)
    assert trace.routing.selected_strategy == "decomposition"

def test_reranking():
    baseline_service = Mock(spec=RetrievalService)
    baseline_service.retrieve_relevant_chunks.return_value = [{"chunk_id": "c1", "similarity_score": 0.5}]
    intel_service = Mock(spec=QueryIntelligenceService)
    
    reranking_service = Mock(spec=RerankingService)
    reranking_service.rerank.return_value = (
        [{"chunk_id": "c1", "similarity_score": 0.9}],
        RerankingTrace(model="mock", pre_order_ids=["c1"], post_order_ids=["c1"])
    )
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(enable_reranking=True)
    
    chunks, trace = advanced_service.retrieve(query_text="Query", config=config)
    reranking_service.rerank.assert_called_once()
def test_parent_child_expansion():
    baseline_service = Mock(spec=RetrievalService)
    # Return two children with same parent, and one without parent
    baseline_service.retrieve_relevant_chunks.return_value = [
        {"chunk_id": "c1", "parent_chunk_id": "p1", "similarity_score": 0.9},
        {"chunk_id": "c2", "parent_chunk_id": "p1", "similarity_score": 0.8},
        {"chunk_id": "c3", "similarity_score": 0.7}
    ]
    intel_service = Mock(spec=QueryIntelligenceService)
    reranking_service = Mock(spec=RerankingService)
    
    advanced_service = AdvancedRetrievalService(baseline_service, intel_service, reranking_service)
    config = AdvancedRetrievalConfig(enable_parent_child=True)
    
    with patch('chat.retrieval.ChunkRepository') as mock_repo_cls:
        mock_repo = mock_repo_cls.return_value
        mock_repo.get_chunk.side_effect = lambda cid: {"chunk_id": cid, "text": "Parent Text"} if cid == "p1" else None
        
        chunks, trace = advanced_service.retrieve(query_text="Query", config=config)
        
        assert len(chunks) == 2
        assert chunks[0]["chunk_id"] == "p1"
        assert chunks[1]["chunk_id"] == "c3"
        assert chunks[0]["similarity_score"] == 0.9
        assert trace.parent_child_expansions_count == 1
