"""Factory functions for provider selection based on configuration."""

import logging
from functools import lru_cache

from config import get_settings, get_config
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
    config = get_config()
    settings = get_settings()
    provider_type = config.llm.provider

    logger.info(f"Initializing LLM provider: {provider_type}")

    if provider_type in ("openai", "openai-compatible"):
        api_key = settings.openai_api_key
        api_base = settings.openai_api_base if provider_type == "openai-compatible" else None
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
    config = get_config()
    settings = get_settings()
    provider_type = config.ingestion.embedding_provider

    logger.info(f"Initializing embedding provider: {provider_type}")

    if provider_type in ("openai", "openai-compatible"):
        api_key = settings.embedding_api_key
        api_base = settings.embedding_api_base if provider_type == "openai-compatible" else None
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
