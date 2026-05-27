"""Multi-hop retrieval orchestrator for sequential iterative retrieval."""

from typing import List, Tuple, Optional
import logging

from schemas.chat import ReasoningChainTrace, ReasoningStep
from schemas.settings import RetrievalSettings

logger = logging.getLogger(__name__)


class MultiHopRetrievalOrchestrator:
    """Orchestrator for multi-hop reasoning with sequential sub-question execution."""

    def __init__(self, retrieval_service=None, llm_client=None):
        """Initialize the multi-hop orchestrator.

        Args:
            retrieval_service: Service for executing retrieval operations
            llm_client: LLM client for generating intermediate answers
        """
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client
        logger.info("MultiHopRetrievalOrchestrator initialized")

    def _should_use_multi_hop(self, sub_questions: List[str]) -> bool:
        """Detect if query needs multi-hop reasoning.

        Args:
            sub_questions: List of decomposed sub-questions

        Returns:
            True if multi-hop reasoning should be used (>1 sub-question), False otherwise
        """
        return len(sub_questions) > 1

    def _generate_intermediate_answer(
        self,
        sub_question: str,
        chunks: List[dict]
    ) -> str:
        """Generate intermediate answer from retrieved chunks.

        Args:
            sub_question: The sub-question being answered
            chunks: Retrieved chunks for this sub-question

        Returns:
            Concise intermediate answer (1-3 sentences)
        """
        if not chunks:
            return f"No relevant information found for: {sub_question}"

        # Build context from chunks
        chunk_texts = [c.get("text", c.get("content", "")) for c in chunks[:5]]  # Use top 5 chunks
        context = "\n".join(chunk_texts)

        # Build prompt for intermediate answer generation
        prompt = f"""Based on the following information, provide a concise answer (1-3 sentences) to the question.

Question: {sub_question}

Information:
{context}

Answer:"""

        try:
            # Call LLM to generate intermediate answer
            answer = self.llm_client.generate_completion([{"role": "user", "content": prompt}], stream=False)
            return answer.strip()
        except Exception as e:
            logger.error(f"Failed to generate intermediate answer: {e}")
            return f"Unable to generate answer for: {sub_question}"

    def _handle_step_failure(
        self,
        query: str,
        remaining_sub_questions: List[str],
        config: RetrievalSettings,
        collection_ids: List[str]
    ) -> List[dict]:
        """Handle failure by falling back to original query + remaining sub-questions.

        Args:
            query: Original user query
            remaining_sub_questions: Sub-questions that haven't been executed yet
            config: Advanced retrieval configuration
            collection_ids: Collection IDs to search

        Returns:
            Chunks retrieved using fallback strategy
        """
        logger.info("Executing fallback strategy: original query + remaining sub-questions")

        try:
            # Combine original query with remaining sub-questions
            fallback_query = query
            if remaining_sub_questions:
                fallback_query += "\n\nAdditional context: " + " ".join(remaining_sub_questions)

            # Execute retrieval with fallback query
            chunks, _ = self.retrieval_service.retrieve(
                query_text=fallback_query,
                config=config,
                collection_ids=collection_ids
            )
            return chunks

        except Exception as e:
            logger.error(f"Fallback retrieval failed: {e}")
            return []

    def _execute_sequential_retrieval(
        self,
        sub_questions: List[str],
        config: RetrievalSettings,
        collection_ids: List[str],
        max_hops: int,
        timeout_ms: int = 30000
    ) -> Tuple[List[dict], List[ReasoningStep]]:
        """Execute sub-questions sequentially, passing context forward.

        Args:
            sub_questions: List of sub-questions to execute
            config: Advanced retrieval configuration
            collection_ids: Collection IDs to search
            max_hops: Maximum number of hops to execute
            timeout_ms: Timeout in milliseconds (default: 30000)

        Returns:
            Tuple of (all_chunks, reasoning_steps)
        """
        import time

        start_time = time.time()
        timeout_seconds = timeout_ms / 1000.0
        all_chunks = []
        reasoning_steps = []
        context = ""  # Accumulated context from previous hops

        # Limit to max_hops
        questions_to_execute = sub_questions[:max_hops]

        for hop_number, sub_question in enumerate(questions_to_execute, start=1):
            # Check timeout before starting hop
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.warning(f"Timeout reached after {elapsed:.2f}s, stopping at hop {hop_number}")
                step = ReasoningStep(
                    hop_number=hop_number,
                    sub_question=sub_question,
                    retrieved_chunk_ids=[],
                    intermediate_answer=None,
                    latency_ms=0,
                    failure="Timeout exceeded"
                )
                reasoning_steps.append(step)
                break

            hop_start = time.time()

            # Contextualize sub-question with previous intermediate answers
            contextualized_question = sub_question
            if context:
                contextualized_question = f"{sub_question}\n\nContext from previous steps: {context}"

            try:
                # Execute retrieval for this sub-question
                chunks, _ = self.retrieval_service.retrieve(
                    query_text=contextualized_question,
                    config=config,
                    collection_ids=collection_ids
                )

                chunk_ids = [c.get("id", "") for c in chunks]
                all_chunks.extend(chunks)

                # Generate intermediate answer
                intermediate_answer = self._generate_intermediate_answer(sub_question, chunks)
                context += f"\n{intermediate_answer}"

                # Record this hop
                step = ReasoningStep(
                    hop_number=hop_number,
                    sub_question=sub_question,
                    retrieved_chunk_ids=chunk_ids,
                    intermediate_answer=intermediate_answer,
                    latency_ms=int((time.time() - hop_start) * 1000),
                    failure=None
                )
                reasoning_steps.append(step)

            except Exception as e:
                logger.error(f"Hop {hop_number} failed: {e}")
                step = ReasoningStep(
                    hop_number=hop_number,
                    sub_question=sub_question,
                    retrieved_chunk_ids=[],
                    intermediate_answer=None,
                    latency_ms=int((time.time() - hop_start) * 1000),
                    failure=str(e)
                )
                reasoning_steps.append(step)
                break  # Stop on failure

        return all_chunks, reasoning_steps

    def execute_multi_hop(
        self,
        query: str,
        sub_questions: List[str],
        config: RetrievalSettings,
        collection_ids: List[str]
    ) -> Tuple[List[dict], ReasoningChainTrace]:
        """Execute multi-hop reasoning with sequential sub-question retrieval.

        Args:
            query: Original user query
            sub_questions: List of decomposed sub-questions
            config: Advanced retrieval configuration
            collection_ids: Collection IDs to search

        Returns:
            Tuple of (final_chunks, reasoning_chain_trace)
        """
        import time
        start_time = time.time()

        logger.info(f"Starting multi-hop execution with {len(sub_questions)} sub-questions")

        # Check if multi-hop should be used
        if not self._should_use_multi_hop(sub_questions):
            logger.info("Single sub-question detected, skipping multi-hop")
            reasoning_chain = ReasoningChainTrace(
                hops=[],
                total_hops=0,
                fallback_triggered=False,
                fallback_reason="Single sub-question, no multi-hop needed",
                total_latency_ms=int((time.time() - start_time) * 1000)
            )
            return [], reasoning_chain

        # Execute sequential retrieval
        try:
            chunks, reasoning_steps = self._execute_sequential_retrieval(
                sub_questions=sub_questions,
                config=config,
                collection_ids=collection_ids,
                max_hops=config.max_hops,
                timeout_ms=config.multi_hop_timeout_ms
            )

            # Build reasoning chain trace
            reasoning_chain = ReasoningChainTrace(
                hops=reasoning_steps,
                total_hops=len(reasoning_steps),
                fallback_triggered=False,
                fallback_reason=None,
                total_latency_ms=int((time.time() - start_time) * 1000)
            )

            return chunks, reasoning_chain

        except Exception as e:
            logger.error(f"Multi-hop execution failed: {e}")
            reasoning_chain = ReasoningChainTrace(
                hops=[],
                total_hops=0,
                fallback_triggered=True,
                fallback_reason=f"Multi-hop execution error: {str(e)}",
                total_latency_ms=int((time.time() - start_time) * 1000)
            )
            return [], reasoning_chain
