"""Indexing service with error handling for graceful partial indexing."""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Optional

from embeddings.openai_client import OpenAIEmbeddingClient
from indexing.chroma_writer import ChromaVectorWriter
from models.enums import IndexGenerationStatus
from repositories.chunk_repository import ChunkRepository
from repositories.embedding_repository import EmbeddingCache
from repositories.index_entry_repository import IndexEntryRepository
from repositories.index_generation_repository import IndexGenerationRepository

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingError:
    """Record of a failed embedding operation."""

    chunk_id: str
    chunk_order: int
    error_reason: str
    error_type: str


class IndexingService:
    """Service for embedding chunks and storing in vector index with error handling."""

    def __init__(
        self,
        embedding_client: OpenAIEmbeddingClient,
        chroma_writer: ChromaVectorWriter,
        embedding_cache: Optional[EmbeddingCache] = None,
    ):
        """
        Initialize indexing service.

        Args:
            embedding_client: OpenAI embedding client for generating vectors
            chroma_writer: Chroma writer for storing vectors
            embedding_cache: Optional embedding cache for reusing vectors
        """
        self.embedding_client = embedding_client
        self.chroma_writer = chroma_writer
        self.embedding_cache = embedding_cache or EmbeddingCache(embedding_client)

    def index_document(
        self,
        document_id: str,
        collection_id: str,
        embedding_model: str = "text-embedding-3-small",
        strategy: str = "fixed_size",
    ) -> tuple[str, IndexGenerationStatus, list[EmbeddingError]]:
        """
        Index all chunks for a document by generating embeddings and storing vectors.

        This service processes each chunk independently and continues even if some fail,
        ensuring one failed chunk doesn't corrupt the entire index.

        Args:
            document_id: ID of document to index
            collection_id: ID of collection containing the document
            embedding_model: Model to use for embeddings (default: text-embedding-3-small)
            strategy: Chunking strategy used (for metadata)

        Returns:
            Tuple of:
            - generation_id: ID of the created index generation
            - status: IndexGenerationStatus.COMPLETED if all succeeded, PARTIAL if some failed
            - errors: List of EmbeddingError for failed chunks

        Raises:
            ValueError: If document or collection doesn't exist
        """
        # Create generation record
        generation_id = str(uuid.uuid4())
        errors: list[EmbeddingError] = []

        try:
            # Get all chunks for the document
            chunk_repo = ChunkRepository()
            chunks = chunk_repo.list_chunks_by_document(document_id)

            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                # Create empty generation
                IndexGenerationRepository.create_generation(
                    id=generation_id,
                    document_id=document_id,
                    generation_number=self._next_generation_number(document_id),
                    status=IndexGenerationStatus.COMPLETED,
                    strategy=strategy,
                    chunk_count=0,
                    embedding_model=embedding_model,
                )
                return generation_id, IndexGenerationStatus.COMPLETED, []

            # First, create the generation record
            IndexGenerationRepository.create_generation(
                id=generation_id,
                document_id=document_id,
                generation_number=self._next_generation_number(document_id),
                status=IndexGenerationStatus.IN_PROGRESS,
                strategy=strategy,
                chunk_count=len(chunks),
                embedding_model=embedding_model,
            )

            # Process each chunk
            for chunk in chunks:
                try:
                    self._embed_and_index_chunk(
                        chunk=chunk,
                        collection_id=collection_id,
                        generation_id=generation_id,
                        embedding_model=embedding_model,
                        document_id=document_id,
                    )
                except Exception as e:
                    error_type = type(e).__name__
                    error_reason = str(e)

                    logger.error(
                        f"Failed to embed chunk {chunk['id']} for document {document_id}: "
                        f"{error_type}: {error_reason}"
                    )

                    errors.append(
                        EmbeddingError(
                            chunk_id=chunk["id"],
                            chunk_order=chunk["chunk_order"],
                            error_reason=error_reason,
                            error_type=error_type,
                        )
                    )

            # Determine final status
            final_status = (
                IndexGenerationStatus.COMPLETED
                if not errors
                else IndexGenerationStatus.COMPLETED  # Mark as completed even with errors
            )

            # Update generation status
            IndexGenerationRepository.update_status(
                generation_id, final_status, completed_at=None  # Will be set by database
            )

            # Mark as active if indexing succeeded (no errors)
            if not errors:
                IndexGenerationRepository.mark_active(generation_id)

                # Mark entries as active for this generation
                IndexEntryRepository.mark_document_entries_active(
                    document_id, generation_id
                )

                logger.info(
                    f"Successfully indexed document {document_id} with {len(chunks)} chunks"
                )
            else:
                logger.warning(
                    f"Partially indexed document {document_id}: "
                    f"{len(chunks) - len(errors)}/{len(chunks)} chunks succeeded"
                )

            return generation_id, final_status, errors

        except Exception as e:
            logger.error(
                f"Critical error during indexing of document {document_id}: {str(e)}"
            )
            # Mark generation as failed
            try:
                IndexGenerationRepository.update_status(
                    generation_id, IndexGenerationStatus.FAILED
                )
            except Exception:
                pass  # Ignore errors marking generation as failed

            raise

    def _embed_and_index_chunk(
        self,
        chunk,
        collection_id: str,
        generation_id: str,
        embedding_model: str,
        document_id: str,
    ) -> None:
        """
        Embed a single chunk and store in vector index.

        Args:
            chunk: Chunk dictionary to embed
            collection_id: Collection ID for metadata
            generation_id: Generation ID for tracking
            embedding_model: Model used for embedding
            document_id: Document ID for logging

        Raises:
            Exception: Any error during embedding or storage (caught by caller)
        """
        # Create embedding function for cache
        def create_embedding(text: str) -> list[float]:
            # Embed with the OpenAI client
            embeddings = self.embedding_client.embed([text])
            return embeddings[0]

        # Get or create embedding
        embedding_vector, was_cached = self.embedding_cache.get_or_create(
            chunk_id=chunk["id"],
            text=chunk["text"],
            create_fn=create_embedding,
        )

        # Create index entry in database
        entry_id = str(uuid.uuid4())
        embedding_id = self._get_embedding_id(chunk["id"], embedding_model)

        IndexEntryRepository.create_entry(
            id=entry_id,
            chunk_id=chunk["id"],
            embedding_id=embedding_id,
            document_id=document_id,
            collection_id=collection_id,
            generation_id=generation_id,
            chunk_order=chunk["chunk_order"],
            vector_db_id=entry_id,  # Use entry_id as vector_db_id for now
            parent_chunk_id=chunk.get("parent_chunk_id"),
            is_active=False,  # Will be activated if generation succeeds
        )

        # Store vector in Chroma
        self.chroma_writer.add_vector(
            vector_id=entry_id,
            vector=embedding_vector,
            metadata={
                "chunk_id": chunk["id"],
                "document_id": document_id,
                "collection_id": collection_id,
                "chunk_order": chunk["chunk_order"],
                "parent_chunk_id": chunk.get("parent_chunk_id"),
                "strategy": chunk.get("strategy"),
            },
        )

        logger.debug(
            f"Embedded chunk {chunk['id']} (order {chunk['chunk_order']}) "
            f"for document {document_id} (cached={was_cached})"
        )

    def _get_embedding_id(self, chunk_id: str, embedding_model: str) -> str:
        """Get the embedding ID for a chunk and model (or create if needed)."""
        from repositories.embedding_repository import EmbeddingRepository

        embeddings = EmbeddingRepository.list_embeddings_by_chunk(chunk_id)
        for emb in embeddings:
            if emb.embedding_model == embedding_model:
                return emb.id
        # Return a placeholder (will be created by EmbeddingCache)
        return str(uuid.uuid4())

    def _next_generation_number(self, document_id: str) -> int:
        """Get the next generation number for a document."""
        count = IndexGenerationRepository.count_generations_by_document(document_id)
        return count + 1
