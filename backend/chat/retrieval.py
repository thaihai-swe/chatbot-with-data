from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import Depends

from config import get_config
from indexing.base import VectorStore
from providers.base import BaseEmbeddingProvider
from providers.factory import get_embedding_provider
from repositories.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant chunks from the vector index."""

    def __init__(
        self,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: VectorStore,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve_relevant_chunks(
        self,
        query_text: str,
        collection_ids: Optional[str | list[str]] = None,
        k: int | None = None,
        alpha: float | None = None,
    ) -> List[Dict[str, Any]]:
        config = get_config()
        k = k or config.retrieval.top_k

        if alpha is None:
            search_mode = config.retrieval.retrieval_mode
            if search_mode == "keyword":
                alpha = 0.0
            elif search_mode == "semantic":
                alpha = 1.0
            else:
                alpha = config.retrieval.hybrid_weight

        logger.info(f"Retrieving {k} chunks (alpha={alpha}) for query: '{query_text}' (collections={collection_ids})")

        query_embedding = self.embedding_provider.embed(query_text)

        raw_results = self.vector_store.query_hybrid(
            query_text=query_text,
            query_embedding=query_embedding,
            alpha=alpha,
            k=k,
            collection_ids=collection_ids
            if isinstance(collection_ids, list)
            else ([collection_ids] if collection_ids else None),
        )

        formatted_results = []
        chunk_repo = ChunkRepository()
        for chunk_id, similarity, metadata in raw_results:
            result = {"chunk_id": chunk_id, "similarity_score": float(similarity), **metadata}
            if chunk_id:
                chunk_data = chunk_repo.get_chunk(chunk_id)
                if chunk_data:
                    for key, value in chunk_data.items():
                        if key not in result and value is not None:
                            result[key] = value
            formatted_results.append(result)

        logger.info(f"Found {len(formatted_results)} relevant chunks")
        return formatted_results


def get_retrieval_service(
    embedding_provider: BaseEmbeddingProvider = Depends(get_embedding_provider),
) -> RetrievalService:
    from indexing.weaviate_store import WeaviateVectorStore

    vector_store = WeaviateVectorStore()
    return RetrievalService(embedding_provider, vector_store)
