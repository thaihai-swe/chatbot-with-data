"""Service for collection-scoped retrieval from vector DB."""
from __future__ import annotations

import logging
import json
import time
from typing import Optional, List, Tuple, Dict, Any

from indexing.chroma_writer import ChromaVectorWriter
from embeddings.openai_client import OpenAIEmbeddingClient
from config import get_settings
from repositories.chunk_repository import ChunkRepository
from schemas.chat import AdvancedRetrievalConfig, RetrievalTrace, RetrievalRunTrace
from chat.prompts import (
    QUERY_CLASSIFICATION_PROMPT,
    QUERY_EXPANSION_PROMPT,
    QUERY_DECOMPOSITION_PROMPT,
    HYDE_PROMPT,
    SYNONYM_EXPANSION_PROMPT,
    COLLECTION_DETECTION_PROMPT
)
from repositories.core import Repository
from fastapi import Depends

from llm.client import LLMClient, get_llm_client

logger = logging.getLogger(__name__)


class QueryIntelligenceService:
    """Service for LLM-powered query intelligence and transformation."""
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def _call_llm(self, prompt: str) -> str:
        # LLMClient handles temperature 0.0 internally or via parameters if supported
        # For simplicity, we pass messages and temperature=0.0
        return self.llm_client.generate_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            stream=False
        )

    def classify_query(self, query_text: str) -> str:
        prompt = QUERY_CLASSIFICATION_PROMPT.format(query_text=query_text)
        return self._call_llm(prompt)

    def expand_query(self, query_text: str, count: int) -> List[str]:
        prompt = QUERY_EXPANSION_PROMPT.format(query_text=query_text, count=count)
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except Exception as e:
            logger.error(f"Failed to parse query expansion JSON: {e}")
            return []

    def decompose_query(self, query_text: str) -> List[str]:
        prompt = QUERY_DECOMPOSITION_PROMPT.format(query_text=query_text)
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except Exception as e:
            logger.error(f"Failed to parse query decomposition JSON: {e}")
            return []

    def generate_hyde(self, query_text: str) -> str:
        prompt = HYDE_PROMPT.format(query_text=query_text)
        return self._call_llm(prompt)

    def expand_synonyms(self, query_text: str) -> Dict[str, str]:
        prompt = SYNONYM_EXPANSION_PROMPT.format(query_text=query_text)
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except Exception as e:
            logger.error(f"Failed to parse synonym JSON: {e}")
            return {}

    def detect_collection(self, query_text: str, collections: List[Dict[str, Any]]) -> Optional[str]:
        if not collections:
            return None
        
        collections_string = "\n".join([f"- ID: {c['id']}, Name: {c['name']}, Description: {c.get('description', '')}" for c in collections])
        prompt = COLLECTION_DETECTION_PROMPT.format(collections_string=collections_string, query_text=query_text)
        result = self._call_llm(prompt)
        
        # Valid ID check
        valid_ids = {c['id'] for c in collections}
        if result in valid_ids:
            return result
        return None


def get_query_intelligence_service(llm_client: LLMClient = Depends(get_llm_client)) -> QueryIntelligenceService:
    return QueryIntelligenceService(llm_client)



