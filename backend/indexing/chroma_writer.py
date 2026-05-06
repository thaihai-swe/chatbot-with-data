import logging
from typing import Optional

import chromadb

logger = logging.getLogger(__name__)


class ChromaVectorWriter:
    """Vector index writer for Chroma vector database."""

    def __init__(
        self,
        persist_directory: str = ".chroma_db",
        collection_name: str = "document-chunks",
    ):
        """
        Initialize Chroma vector writer.

        Args:
            persist_directory: Path to persist Chroma database
            collection_name: Name of Chroma collection to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize Chroma client with persistence (new API)
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Document chunks with embeddings"},
        )

        logger.info(f"ChromaVectorWriter initialized: {persist_directory}/{collection_name}")

    def _sanitize_metadata(self, metadata: dict) -> dict:
        """
        Sanitize metadata for Chroma compatibility.

        Chroma's metadata doesn't support None values or complex objects.
        Remove None values and convert complex types to strings if needed.

        Args:
            metadata: Raw metadata dict

        Returns:
            Sanitized metadata compatible with Chroma
        """
        sanitized = {}
        for key, value in metadata.items():
            # Skip None values - Chroma doesn't support them
            if value is None:
                continue

            # Keep strings, numbers as-is
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                # Convert other types to string
                sanitized[key] = str(value)

        return sanitized

    def add_vector(
        self,
        vector_id: str,
        embedding: list[float],
        metadata: dict,
    ) -> str:
        """
        Add a single vector to the index.

        Args:
            vector_id: Unique ID for this vector entry (usually UUID)
            embedding: Embedding vector (list of floats)
            metadata: Metadata dict with: chunk_id, document_id, collection_id,
                     chunk_order, source_url (optional), page_number (optional),
                     section_title (optional), parent_chunk_id (optional)

        Returns:
            The vector_id (for confirmation)

        Raises:
            ValueError: If metadata is missing required fields
        """
        # Validate required metadata
        required_keys = {"chunk_id", "document_id", "collection_id", "chunk_order"}
        if not required_keys.issubset(metadata.keys()):
            raise ValueError(f"Metadata missing required keys: {required_keys - set(metadata.keys())}")

        # Sanitize metadata for Chroma
        sanitized_metadata = self._sanitize_metadata(metadata)

        # Add to collection
        try:
            self.collection.add(
                ids=[vector_id],
                embeddings=[embedding],
                metadatas=[sanitized_metadata],
            )
            logger.debug(f"Added vector {vector_id} to Chroma collection")
            return vector_id

        except Exception as e:
            logger.error(f"Error adding vector {vector_id} to Chroma: {str(e)}")
            raise

    def add_vectors_batch(
        self,
        vectors_data: list[tuple[str, list[float], dict]],
    ) -> int:
        """
        Add multiple vectors in a batch for efficiency.

        Args:
            vectors_data: List of tuples (vector_id, embedding, metadata)

        Returns:
            Number of vectors added
        """
        if not vectors_data:
            return 0

        vector_ids = []
        embeddings = []
        metadatas = []

        for vector_id, embedding, metadata in vectors_data:
            # Validate metadata
            required_keys = {"chunk_id", "document_id", "collection_id", "chunk_order"}
            if not required_keys.issubset(metadata.keys()):
                raise ValueError(f"Metadata missing required keys for {vector_id}")

            # Sanitize metadata
            sanitized = self._sanitize_metadata(metadata)

            vector_ids.append(vector_id)
            embeddings.append(embedding)
            metadatas.append(sanitized)

        try:
            self.collection.add(
                ids=vector_ids,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            logger.info(f"Added {len(vector_ids)} vectors to Chroma collection")
            return len(vector_ids)

        except Exception as e:
            logger.error(f"Error adding batch of {len(vector_ids)} vectors: {str(e)}")
            raise

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        collection_filter: Optional[str] = None,
    ) -> dict:
        """
        Query the vector index for similar embeddings.

        Args:
            query_embedding: Query vector as list of floats
            n_results: Number of results to return
            collection_filter: Optional collection_id to filter results

        Returns:
            Dict with 'ids', 'embeddings', 'metadatas', 'distances'
        """
        where_filter = None
        if collection_filter:
            where_filter = {"collection_id": {"$eq": collection_filter}}

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["embeddings", "metadatas", "distances"],
            )

            logger.debug(f"Query returned {len(results['ids'][0])} results")
            return results

        except Exception as e:
            logger.error(f"Error querying Chroma: {str(e)}")
            raise

    def query_by_collection(
        self,
        query_embedding: list[float],
        collection_id: str,
        n_results: int = 10,
    ) -> list[tuple[str, float, dict]]:
        """
        Query with automatic collection filtering.

        Args:
            query_embedding: Query vector
            collection_id: Collection ID to filter by
            n_results: Number of results

        Returns:
            List of (chunk_id, similarity_score, metadata) tuples
        """
        results = self.query(
            query_embedding=query_embedding,
            n_results=n_results,
            collection_filter=collection_id,
        )

        # Flatten results and compute similarity from distance
        # Chroma returns cosine distance; convert to similarity (1 - distance)
        output = []

        if results['ids'] and results['ids'][0]:
            for i, vector_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                metadata = results['metadatas'][0][i]
                chunk_id = metadata.get('chunk_id')

                output.append((chunk_id, similarity, metadata))

        return output

    def get_vector(self, vector_id: str) -> Optional[dict]:
        """
        Retrieve a specific vector by ID.

        Args:
            vector_id: ID of vector to retrieve

        Returns:
            Dict with 'embedding' and 'metadata' or None if not found
        """
        try:
            results = self.collection.get(
                ids=[vector_id],
                include=["embeddings", "metadatas"],
            )

            if results['ids'] and len(results['ids']) > 0:
                embeddings = results.get('embeddings')
                embedding = embeddings[0] if embeddings is not None and len(embeddings) > 0 else None
                metadatas = results.get('metadatas')
                metadata = metadatas[0] if metadatas is not None and len(metadatas) > 0 else {}

                return {
                    "embedding": embedding,
                    "metadata": metadata,
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving vector {vector_id}: {str(e)}")
            raise

    def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector from the index.

        Args:
            vector_id: ID of vector to delete

        Returns:
            True if deleted, False if not found
        """
        try:
            self.collection.delete(ids=[vector_id])
            logger.debug(f"Deleted vector {vector_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting vector {vector_id}: {str(e)}")
            raise

    def delete_by_document(self, document_id: str) -> int:
        """
        Delete all vectors for a specific document.

        Args:
            document_id: ID of document to delete vectors for

        Returns:
            Number of vectors deleted
        """
        try:
            where_filter = {"document_id": {"$eq": document_id}}

            # Get vectors matching filter
            results = self.collection.get(where=where_filter)
            vector_ids = results['ids']

            if vector_ids:
                self.collection.delete(ids=vector_ids)
                logger.info(f"Deleted {len(vector_ids)} vectors for document {document_id}")

            return len(vector_ids)

        except Exception as e:
            logger.error(f"Error deleting vectors for document {document_id}: {str(e)}")
            raise

    def delete_by_collection(self, collection_id: str) -> int:
        """
        Delete all vectors for a specific collection.

        Args:
            collection_id: ID of collection to delete vectors for

        Returns:
            Number of vectors deleted
        """
        try:
            where_filter = {"collection_id": {"$eq": collection_id}}

            # Get vectors matching filter
            results = self.collection.get(where=where_filter)
            vector_ids = results['ids']

            if vector_ids:
                self.collection.delete(ids=vector_ids)
                logger.info(f"Deleted {len(vector_ids)} vectors for collection {collection_id}")

            return len(vector_ids)

        except Exception as e:
            logger.error(f"Error deleting vectors for collection {collection_id}: {str(e)}")
            raise

    def count_vectors(self) -> int:
        """
        Get total count of vectors in collection.

        Returns:
            Number of vectors
        """
        try:
            count = self.collection.count()
            return count

        except Exception as e:
            logger.error(f"Error counting vectors: {str(e)}")
            raise

    def clear_collection(self):
        """Clear all vectors from the current collection."""
        try:
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks with embeddings"},
            )
            logger.info(f"Cleared collection {self.collection_name}")

        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

    def get_collection_stats(self) -> dict:
        """
        Get statistics about the collection.

        Returns:
            Dict with collection info
        """
        try:
            count = self.collection.count()
            metadata = self.collection.metadata

            return {
                "collection_name": self.collection_name,
                "vector_count": count,
                "metadata": metadata,
            }

        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            raise
