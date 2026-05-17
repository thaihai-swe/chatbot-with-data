from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any

class VectorStore(ABC):
    """Abstract Base Class for vector database providers."""

    @abstractmethod
    def add_vectors(
        self,
        vectors_data: List[Tuple[str, List[float], Dict[str, Any]]],
    ) -> int:
        """
        Add multiple vectors to the index.

        Args:
            vectors_data: List of tuples (vector_id, embedding, metadata)

        Returns:
            Number of vectors added
        """
        pass

    @abstractmethod
    def query_hybrid(
        self,
        query_text: str,
        query_embedding: List[float],
        alpha: float = 0.5,
        k: int = 10,
        collection_ids: Optional[List[str]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Perform a hybrid search (keyword + semantic).

        Args:
            query_text: Raw query string for keyword search
            query_embedding: Query vector for semantic search
            alpha: Weight between keyword (0.0) and semantic (1.0) search
            k: Number of results to return
            collection_ids: Optional list of collection IDs to filter by

        Returns:
            List of (chunk_id, similarity_score, metadata) tuples
        """
        pass

    @abstractmethod
    def delete_by_document(self, document_id: str) -> int:
        """
        Delete all vectors for a specific document.

        Args:
            document_id: ID of document to delete

        Returns:
            Number of vectors deleted
        """
        pass

    @abstractmethod
    def delete_by_collection(self, collection_id: str) -> int:
        """
        Delete all vectors for a specific collection.

        Args:
            collection_id: ID of collection to delete

        Returns:
            Number of vectors deleted
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get total count of vectors in the store.

        Returns:
            Total count
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """
        Clear all data from the vector store.
        """
        pass
