"""OpenAI provider implementations for LLM and embedding."""

import logging
import time
from typing import Dict, Iterator, List, Optional, Union

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai

from providers.base import BaseLLMProvider, BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 60,
    ):
        """Initialize OpenAI LLM provider.

        Args:
            api_key: OpenAI API key
            api_base: Optional custom API base URL (for OpenAI-compatible endpoints)
            model: Model name to use
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.timeout = timeout
        self.client = OpenAI(api_key=api_key, base_url=api_base, timeout=timeout)

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """Generate a completion from OpenAI.

        Args:
            messages: List of message dictionaries
            temperature: Optional temperature for generation
            stream: Whether to stream the response

        Returns:
            String for non-streaming, Iterator[str] for streaming
        """
        if stream:
            return self._generate_stream(messages, temperature)
        else:
            return self._generate_non_stream(messages, temperature)

    def _generate_non_stream(
        self, messages: List[Dict[str, str]], temperature: Optional[float]
    ) -> str:
        """Generate non-streaming completion."""
        from config import get_config
        model = get_config().llm.model
        kwargs = {"model": model, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature

        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        if isinstance(content, dict):
            import json
            content = json.dumps(content)
        return str(content).strip() if content else ""

    def _generate_stream(
        self, messages: List[Dict[str, str]], temperature: Optional[float]
    ) -> Iterator[str]:
        """Generate streaming completion."""
        from config import get_config
        model = get_config().llm.model
        kwargs = {"model": model, "messages": messages, "stream": True}
        if temperature is not None:
            kwargs["temperature"] = temperature

        stream = self.client.chat.completions.create(**kwargs)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


def _rate_limit_aware(max_retries: int = 3):
    """Decorator for retry logic with exponential backoff."""
    return retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError)),
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider implementation."""

    # Pricing per 1M tokens
    PRICING = {
        "text-embedding-3-small": 0.02,
        "text-embedding-3-large": 0.13,
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """Initialize OpenAI embedding provider.

        Args:
            api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
            api_base: Optional custom API base URL
            model: Model name (defaults to text-embedding-3-small)
            max_retries: Maximum number of retries for rate limit errors
            timeout: Request timeout in seconds
        """
        import os

        self.api_key = api_key or os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and EMBEDDING_API_KEY/OPENAI_API_KEY not set")

        self.api_base = api_base or os.getenv("EMBEDDING_API_BASE") or os.getenv("OPENAI_API_BASE")
        from config import get_config
        self.model = model or get_config().ingestion.embedding_model
        self.max_retries = max_retries
        self.timeout = timeout

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base, timeout=timeout)

        # Tracking statistics
        self.api_calls = 0
        self.failed_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0

    @_rate_limit_aware(max_retries=3)
    def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty or not a string
            openai.APIError: If API request fails after retries
        """
        if not isinstance(text, str):
            raise ValueError(f"Text must be a string, got {type(text)}")
        if not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            from config import get_config
            model = get_config().ingestion.embedding_model
            response = self.client.embeddings.create(input=[text], model=model)
            embedding = response.data[0].embedding

            # Track usage
            tokens = response.usage.total_tokens
            self.total_tokens += tokens
            self.total_cost += self._calculate_cost(tokens)
            self.api_calls += 1

            return embedding

        except (openai.RateLimitError, openai.APIError) as e:
            self.failed_calls += 1
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            self.failed_calls += 1
            logger.error(f"Unexpected error in embed: {e}")
            raise

    def embed_batch(self, texts: list[str], batch_size: int = 10) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch

        Returns:
            List of embedding vectors, one per input text

        Raises:
            ValueError: If any text is not a string
        """
        if not all(isinstance(t, str) for t in texts):
            raise ValueError("All texts must be strings")

        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                from config import get_config
                model = get_config().ingestion.embedding_model
                response = self.client.embeddings.create(input=batch, model=model)

                # Extract embeddings in order
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                # Track usage
                tokens = response.usage.total_tokens
                self.total_tokens += tokens
                self.total_cost += self._calculate_cost(tokens)
                self.api_calls += 1

            except (openai.RateLimitError, openai.APIError) as e:
                self.failed_calls += 1
                logger.error(f"OpenAI API error in batch: {e}")
                raise
            except Exception as e:
                self.failed_calls += 1
                logger.error(f"Unexpected error in embed_batch: {e}")
                raise

            # Add delay between batches to avoid rate limiting
            if i + batch_size < len(texts):
                time.sleep(0.1)

        return embeddings

    def _calculate_cost(self, tokens: int) -> float:
        """Calculate cost based on tokens and model pricing.

        Args:
            tokens: Number of tokens used

        Returns:
            Cost in dollars
        """
        from config import get_config
        model = get_config().ingestion.embedding_model
        price_per_million = self.PRICING.get(model, 0.0)
        return (tokens / 1_000_000) * price_per_million

    def get_stats(self) -> dict:
        """Get usage statistics.

        Returns:
            Dictionary with api_calls, failed_calls, total_tokens, total_cost, model
        """
        from config import get_config
        return {
            "api_calls": self.api_calls,
            "failed_calls": self.failed_calls,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "model": get_config().ingestion.embedding_model,
        }

    def reset_stats(self):
        """Reset all tracking statistics to zero."""
        self.api_calls = 0
        self.failed_calls = 0
        self.total_tokens = 0
        self.total_cost = 0.0
