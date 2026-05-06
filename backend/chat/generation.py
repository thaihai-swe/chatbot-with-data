"""Service for generating grounded answers via LLM."""
from __future__ import annotations

import logging
import json
from typing import Optional, List, Dict, Any, Iterator

import openai
from config import get_settings

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for calling the LLM to generate answers."""

    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 60,
    ):
        """
        Initialize the generation service.

        Args:
            api_key: OpenAI API key
            api_base: Optional custom API base URL (e.g. for local LLM)
            model: Chat model to use
            timeout: API timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        openai.api_key = api_key
        if api_base:
            openai.api_base = api_base

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
            {"role": "system", "content": context_package["system_prompt"]},
        ]
        
        # Add history
        messages.extend(context_package["history"])
        
        # Add current query
        messages.append({"role": "user", "content": context_package["current_query"]})

        logger.info(f"Generating answer using model={self.model} (stream={stream})")

        try:
            if stream:
                return self._generate_stream(messages)
            else:
                return self._generate_non_stream(messages)
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def _generate_non_stream(self, messages: List[Dict[str, str]]) -> str:
        """Internal method for non-streaming generation."""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            request_timeout=self.timeout,
        )
        answer = response.choices[0].message.content
        logger.debug(f"Generation complete. Length: {len(answer)}")
        return answer

    def _generate_stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """Internal method for streaming generation."""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            stream=True,
            request_timeout=self.timeout,
        )
        for chunk in response:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]


def get_generation_service() -> GenerationService:
    """Factory function for GenerationService."""
    settings = get_settings()
    return GenerationService(
        api_key=settings.openai_api_key,
        api_base=settings.openai_api_base,
        model=settings.chat_model,
    )
