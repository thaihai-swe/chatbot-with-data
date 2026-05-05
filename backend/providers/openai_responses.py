import json
import re

from openai import OpenAI


class OpenAIResponsesProvider:
    def __init__(self, api_key=None, model="gpt-5.5", base_url=None, reasoning_effort="low"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.reasoning_effort = reasoning_effort
        self._client = None

    def _client_instance(self):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured for the OpenAI generation provider.")
        if self._client is None:
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def _developer_instructions(self):
        return (
            "You are a grounded question answering assistant for a RAG system. "
            "Answer only from the provided context chunks. "
            "Do not use outside knowledge. "
            "Return valid JSON with keys `answer_text` and `citation_indices`. "
            "`citation_indices` must be an array of zero-based chunk indexes that support the answer. "
            "If one chunk is enough, return one index. "
            "Do not wrap the JSON in markdown fences."
        )

    def _history_block(self, conversation_history):
        lines = []
        for message in conversation_history or []:
            content = (message.get("content") or "").strip()
            if not content:
                continue
            lines.append(f"{message.get('role', 'user').title()}: {content}")
        return "\n".join(lines) if lines else "No prior conversation history."

    def _user_prompt(self, question, packed_context, conversation_history=None):
        context_lines = []
        for index, chunk in enumerate(packed_context):
            context_lines.append(
                "\n".join(
                    [
                        f"[Chunk {index}]",
                        f"document_id: {chunk.get('document_id')}",
                        f"document_title: {chunk.get('document_title') or ''}",
                        f"chunk_id: {chunk.get('chunk_id')}",
                        f"page_or_section: {chunk.get('page_or_section') or ''}",
                        f"content: {chunk.get('full_text') or chunk.get('content_snippet') or ''}",
                    ]
                )
            )
        context_block = "\n\n".join(context_lines) if context_lines else "[No context chunks provided]"
        return (
            f"Recent conversation history:\n{self._history_block(conversation_history)}\n\n"
            f"Current question:\n{question}\n\n"
            f"Context chunks:\n{context_block}"
        )

    def _parse_json_output(self, output_text, packed_context):
        text = (output_text or "").strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z0-9_-]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return {
                    "answer_text": text,
                    "citation_indices": [0] if packed_context else [],
                }
            parsed = json.loads(match.group(0))

        answer_text = str(parsed.get("answer_text") or "").strip()
        citation_indices = parsed.get("citation_indices") or []
        valid_indices = []
        for value in citation_indices:
            if isinstance(value, int) and 0 <= value < len(packed_context) and value not in valid_indices:
                valid_indices.append(value)
        if not answer_text:
            answer_text = text
        if not valid_indices and packed_context:
            valid_indices = [0]
        return {
            "answer_text": answer_text,
            "citation_indices": valid_indices,
        }

    def generate(self, question, packed_context, conversation_history=None):
        response = self._client_instance().responses.create(
            model=self.model,
            reasoning={"effort": self.reasoning_effort},
            instructions=self._developer_instructions(),
            input=self._user_prompt(question, packed_context, conversation_history=conversation_history),
        )
        parsed = self._parse_json_output(response.output_text, packed_context)
        usage = getattr(response, "usage", None)
        token_count = 0
        if usage:
            token_count = getattr(usage, "total_tokens", None) or getattr(usage, "output_tokens", None) or 0
        if not token_count:
            token_count = len(parsed["answer_text"].split())
        return {
            "answer_text": parsed["answer_text"],
            "citation_indices": parsed["citation_indices"],
            "generation_metadata": {
                "model": self.model,
                "tokens_used": token_count,
                "finish_reason": "completed",
                "provider": "openai-responses-v1",
                "response_id": getattr(response, "id", None),
            },
        }
