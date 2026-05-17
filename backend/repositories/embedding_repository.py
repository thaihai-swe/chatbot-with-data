import hashlib
import json
import uuid
from typing import Optional

from database import get_connection
from models.embedding import Embedding


class EmbeddingRepository:
    """Data access layer for cached embeddings."""

    @staticmethod
    def create_embedding(
        chunk_id: str,
        embedding_model: str,
        embedding_vector: list[float],
        input_text_hash: str,
        embedding_model_version: Optional[str] = None,
    ) -> Embedding:
        """
        Create and persist an embedding.

        Args:
            chunk_id: ID of chunk being embedded
            embedding_model: Name of embedding model (e.g., "text-embedding-3-small")
            embedding_vector: Vector as list of floats
            input_text_hash: Hash of input text for cache validation
            embedding_model_version: Optional model version

        Returns:
            Embedding object with all metadata

        Raises:
            ValueError: If inputs are invalid
        """
        if not chunk_id or not embedding_model or not embedding_vector:
            raise ValueError("chunk_id, embedding_model, and embedding_vector are required")

        embedding_id = str(uuid.uuid4())

        with get_connection() as conn:
            cursor = conn.cursor()

            # Serialize vector as JSON for storage
            vector_json = json.dumps(embedding_vector)

            cursor.execute(
                """
                INSERT INTO embeddings
                (id, chunk_id, embedding_model, embedding_model_version, embedding_vector, input_text_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    embedding_id,
                    chunk_id,
                    embedding_model,
                    embedding_model_version,
                    vector_json,
                    input_text_hash,
                ),
            )
            conn.commit()

        return Embedding(
            id=embedding_id,
            chunk_id=chunk_id,
            embedding_model=embedding_model,
            embedding_model_version=embedding_model_version,
            embedding_vector=embedding_vector,
            input_text_hash=input_text_hash,
            created_at="",  # Will be populated from DB
        )

    @staticmethod
    def get_cached_embedding(
        chunk_id: str,
        embedding_model: str,
    ) -> Optional[Embedding]:
        """
        Retrieve cached embedding if it exists.

        This is the core cache lookup for avoiding re-embedding.

        Args:
            chunk_id: ID of chunk
            embedding_model: Name of embedding model

        Returns:
            Embedding object if found, None otherwise
        """
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, chunk_id, embedding_model, embedding_model_version,
                       embedding_vector, input_text_hash, created_at
                FROM embeddings
                WHERE chunk_id = ? AND embedding_model = ?
                LIMIT 1
                """,
                (chunk_id, embedding_model),
            )

            row = cursor.fetchone()
            if not row:
                return None

            # Deserialize vector
            vector_json = row[4]
            embedding_vector = json.loads(vector_json) if isinstance(vector_json, str) else vector_json

            return Embedding(
                id=row[0],
                chunk_id=row[1],
                embedding_model=row[2],
                embedding_model_version=row[3],
                embedding_vector=embedding_vector,
                input_text_hash=row[5],
                created_at=row[6],
            )

    @staticmethod
    def get_embedding_by_id(embedding_id: str) -> Optional[Embedding]:
        """
        Retrieve embedding by ID.

        Args:
            embedding_id: ID of embedding record

        Returns:
            Embedding object if found, None otherwise
        """
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, chunk_id, embedding_model, embedding_model_version,
                       embedding_vector, input_text_hash, created_at
                FROM embeddings
                WHERE id = ?
                """,
                (embedding_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            vector_json = row[4]
            embedding_vector = json.loads(vector_json) if isinstance(vector_json, str) else vector_json

            return Embedding(
                id=row[0],
                chunk_id=row[1],
                embedding_model=row[2],
                embedding_model_version=row[3],
                embedding_vector=embedding_vector,
                input_text_hash=row[5],
                created_at=row[6],
            )

    @staticmethod
    def list_embeddings_by_chunk(chunk_id: str) -> list[Embedding]:
        """
        Get all embeddings for a chunk (possibly multiple models).

        Args:
            chunk_id: ID of chunk

        Returns:
            List of Embedding objects
        """
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, chunk_id, embedding_model, embedding_model_version,
                       embedding_vector, input_text_hash, created_at
                FROM embeddings
                WHERE chunk_id = ?
                ORDER BY created_at DESC
                """,
                (chunk_id,),
            )

            rows = cursor.fetchall()
            embeddings = []

            for row in rows:
                vector_json = row[4]
                embedding_vector = json.loads(vector_json) if isinstance(vector_json, str) else vector_json

                embeddings.append(
                    Embedding(
                        id=row[0],
                        chunk_id=row[1],
                        embedding_model=row[2],
                        embedding_model_version=row[3],
                        embedding_vector=embedding_vector,
                        input_text_hash=row[5],
                        created_at=row[6],
                    )
                )

            return embeddings

    @staticmethod
    def delete_embedding(embedding_id: str) -> bool:
        """
        Delete an embedding by ID.

        Args:
            embedding_id: ID of embedding to delete

        Returns:
            True if deleted, False if not found
        """
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM embeddings WHERE id = ?", (embedding_id,))
            conn.commit()

            return cursor.rowcount > 0

    @staticmethod
    def delete_embeddings_by_chunk(chunk_id: str) -> int:
        """
        Delete all embeddings for a chunk (when re-embedding).

        Args:
            chunk_id: ID of chunk

        Returns:
            Number of embeddings deleted
        """
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM embeddings WHERE chunk_id = ?", (chunk_id,))
            conn.commit()

            return cursor.rowcount

    @staticmethod
    def cache_is_valid(
        embedding: Embedding,
        current_text_hash: str,
    ) -> bool:
        """
        Validate that cached embedding is still valid.

        Cache is valid if the input text hash matches. This prevents using
        stale embeddings if the chunk text changed.

        Args:
            embedding: Cached embedding to validate
            current_text_hash: Current hash of chunk text

        Returns:
            True if cache is still valid, False if should re-embed
        """
        return embedding.input_text_hash == current_text_hash

    @staticmethod
    def compute_text_hash(text: str) -> str:
        """
        Compute hash of text for cache validation.

        Args:
            text: Text to hash

        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """High-level caching interface for embeddings."""

    def __init__(self, embedding_model: Optional[str] = None):
        """
        Initialize embedding cache.

        Args:
            embedding_model: Default embedding model to use (defaults to EMBEDDING_MODEL env var or text-embedding-3-small)
        """
        import os
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.repository = EmbeddingRepository()

    def get_or_create(
        self,
        chunk_id: str,
        text: str,
        create_fn,  # Callable that generates embedding if cache miss
    ) -> tuple[list[float], str, bool]:
        """
        Get embedding from cache or create if missing.

        Args:
            chunk_id: ID of chunk to embed
            text: Text content to embed
            create_fn: Callable that takes (text) and returns embedding vector

        Returns:
            Tuple of (embedding_vector, embedding_id, was_cached)
            - embedding_vector: The embedding as list of floats
            - embedding_id: ID of the embedding record
            - was_cached: True if from cache, False if newly created
        """
        # Compute hash of input text
        text_hash = EmbeddingRepository.compute_text_hash(text)

        # Try to get from cache
        cached = self.repository.get_cached_embedding(chunk_id, self.embedding_model)

        if cached and EmbeddingRepository.cache_is_valid(cached, text_hash):
            # Cache hit
            return cached.embedding_vector, cached.id, True

        # Cache miss - delete old embedding if it exists
        if cached:
            self.repository.delete_embedding(cached.id)

        # Generate new embedding
        embedding_vector = create_fn(text)

        # Store in cache
        embedding = self.repository.create_embedding(
            chunk_id=chunk_id,
            embedding_model=self.embedding_model,
            embedding_vector=embedding_vector,
            input_text_hash=text_hash,
        )

        return embedding_vector, embedding.id, False

    def get_cache_stats(self, chunk_id: str) -> dict:
        """
        Get cache statistics for a chunk.

        Args:
            chunk_id: ID of chunk

        Returns:
            Dict with embedding count, models, and cache info
        """
        embeddings = self.repository.list_embeddings_by_chunk(chunk_id)

        return {
            "chunk_id": chunk_id,
            "embedding_count": len(embeddings),
            "models": list(set(e.embedding_model for e in embeddings)),
            "embeddings": [
                {
                    "id": e.id,
                    "model": e.embedding_model,
                    "created_at": e.created_at,
                    "vector_dimension": len(e.embedding_vector),
                }
                for e in embeddings
            ],
        }
