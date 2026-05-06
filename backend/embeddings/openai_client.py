import os
import time
import logging
from typing import Optional
from functools import wraps

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


def _rate_limit_aware(max_retries: int = 3):
    """Decorator for rate-limit aware API calls."""
    def decorator(func):
        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type((openai.RateLimitError, openai.APIError)),
            reraise=True,
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


class OpenAIEmbeddingClient:
    """Client for generating embeddings using OpenAI API."""

    # Pricing per 1K tokens (as of May 2026, approximate)
    EMBEDDING_COSTS = {
        "text-embedding-3-small": 0.00002,  # $0.02 per 1M tokens
        "text-embedding-3-large": 0.00013,  # $0.13 per 1M tokens
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: str = "text-embedding-3-small",
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize OpenAI embedding client.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            api_base: Optional custom API base URL
            model: Embedding model to use
            max_retries: Max retries for transient errors
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Set it or pass api_key to OpenAIEmbeddingClient."
            )

        openai.api_key = self.api_key
        if api_base:
            openai.api_base = api_base
        
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout

        # Track statistics
        self.total_tokens = 0
        self.total_cost = 0.0
        self.api_calls = 0
        self.failed_calls = 0

    @_rate_limit_aware(max_retries=3)
    def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats)

        Raises:
            ValueError: If text is empty or invalid
            openai.APIError: If API call fails after retries
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty after stripping whitespace")

        try:
            response = openai.Embedding.create(
                input=text,
                model=self.model,
                request_timeout=self.timeout,
            )

            # Extract embedding
            embedding = response["data"][0]["embedding"]

            # Track usage
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            self.total_tokens += tokens_used
            self.api_calls += 1

            # Calculate and track cost
            cost = self._calculate_cost(tokens_used)
            self.total_cost += cost

            logger.info(
                f"Embedding generated: model={self.model}, tokens={tokens_used}, "
                f"cost=${cost:.6f}, total_cost=${self.total_cost:.6f}"
            )

            return embedding

        except openai.RateLimitError as e:
            self.failed_calls += 1
            logger.warning(f"Rate limited: {str(e)}. Retrying...")
            raise
        except openai.APIError as e:
            self.failed_calls += 1
            logger.error(f"API error: {str(e)}")
            raise
        except Exception as e:
            self.failed_calls += 1
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """
        Generate embeddings for multiple texts with batch processing.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts is empty or invalid
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        if not all(isinstance(t, str) for t in texts):
            raise ValueError("All texts must be strings")

        embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                response = openai.Embedding.create(
                    input=batch,
                    model=self.model,
                    request_timeout=self.timeout,
                )

                # Extract embeddings in original order
                batch_embeddings = [item["embedding"] for item in response["data"]]
                embeddings.extend(batch_embeddings)

                # Track usage
                tokens_used = response.get("usage", {}).get("total_tokens", 0)
                self.total_tokens += tokens_used
                self.api_calls += 1

                # Calculate and track cost
                cost = self._calculate_cost(tokens_used)
                self.total_cost += cost

                logger.info(
                    f"Batch embedding generated: batch_size={len(batch)}, "
                    f"tokens={tokens_used}, cost=${cost:.6f}"
                )

                # Add small delay between batches to avoid rate limiting
                if i + batch_size < len(texts):
                    time.sleep(0.1)

            except openai.RateLimitError as e:
                self.failed_calls += 1
                logger.warning(f"Rate limited on batch {i//batch_size}: {str(e)}. Retrying...")
                raise
            except openai.APIError as e:
                self.failed_calls += 1
                logger.error(f"API error on batch {i//batch_size}: {str(e)}")
                raise

        return embeddings

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost for tokens used."""
        if self.model not in self.EMBEDDING_COSTS:
            logger.warning(f"Unknown model {self.model}, unable to calculate cost")
            return 0.0

        cost_per_token = self.EMBEDDING_COSTS[self.model]
        return (tokens / 1000) * cost_per_token

    def get_stats(self) -> dict:
        """Get embedding statistics."""
        return {
            "api_calls": self.api_calls,
            "failed_calls": self.failed_calls,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "model": self.model,
        }

    def reset_stats(self):
        """Reset tracking statistics."""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.api_calls = 0
        self.failed_calls = 0

    @staticmethod
    def validate_embedding_dimension(embedding: list[float], expected_dim: int = 1536) -> bool:
        """
        Validate embedding dimension.

        Args:
            embedding: Embedding vector
            expected_dim: Expected dimension (default for text-embedding-3-small is 1536)

        Returns:
            True if valid, False otherwise
        """
        return isinstance(embedding, list) and len(embedding) == expected_dim
