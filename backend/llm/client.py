import logging
from typing import Optional, List, Dict, Any, Iterator, Union

from openai import OpenAI
from config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified client for interacting with Large Language Models."""
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        model: str = "gpt-4o",
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        
    def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """Generate a response from the LLM."""
        if stream:
            return self._generate_stream(messages, temperature)
        else:
            return self._generate_non_stream(messages, temperature)

    def _generate_non_stream(self, messages: List[Dict[str, str]], temperature: Optional[float]) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "timeout": self.timeout,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
            
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip() if response.choices[0].message.content else ""

    def _generate_stream(self, messages: List[Dict[str, str]], temperature: Optional[float]) -> Iterator[str]:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "timeout": self.timeout,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
            
        response = self.client.chat.completions.create(**kwargs)
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content


def get_llm_client() -> LLMClient:
    settings = get_settings()
    return LLMClient(
        api_key=settings.openai_api_key,
        api_base=settings.openai_api_base,
        model=settings.chat_model,
    )
