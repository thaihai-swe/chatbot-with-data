"""Service for collection-scoped retrieval from vector DB."""
from __future__ import annotations

import logging
from typing import Optional, List, Tuple, Dict, Any

from indexing.chroma_writer import ChromaVectorWriter
from embeddings.openai_client import OpenAIEmbeddingClient
from config import get_settings
from repositories.chunk_repository import ChunkRepository

logger = logging.getLogger(__name__)


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
