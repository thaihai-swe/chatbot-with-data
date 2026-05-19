"""Abstract base classes for LLM and embedding providers."""

from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, Optional, Union


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """Generate a completion from the LLM.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            temperature: Optional temperature for generation (0.0-2.0)
            stream: Whether to stream the response

        Returns:
            String for non-streaming, Iterator[str] for streaming
        """
        pass


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors, one per input text
        """
        pass

