from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Depends

from config import get_config
from repositories.chunk_repository import ChunkRepository
from chat.candidate_merger import CandidateMerger
from chat.multi_hop import MultiHopRetrievalOrchestrator
from chat.query_intelligence import QueryIntelligenceService, get_query_intelligence_service
from chat.reranking import RerankingService, get_reranking_service
from chat.retrieval import RetrievalService, get_retrieval_service
from schemas.chat import RetrievalTrace, RetrievalRunTrace
from schemas.settings import RetrievalSettings

logger = logging.getLogger(__name__)


class AdvancedRetrievalService:
    """Wrapper service for advanced retrieval strategies."""

    def __init__(
        self,
        baseline_retrieval_service: RetrievalService,
        query_intelligence_service: QueryIntelligenceService,
        reranking_service: RerankingService,
    ):
        self.baseline_retrieval_service = baseline_retrieval_service
        self.query_intelligence_service = query_intelligence_service
        self.reranking_service = reranking_service
        self.candidate_merger = CandidateMerger()

    def retrieve(
        self,
        query_text: str,
        config: RetrievalSettings,
        collection_ids: Optional[list[str]] = None,
        k: int | None = None,
    ) -> Tuple[List[Dict[str, Any]], RetrievalTrace]:
        global_config = get_config()
        k = k or global_config.retrieval.top_k

        trace = RetrievalTrace(original_query=query_text)

        # Determine effective grounding threshold (collection override > global default)
        if collection_ids and len(collection_ids) == 1:
            from repositories.collection_repository import CollectionRepository
            collection = CollectionRepository().get_collection(collection_ids[0])
            if collection and collection.get("min_similarity_threshold") is not None:
                trace.grounding_threshold_used = float(collection["min_similarity_threshold"])
            else:
                trace.grounding_threshold_used = global_config.safety.min_similarity_threshold
        else:
            trace.grounding_threshold_used = global_config.safety.min_similarity_threshold

        if config.intelligence_enabled:
            t0 = time.time()
            intent, confidence = self.query_intelligence_service.classify_query(query_text)
            if confidence < 0.6:
                intent = "factual"

            trace.classification = intent
            trace.classification_confidence = confidence
            trace.execution_time_ms["classification"] = int((time.time() - t0) * 1000)

            if config.dynamic_routing_enabled and trace.classification:
                config.query_expansion_enabled = False
                config.query_decomposition_enabled = False
                config.hyde_enabled = False
                config.synonym_expansion_enabled = False

                if trace.classification == "factual":
                    trace.routing.selected_strategy = "baseline"
                    trace.routing.reason = "Factual query: skipping complex expansions."
                elif trace.classification == "comparison":
                    config.query_decomposition_enabled = True
                    trace.routing.selected_strategy = "decomposition"
                    trace.routing.reason = "Comparison query: enabling decomposition."
                elif trace.classification == "how_to":
                    config.hyde_enabled = True
                    trace.routing.selected_strategy = "hyde"
                    trace.routing.reason = "How-to query: enabling HyDE."
                elif trace.classification == "troubleshooting":
                    config.synonym_expansion_enabled = True
                    trace.routing.selected_strategy = "synonym_expansion"
                    trace.routing.reason = "Troubleshooting query: enabling synonym expansion."
                elif trace.classification == "exploratory":
                    config.query_expansion_enabled = True
                    trace.routing.selected_strategy = "expansion"
                    trace.routing.reason = "Exploratory query: enabling query expansion."
                else:
                    trace.routing.selected_strategy = "baseline"
                    trace.routing.reason = f"Classification {trace.classification} unmapped. Defaulting to baseline."
            else:
                trace.routing.selected_strategy = "manual"
                trace.routing.reason = "Dynamic routing disabled or no classification available."

        if config.intelligence_enabled:
            t0 = time.time()
            rewritten = self.query_intelligence_service.rewrite_query(query_text)
            trace.transformations.rewritten_query = rewritten
            trace.execution_time_ms["rewriting"] = int((time.time() - t0) * 1000)

        queries_to_run = [query_text]
        if config.intelligence_enabled and trace.transformations.rewritten_query:
            if trace.transformations.rewritten_query != query_text:
                queries_to_run.append(trace.transformations.rewritten_query)

        all_variations = []

        for q in queries_to_run:
            if config.query_expansion_enabled:
                t0 = time.time()
                vars = self.query_intelligence_service.expand_query(q, config.query_expansion_count)
                all_variations.extend(vars)
                trace.execution_time_ms["expansion"] = trace.execution_time_ms.get("expansion", 0) + int((time.time() - t0) * 1000)

        if config.query_expansion_enabled:
            trace.transformations.expanded_queries = list(set(all_variations))

        if config.query_decomposition_enabled:
            t0 = time.time()
            trace.transformations.sub_questions = self.query_intelligence_service.decompose_query(query_text)
            trace.execution_time_ms["decomposition"] = int((time.time() - t0) * 1000)

        if config.multi_hop_enabled and trace.transformations.sub_questions and len(trace.transformations.sub_questions) > 1:
            logger.info("Multi-hop enabled with multiple sub-questions, using MultiHopRetrievalOrchestrator")
            try:
                orchestrator = MultiHopRetrievalOrchestrator(
                    retrieval_service=self,
                    llm_client=self.query_intelligence_service.llm_provider,
                )
                chunks, reasoning_chain = orchestrator.execute_multi_hop(
                    query=query_text,
                    sub_questions=trace.transformations.sub_questions,
                    config=config,
                    collection_ids=collection_ids or [],
                )
                trace.reasoning_chain = reasoning_chain
                trace.merged_candidates_count = len(chunks)

                if config.reranker_enabled and chunks:
                    top_k_rerank = config.reranker_top_n or k
                    chunks, rerank_trace = self.reranking_service.rerank(query_text, chunks, top_k_rerank)
                    trace.reranking = rerank_trace

                return chunks, trace
            except Exception as e:
                logger.error(f"Multi-hop execution failed: {e}, falling back to parallel retrieval")

        if config.hyde_enabled:
            t0 = time.time()
            trace.transformations.hyde_doc = self.query_intelligence_service.generate_hyde(query_text)
            trace.execution_time_ms["hyde"] = int((time.time() - t0) * 1000)

        if config.synonym_expansion_enabled:
            t0 = time.time()
            trace.transformations.synonym_expansions = self.query_intelligence_service.expand_synonyms(query_text)
            trace.execution_time_ms["synonym_expansion"] = int((time.time() - t0) * 1000)

        unique_queries = list(set(queries_to_run))
        if config.query_expansion_enabled and trace.transformations.expanded_queries:
            unique_queries.extend(trace.transformations.expanded_queries)

        if config.query_decomposition_enabled and trace.transformations.sub_questions:
            unique_queries.extend(trace.transformations.sub_questions)

        if config.hyde_enabled and trace.transformations.hyde_doc:
            unique_queries.append(trace.transformations.hyde_doc)

        unique_queries = list(dict.fromkeys(unique_queries))

        search_mode = config.retrieval_mode or global_config.retrieval.retrieval_mode

        if search_mode == "keyword":
            effective_alpha = 0.0
        elif search_mode == "semantic":
            effective_alpha = 1.0
        else:
            effective_alpha = config.hybrid_weight if config.hybrid_weight is not None else global_config.retrieval.hybrid_weight

        all_results = []
        for q in unique_queries:
            search_query = q
            if config.synonym_expansion_enabled and trace.transformations.synonym_expansions:
                for old, new in trace.transformations.synonym_expansions.items():
                    if isinstance(new, list):
                        new = " ".join(map(str, new))
                    elif not isinstance(new, str):
                        new = str(new)
                    search_query = search_query.replace(old, new)

            chunks = self.baseline_retrieval_service.retrieve_relevant_chunks(
                query_text=search_query,
                collection_ids=collection_ids,
                k=k,
                alpha=effective_alpha,
            )
            all_results.append(chunks)
            trace.retrieval_runs.append(RetrievalRunTrace(
                query=search_query,
                raw_count=len(chunks),
                top_scores=[float(c.get("similarity_score", 0.0)) for c in chunks],
            ))

        if len(all_results) > 1:
            t0 = time.time()
            merged_chunks = self.candidate_merger.merge(all_results, top_k=k)
            trace.execution_time_ms["merging"] = int((time.time() - t0) * 1000)
            final_chunks = merged_chunks
        else:
            final_chunks = all_results[0] if all_results else []

        trace.merged_candidates_count = len(final_chunks)

        if config.reranker_enabled:
            top_k_rerank = config.reranker_top_n or k
            t0 = time.time()
            final_chunks, rerank_trace = self.reranking_service.rerank(query_text, final_chunks, top_k_rerank)
            trace.reranking = rerank_trace
            trace.execution_time_ms["reranking"] = int((time.time() - t0) * 1000)

        if config.parent_child_enabled:
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

        # TODO: Populate trace.grounding_filtered_chunks after grounding evaluation
        # This requires passing grounding_service to AdvancedRetrievalService or
        # moving the filtering logic to be accessible here

        return final_chunks, trace

    def retrieve_relevant_chunks(
        self,
        query_text: str,
        collection_ids: Optional[list[str]] = None,
        k: int | None = None,
        config: Optional[RetrievalSettings] = None,
    ) -> List[Dict[str, Any]]:
        effective_config = config if config is not None else get_config().retrieval
        chunks, _ = self.retrieve(
            query_text=query_text,
            config=effective_config,
            collection_ids=collection_ids,
            k=k,
        )
        return chunks


def get_advanced_retrieval_service(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    query_intelligence_service: QueryIntelligenceService = Depends(get_query_intelligence_service),
    reranking_service: RerankingService = Depends(get_reranking_service),
) -> AdvancedRetrievalService:
    return AdvancedRetrievalService(retrieval_service, query_intelligence_service, reranking_service)
