import logging
import json
import time
from typing import List, Dict, Any, Tuple

from fastapi import Depends

from llm.client import LLMClient, get_llm_client
from chat.prompts import JUDGE_GROUNDEDNESS_PROMPT, JUDGE_RELEVANCE_PROMPT
from schemas.evaluation import JudgeMetric

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
            data = self._parse_json_response(response_text)
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
            data = self._parse_json_response(response_text)
            return JudgeMetric(
                score=data.get("score", 0.0),
                reason=data.get("reason", "Failed to parse judge response.")
            )
        except Exception as e:
            logger.error(f"Error in evaluate_relevance: {str(e)}")
            return JudgeMetric(score=0.0, reason=f"Evaluation error: {str(e)}")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from the LLM response, handling potential markdown blocks."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM response as JSON: {text}")
            # Try a very basic extraction if it failed
            if '"score":' in text and '"reason":' in text:
                try:
                    # Very crude fallback
                    score_start = text.find('"score":') + 8
                    score_end = text.find(',', score_start)
                    score = float(text[score_start:score_end].strip())
                    
                    reason_start = text.find('"reason":') + 9
                    reason_end = text.rfind('"')
                    reason = text[reason_start:reason_end].strip().strip('"')
                    return {"score": score, "reason": reason}
                except:
                    pass
            return {"score": 0.0, "reason": "Could not parse JSON from judge."}


def get_judge_service(llm_client: LLMClient = Depends(get_llm_client)) -> JudgeService:
    """Factory function for JudgeService."""
    return JudgeService(llm_client)
