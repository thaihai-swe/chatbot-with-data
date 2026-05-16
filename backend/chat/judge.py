import logging
import json
import time
from typing import List, Dict, Any, Tuple

from fastapi import Depends

from llm.client import LLMClient, get_llm_client
from chat.prompts import JUDGE_GROUNDEDNESS_PROMPT, JUDGE_RELEVANCE_PROMPT
from schemas.evaluation import JudgeMetric
from chat.utils import parse_json_from_llm

logger = logging.getLogger(__name__)


class JudgeService:
    """Service for evaluating AI responses using LLM-as-a-judge."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def evaluate_groundedness(self, answer_text: str, retrieved_chunks: List[Dict[str, Any]]) -> JudgeMetric:
        """Evaluate how grounded the answer is in the retrieved chunks."""
        context_string = "\n\n".join([
            f"Source {i+1}:\n{c.get('text', c.get('content', ''))}"
            for i, c in enumerate(retrieved_chunks)
        ])

        prompt = JUDGE_GROUNDEDNESS_PROMPT.format(
            context_string=context_string,
            answer_text=answer_text
        )

        try:
            response_text = self.llm_client.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0  # Use 0 for more consistent evaluation
            )
            data = parse_json_from_llm(response_text)
            if not isinstance(data, dict):
                data = {}
            return JudgeMetric(
                score=data.get("score", 0.0),
                reason=data.get("reason", "Failed to parse judge response.")
            )
        except Exception as e:
            logger.error(f"Error in evaluate_groundedness: {str(e)}")
            return JudgeMetric(score=0.0, reason=f"Evaluation error: {str(e)}")

    def evaluate_relevance(self, query_text: str, answer_text: str) -> JudgeMetric:
        """Evaluate how relevant the answer is to the user query."""
        prompt = JUDGE_RELEVANCE_PROMPT.format(
            query_text=query_text,
            answer_text=answer_text
        )

        try:
            response_text = self.llm_client.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            data = parse_json_from_llm(response_text)
            if not isinstance(data, dict):
                data = {}
            return JudgeMetric(
                score=data.get("score", 0.0),
                reason=data.get("reason", "Failed to parse judge response.")
            )
        except Exception as e:
            logger.error(f"Error in evaluate_relevance: {str(e)}")
            return JudgeMetric(score=0.0, reason=f"Evaluation error: {str(e)}")


def get_judge_service(llm_client: LLMClient = Depends(get_llm_client)) -> JudgeService:
    """Factory function for JudgeService."""
    return JudgeService(llm_client)
