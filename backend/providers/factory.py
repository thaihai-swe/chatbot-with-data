"""Factory functions for provider selection based on configuration."""

import logging
import os
from functools import lru_cache

from .base import BaseLLMProvider, BaseEmbeddingProvider
from .openai import OpenAILLMProvider, OpenAIEmbeddingProvider

logger = logging.getLogger(__name__)


@lru_cache()
def get_llm_provider() -> BaseLLMProvider:
    """Get LLM provider based on configuration.

    Returns:
        BaseLLMProvider instance

    Raises:
        ValueError: If provider type is unsupported
    """
    # Read provider type from environment or use default
    provider_type = os.getenv("LLM_PROVIDER", "openai").lower()

    logger.info(f"Initializing LLM provider: {provider_type}")

    from config import get_config
    
    if provider_type in ("openai", "openai-compatible"):
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE") if provider_type == "openai-compatible" else None
        model = get_config().llm.model
        timeout = 60

        return OpenAILLMProvider(
            api_key=api_key,
            api_base=api_base,
            model=model,
            timeout=timeout,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_type}")


@lru_cache()
def get_embedding_provider() -> BaseEmbeddingProvider:
    """Get embedding provider based on configuration.

    Returns:
        BaseEmbeddingProvider instance

    Raises:
        ValueError: If provider type is unsupported
    """
    # Read provider type from environment or use default
    provider_type = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

    logger.info(f"Initializing embedding provider: {provider_type}")

    from config import get_config
    
    if provider_type in ("openai", "openai-compatible"):
        api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("EMBEDDING_API_BASE") if provider_type == "openai-compatible" else None
        model = get_config().ingestion.embedding_model
        max_retries = 3
        timeout = 30

        return OpenAIEmbeddingProvider(
            api_key=api_key,
            api_base=api_base,
            model=model,
            max_retries=max_retries,
            timeout=timeout,
        )
    else:
        raise ValueError(f"Unsupported embedding provider: {provider_type}")

