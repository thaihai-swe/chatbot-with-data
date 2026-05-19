"""Service for generating grounded answers via LLM."""
from __future__ import annotations

import logging
import json
from typing import Optional, List, Dict, Any, Iterator

from fastapi import Depends
from providers.base import BaseLLMProvider
from providers.factory import get_llm_provider
from config import get_config

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for calling the LLM to generate answers."""

    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Initialize the generation service.

        Args:
            llm_provider: Provider for interacting with LLM.
        """
        self.llm_provider = llm_provider

    def generate_answer(
        self,
        context_package: Dict[str, Any],
        stream: bool | None = None,
    ) -> Any:
        """
        Generate an answer from the context package.

        Args:
            context_package: Package containing system prompt, history, and query
            stream: Whether to stream the response (defaults to config)

        Returns:
            If stream=False: The full response string
            If stream=True: An iterator of response tokens
        """
        config = get_config()
        effective_stream = stream if stream is not None else config.llm.streaming_enabled

        print(f"Context package for generation: {json.dumps(context_package, indent=2)}")
        messages = [
            {"role": "system", "content": context_package["system_prompt"]},
        ]

        # Add history
        messages.extend(context_package["history"])

        # Add current query
        messages.append({"role": "user", "content": context_package["current_query"]})

        logger.info(f"Generating answer using LLM provider (stream={effective_stream})")

        try:
            return self.llm_provider.generate_completion(
                messages,
                temperature=config.llm.temperature,
                stream=effective_stream
            )
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise


def get_generation_service(llm_provider: BaseLLMProvider = Depends(get_llm_provider)) -> GenerationService:
    """Factory function for GenerationService."""
    return GenerationService(llm_provider)
