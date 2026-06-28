"""Service for generating grounded answers via LLM."""
from __future__ import annotations

import logging
import json
from typing import Optional, List, Dict, Any, Iterator

from fastapi import Depends
from providers.base import BaseLLMProvider
from providers.factory import get_llm_provider
from config import get_config
from chat.prompts import (
    get_grounded_system_prompt,
    get_factual_system_prompt,
    get_comparison_system_prompt,
    get_how_to_system_prompt,
    get_troubleshooting_system_prompt,
    get_exploratory_system_prompt
)

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
        intent: Optional[str] = None,
    ) -> Any:
        """
        Generate an answer from the context package.

        Args:
            context_package: Package containing system prompt, history, and query
            stream: Whether to stream the response (defaults to config)
            intent: Detected query intent classification

        Returns:
            If stream=False: The full response string
            If stream=True: An iterator of response tokens
        """
        config = get_config()
        effective_stream = stream if stream is not None else config.llm.streaming_enabled

        logger.debug(f"Context package for generation: {json.dumps(context_package, indent=2)}")
        
        context_string = context_package.get("context_string", "")
        if intent == "factual":
            system_prompt = get_factual_system_prompt(context_string)
        elif intent == "comparison":
            system_prompt = get_comparison_system_prompt(context_string)
        elif intent == "how_to":
            system_prompt = get_how_to_system_prompt(context_string)
        elif intent == "troubleshooting":
            system_prompt = get_troubleshooting_system_prompt(context_string)
        elif intent == "exploratory":
            system_prompt = get_exploratory_system_prompt(context_string)
        else:
            system_prompt = get_grounded_system_prompt(context_string)

        messages = [
            {"role": "system", "content": system_prompt},
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
