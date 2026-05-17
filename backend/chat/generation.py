"""Service for generating grounded answers via LLM."""
from __future__ import annotations

import logging
import json
from typing import Optional, List, Dict, Any, Iterator

from fastapi import Depends
from llm.client import LLMClient, get_llm_client
from config import get_config

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for calling the LLM to generate answers."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the generation service.

        Args:
            llm_client: Unified client for interacting with LLM.
        """
        self.llm_client = llm_client

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

        logger.info(f"Generating answer using LLMClient (stream={effective_stream})")

        try:
            return self.llm_client.generate_completion(
                messages, 
                temperature=config.llm.temperature,
                stream=effective_stream
            )
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise


def get_generation_service(llm_client: LLMClient = Depends(get_llm_client)) -> GenerationService:
    """Factory function for GenerationService."""
    return GenerationService(llm_client)