class CandidateMerger:
    """Service for merging candidate chunks from multiple retrieval runs using Reciprocal Rank Fusion."""
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def merge(self, results_list: List[List[Dict[str, Any]]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Merge multiple lists of chunks using RRF.
        Each chunk must have a 'chunk_id' to deduplicate.
        """
        if not results_list:
            return []
            
        chunk_map = {}
        rrf_scores = {}
        
        for results in results_list:
            for rank, chunk in enumerate(results):
                chunk_id = chunk.get("chunk_id")
                if not chunk_id:
                    continue
                    
                if chunk_id not in chunk_map:
                    chunk_map[chunk_id] = chunk
                    rrf_scores[chunk_id] = 0.0
                    
                rrf_scores[chunk_id] += 1.0 / (self.rrf_k + rank + 1)
                
        # Sort by RRF score descending
        sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)
        
        merged_chunks = []
        for cid in sorted_chunk_ids[:top_k]:
            chunk = chunk_map[cid].copy()
            chunk["similarity_score"] = rrf_scores[cid]
            chunk["original_score"] = chunk_map[cid].get("similarity_score")
            merged_chunks.append(chunk)
            
        return merged_chunks

class RetrievalService:
    """Service for retrieving relevant chunks from the vector index."""

    def __init__(
        self,
        embedding_client: OpenAIEmbeddingClient,
        chroma_writer: ChromaVectorWriter,
    ):
        """
        Initialize the retrieval service.

        Args:
            embedding_client: Client for generating embeddings of queries
            chroma_writer: Client for querying the vector DB
        """
        self.embedding_client = embedding_client
        self.chroma_writer = chroma_writer

    def retrieve_relevant_chunks(
        self,
        query_text: str,
        collection_id: Optional[str] = None,
        k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query, scoped to a collection.

        Args:
            query_text: The user's query
            collection_id: The collection ID to scope the search to (None for all)
            k: Number of chunks to retrieve

        Returns:
            List of chunk metadata dicts with similarity scores
        """
        logger.info(f"Retrieving {k} chunks for query: '{query_text}' (collection={collection_id})")
        
        # 1. Generate embedding for the query
        query_embedding = self.embedding_client.embed(query_text)
        
        # 2. Query Chroma
        if collection_id:
            # Query with collection filter
            raw_results = self.chroma_writer.query_by_collection(
                query_embedding=query_embedding,
                collection_id=collection_id,
                n_results=k,
            )
        else:
            # Query all collections
            results = self.chroma_writer.query(
                query_embedding=query_embedding,
                n_results=k,
            )
            
            # Flatten raw Chroma results into (chunk_id, similarity, metadata) format
            raw_results = []
            if results['ids'] and results['ids'][0]:
                for i, vector_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    metadata = results['metadatas'][0][i]
                    chunk_id = metadata.get('chunk_id')
                    raw_results.append((chunk_id, similarity, metadata))

        # 3. Format results
        formatted_results = []
        chunk_repo = ChunkRepository()
        for chunk_id, similarity, metadata in raw_results:
            result = {
                "chunk_id": chunk_id,
                "similarity_score": similarity,
                **metadata
            }
            
            if chunk_id:
                chunk_data = chunk_repo.get_chunk(chunk_id)
                if chunk_data:
                    for key, value in chunk_data.items():
                        if key not in result and value is not None:
                            result[key] = value
                            
            formatted_results.append(result)
            
        logger.info(f"Found {len(formatted_results)} relevant chunks")
        return formatted_results


def get_retrieval_service() -> RetrievalService:
    """Factory function for RetrievalService."""
    settings = get_settings()
    embedding_client = OpenAIEmbeddingClient(
        api_key=settings.openai_api_key,
        api_base=settings.openai_api_base,
        model=settings.embedding_model,
    )
    chroma_writer = ChromaVectorWriter(
        persist_directory=settings.chroma_db_path,
        collection_name=settings.chroma_collection_name,
    )
    return RetrievalService(embedding_client, chroma_writer)


from schemas.chat import AdvancedRetrievalConfig, RetrievalTrace, RetrievalRunTrace
from fastapi import Depends

class RerankingService:
    """Service for re-scoring candidates after retrieval."""
    def __init__(self, model: str = "dummy-reranker"):
        self.model = model

    def rerank(self, query_text: str, chunks: List[Dict[str, Any]], top_k: int) -> Tuple[List[Dict[str, Any]], RerankingTrace]:
        if not chunks:
            return chunks, RerankingTrace(model=self.model)
            
        t0 = time.time()
        pre_order_ids = [str(c.get("chunk_id")) for c in chunks]
        
        # Dummy reranking: Sort by similarity_score
        sorted_chunks = sorted(chunks, key=lambda c: c.get("similarity_score", 0), reverse=True)[:top_k]
        
        post_order_ids = [str(c.get("chunk_id")) for c in sorted_chunks]
        
        trace = RerankingTrace(
            model=self.model,
            pre_order_ids=pre_order_ids,
            post_order_ids=post_order_ids,
            latency_ms=int((time.time() - t0) * 1000)
        )
        return sorted_chunks, trace

def get_reranking_service() -> RerankingService:
    return RerankingService()

class AdvancedRetrievalService:
    """Wrapper service for advanced retrieval strategies."""
    
    def __init__(self, baseline_retrieval_service: RetrievalService, query_intelligence_service: QueryIntelligenceService, reranking_service: RerankingService):
        self.baseline_retrieval_service = baseline_retrieval_service
        self.query_intelligence_service = query_intelligence_service
        self.reranking_service = reranking_service
        self.candidate_merger = CandidateMerger()

    def retrieve(
        self,
        query_text: str,
        config: AdvancedRetrievalConfig,
        collection_id: Optional[str] = None,
        k: int = 10,
    ) -> Tuple[List[Dict[str, Any]], RetrievalTrace]:
        """
        Retrieve chunks using configured advanced strategies.
        Defaults to baseline if no advanced features are enabled.
        """
        trace = RetrievalTrace(original_query=query_text)
        
        if config.auto_collection_detection and not collection_id:
            core_repo = Repository()
            available_collections = core_repo.list_collections()
            t0 = time.time()
            inferred_collection = self.query_intelligence_service.detect_collection(query_text, available_collections)
            trace.execution_time_ms["collection_detection"] = int((time.time() - t0) * 1000)
            if inferred_collection:
                collection_id = inferred_collection
                trace.routing.inferred_collections.append(inferred_collection)
                trace.routing.reason = f"Auto-detected collection: {inferred_collection}"
            else:
                trace.routing.reason = "Auto-detection returned 'all' or invalid. Searching all collections."
                trace.routing.fallback_triggered = True
        
        if config.enable_intelligence:
            t0 = time.time()
            trace.classification = self.query_intelligence_service.classify_query(query_text)
            trace.execution_time_ms["classification"] = int((time.time() - t0) * 1000)
            
            if config.enable_dynamic_routing and trace.classification:
                if trace.classification == "simple":
                    config.enable_expansion = False
                    config.enable_decomposition = False
                    trace.routing.selected_strategy = "baseline"
                    trace.routing.reason = "Simple query: skipping expansion and decomposition."
                elif trace.classification == "multi_hop":
                    config.enable_decomposition = True
                    config.enable_expansion = False
                    trace.routing.selected_strategy = "decomposition"
                    trace.routing.reason = "Multi-hop query: enabling decomposition."
                elif trace.classification in ["out_of_domain", "conversational"]:
                    config.enable_expansion = False
                    config.enable_decomposition = False
                    trace.routing.selected_strategy = "baseline"
                    trace.routing.reason = f"Classification is {trace.classification}. Skipping expansion."
                else:
                    trace.routing.selected_strategy = "expansion"
                    config.enable_expansion = True
                    trace.routing.reason = f"Classification is {trace.classification}. Enabling expansion."
            else:
                trace.routing.selected_strategy = "manual"
                trace.routing.reason = "Dynamic routing disabled or no classification available."
            
        if config.enable_expansion:
            t0 = time.time()
            trace.transformations.expanded_queries = self.query_intelligence_service.expand_query(query_text, config.expansion_count)
            trace.execution_time_ms["expansion"] = int((time.time() - t0) * 1000)
            
        if config.enable_decomposition:
            t0 = time.time()
            trace.transformations.sub_questions = self.query_intelligence_service.decompose_query(query_text)
            trace.execution_time_ms["decomposition"] = int((time.time() - t0) * 1000)
            
        if config.enable_hyde:
            t0 = time.time()
            trace.transformations.hyde_doc = self.query_intelligence_service.generate_hyde(query_text)
            trace.execution_time_ms["hyde"] = int((time.time() - t0) * 1000)
            
        if config.enable_synonym_expansion:
            t0 = time.time()
            trace.transformations.synonym_expansions = self.query_intelligence_service.expand_synonyms(query_text)
            trace.execution_time_ms["synonym_expansion"] = int((time.time() - t0) * 1000)
        
        queries_to_run = [query_text]
        
        if config.enable_expansion and trace.transformations.expanded_queries:
            queries_to_run.extend(trace.transformations.expanded_queries)
            
        if config.enable_decomposition and trace.transformations.sub_questions:
            queries_to_run.extend(trace.transformations.sub_questions)
            
        if config.enable_hyde and trace.transformations.hyde_doc:
            queries_to_run.append(trace.transformations.hyde_doc)
            
        all_results = []
        for q in queries_to_run:
            search_query = q
            if config.enable_synonym_expansion and trace.transformations.synonym_expansions:
                for old, new in trace.transformations.synonym_expansions.items():
                    search_query = search_query.replace(old, new)
                    
            chunks = self.baseline_retrieval_service.retrieve_relevant_chunks(
                query_text=search_query,
                collection_id=collection_id,
                k=k
            )
            all_results.append(chunks)
            trace.retrieval_runs.append(RetrievalRunTrace(
                query=search_query,
                raw_count=len(chunks),
                top_scores=[float(c.get("similarity_score", 0.0)) for c in chunks]
            ))
            
        if len(all_results) > 1:
            t0 = time.time()
            merged_chunks = self.candidate_merger.merge(all_results, top_k=k)
            trace.execution_time_ms["merging"] = int((time.time() - t0) * 1000)
            final_chunks = merged_chunks
        else:
            final_chunks = all_results[0] if all_results else []
            
        trace.merged_candidates_count = len(final_chunks)

        if config.enable_reranking:
            top_k_rerank = config.reranker_top_k or k
            t0 = time.time()
            final_chunks, rerank_trace = self.reranking_service.rerank(query_text, final_chunks, top_k_rerank)
            trace.reranking = rerank_trace
            trace.execution_time_ms["reranking"] = int((time.time() - t0) * 1000)

        if config.enable_parent_child:
            t0 = time.time()
            expanded_chunks = []
            seen_parent_ids = set()
            chunk_repo = ChunkRepository()
            
            for chunk in final_chunks:
                parent_id = chunk.get("parent_chunk_id")
                if parent_id:
                    if parent_id not in seen_parent_ids:
                        seen_parent_ids.add(parent_id)
                        parent_chunk = chunk_repo.get_chunk(parent_id)
                        if parent_chunk:
                            # Inherit scores from child for downstream consistency
                            parent_chunk["similarity_score"] = chunk.get("similarity_score", 0.0)
                            if "original_score" in chunk:
                                parent_chunk["original_score"] = chunk["original_score"]
                            expanded_chunks.append(parent_chunk)
                            trace.parent_child_expansions_count += 1
                        else:
                            expanded_chunks.append(chunk)
                else:
                    expanded_chunks.append(chunk)
            
            final_chunks = expanded_chunks
            trace.execution_time_ms["parent_child_expansion"] = int((time.time() - t0) * 1000)

        return final_chunks, trace

    def retrieve_relevant_chunks(
        self,
        query_text: str,
        collection_id: Optional[str] = None,
        k: int = 10,
        config: Optional[AdvancedRetrievalConfig] = None,
    ) -> List[Dict[str, Any]]:
        """
        Compatibility wrapper for callers that still expect the baseline
        retrieval interface.
        """
        effective_config = config if config is not None else AdvancedRetrievalConfig()
        chunks, _ = self.retrieve(
            query_text=query_text,
            config=effective_config,
            collection_id=collection_id,
            k=k,
        )
        return chunks


def get_advanced_retrieval_service(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    query_intelligence_service: QueryIntelligenceService = Depends(get_query_intelligence_service),
    reranking_service: RerankingService = Depends(get_reranking_service)
) -> AdvancedRetrievalService:
    """Factory function for AdvancedRetrievalService."""
    return AdvancedRetrievalService(retrieval_service, query_intelligence_service, reranking_service)
