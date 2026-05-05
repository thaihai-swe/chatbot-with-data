from backend.providers.local_extractive import LocalExtractiveProvider
from backend.providers.openai_responses import OpenAIResponsesProvider



class ResponseGenerationService:
    def __init__(
        self,
        provider_name="openai-responses-v1",
        openai_api_key=None,
        openai_model="gpt-5.5",
        openai_base_url=None,
        openai_reasoning_effort="low",
    ):
        self.provider_name = provider_name

        if provider_name == "local-extractive-v1":
            self.provider = LocalExtractiveProvider()
        elif provider_name == "openai-responses-v1":
            self.provider = OpenAIResponsesProvider(
                api_key=openai_api_key,
                model=openai_model,
                base_url=openai_base_url,
                reasoning_effort=openai_reasoning_effort,
            )
        else:
            raise ValueError(f"Unsupported generation provider: {provider_name}")

    def generate(self, question, packed_context, conversation_history=None):
        return self.provider.generate(question, packed_context, conversation_history=conversation_history)

    def stream_answer_chunks(self, answer_text, chunk_size=40):
        text = answer_text or ""
        for start in range(0, len(text), chunk_size):
            yield text[start : start + chunk_size]
