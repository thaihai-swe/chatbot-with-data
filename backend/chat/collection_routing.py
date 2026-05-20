"""Collection routing service for automatic collection selection."""

from typing import List, Optional, Tuple, Dict, Any
import logging

from schemas.chat import CollectionRoutingTrace
from database import get_connection

logger = logging.getLogger(__name__)


class CollectionRoutingService:
    """Service for routing queries to relevant collections using LLM-based analysis."""

    def __init__(self, llm_client=None, db_session=None):
        """Initialize the collection routing service.

        Args:
            llm_client: LLM client for routing decisions
            db_session: Database session for collection metadata retrieval
        """
        self.llm_client = llm_client
        self.db_session = db_session
        logger.info("CollectionRoutingService initialized")

    def _get_collections(self) -> List[Dict[str, Any]]:
        """Fetch all collections with id, name, description from database.

        Returns:
            List of collection dictionaries with id, name, description fields
        """
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, name, description
                FROM collections
                WHERE deleted_at IS NULL
                ORDER BY created_at ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def _build_routing_prompt(self, query: str, collections: List[Dict[str, Any]]) -> str:
        """Build a structured prompt for LLM-based collection routing.

        Args:
            query: User query text
            collections: List of collection dictionaries with id, name, description

        Returns:
            Formatted prompt string for the LLM
        """
        collections_text = "\n".join(
            f"- ID: {c['id']}, Name: {c['name']}, Description: {c.get('description') or 'No description'}"
            for c in collections
        )

        prompt = f"""You are a collection routing assistant. Given a user query and a list of available collections, determine which collection(s) are most relevant to answer the query.

Available Collections:
{collections_text}

User Query: {query}

Task:
1. Analyze the query and determine which collection(s) would best answer it
2. Return the collection IDs that are relevant
3. Provide a confidence score (0.0-1.0) for your routing decision
4. Explain your reasoning

Format your response as JSON with the following structure:
{{
  "collection_ids": ["id1", "id2"],
  "confidence": 0.85,
  "reasoning": "Brief explanation of why these collections were selected"
}}

If no collections are relevant or you're uncertain, return an empty collection_ids list and low confidence."""

        return prompt

    def route_query(self, query: str, max_collections: int = 3) -> Tuple[List[str], Dict[str, Any]]:
        """Route query to relevant collections using LLM.

        Args:
            query: User query text
            max_collections: Maximum collections to return

        Returns:
            Tuple of (collection_ids, parsed_response_dict)
        """
        import json
        import time

        start_time = time.time()

        # Get collections
        collections = self._get_collections()

        # Build prompt
        prompt = self._build_routing_prompt(query, collections)

        # Call LLM
        response_text = self.llm_client(prompt)

        # Parse JSON response
        try:
            response_data = json.loads(response_text)
            collection_ids = response_data.get("collection_ids", [])[:max_collections]
            confidence = response_data.get("confidence", 0.0)
            reasoning = response_data.get("reasoning", "")
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            collection_ids = []
            confidence = 0.0
            reasoning = f"Parse error: {str(e)}"

        latency_ms = int((time.time() - start_time) * 1000)

        return collection_ids, {
            "confidence": confidence,
            "reasoning": reasoning,
            "latency_ms": latency_ms
        }

    def route_to_collections(
        self,
        query: str,
        confidence_threshold: float = 0.7,
        max_collections: int = 3
    ) -> Tuple[List[str], CollectionRoutingTrace]:
        """Route a query to relevant collection(s).

        Args:
            query: User query text
            confidence_threshold: Minimum confidence to use routing (default: 0.7)
            max_collections: Maximum number of collections to return (default: 3)

        Returns:
            Tuple of (collection_ids, routing_trace)
            - If confidence >= threshold: returns selected collection IDs
            - If confidence < threshold: returns empty list (fallback to all collections)
        """
        import time
        start_time = time.time()

        try:
            # Call route_query to get LLM routing decision
            collection_ids, response_data = self.route_query(query, max_collections)
            confidence = response_data.get("confidence", 0.0)
            reasoning = response_data.get("reasoning", "")

            # Apply confidence threshold
            if confidence >= confidence_threshold:
                # Use routing decision
                trace = CollectionRoutingTrace(
                    routing_decision=collection_ids,
                    confidence=confidence,
                    reasoning=reasoning,
                    fallback_reason=None,
                    latency_ms=int((time.time() - start_time) * 1000)
                )
                return collection_ids, trace
            else:
                # Fall back to all collections (empty list signals fallback)
                trace = CollectionRoutingTrace(
                    routing_decision=[],
                    confidence=confidence,
                    reasoning=reasoning,
                    fallback_reason=f"Confidence {confidence:.2f} below threshold {confidence_threshold}",
                    latency_ms=int((time.time() - start_time) * 1000)
                )
                return [], trace

        except Exception as e:
            logger.error(f"Error in route_to_collections: {e}")
            trace = CollectionRoutingTrace(
                routing_decision=[],
                confidence=0.0,
                reasoning="",
                fallback_reason=f"Routing error: {str(e)}",
                latency_ms=int((time.time() - start_time) * 1000)
            )
            return [], trace
