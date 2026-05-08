"""Service for generating grounded answers via LLM."""
from __future__ import annotations

import logging
import json
from typing import Optional, List, Dict, Any, Iterator

from fastapi import Depends
from llm.client import LLMClient, get_llm_client

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
        stream: bool = False,
    ) -> Any:
        """
        Generate an answer from the context package.

        Args:
            context_package: Package containing system prompt, history, and query
            stream: Whether to stream the response

        Returns:
            If stream=False: The full response string
            If stream=True: An iterator of response tokens
        """
        messages = [
            {"role": "system", "content": context_package[""]},
        ]

        # Add history
        messages.extend(context_package["history"])

        # Add current query
        messages.append({"role": "user", "content": context_package["current_query"]})

        logger.info(f"Generating answer using LLMClient (stream={stream})")

        try:
            return self.llm_client.generate_completion(messages, stream=stream)
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise


def get_generation_service(llm_client: LLMClient = Depends(get_llm_client)) -> GenerationService:
    """Factory function for GenerationService."""
    return GenerationService(llm_client)
