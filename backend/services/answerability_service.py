class AnswerabilityService:
    def __init__(
        self,
        min_similarity_threshold=0.5,
        min_chunk_count=1,
        min_query_overlap=0.15,
        consistency_threshold=0.8,
    ):
        self.min_similarity_threshold = min_similarity_threshold
        self.min_chunk_count = min_chunk_count
        self.min_query_overlap = min_query_overlap
        self.consistency_threshold = consistency_threshold

    def _detect_conflict(self, chunks):
        number_pattern = __import__("re").compile(
            r"\b(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b"
        )
        statements = []
        for chunk in chunks[:3]:
            snippet = (chunk.get("full_text") or "").lower()
            statements.append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "has_yes": " yes " in f" {snippet} ",
                    "has_no": " no " in f" {snippet} ",
                    "numbers": set(number_pattern.findall(snippet)),
                }
            )
        yes_present = any(item["has_yes"] for item in statements)
        no_present = any(item["has_no"] for item in statements)
        if yes_present and no_present:
            return True
        numbers = [item["numbers"] for item in statements if item["numbers"]]
        if len(numbers) >= 2:
            unique = set()
            for item in numbers:
                unique.update(item)
            if len(unique) > 1:
                return True
        return False

    def evaluate(self, question, retrieved_chunks):
        if not retrieved_chunks:
            return {
                "answerable": False,
                "answerability_score": 0.0,
                "reason_category": "no_relevant_evidence",
                "supporting_metrics": {
                    "top_similarity": 0.0,
                    "chunk_count": 0,
                    "query_overlap": 0.0,
                    "consistency_score": 0.0,
                },
            }

        top_similarity = max(chunk.get("retrieval_score", 0.0) or 0.0 for chunk in retrieved_chunks)
        chunk_count = len(retrieved_chunks)
        average_overlap = sum(chunk.get("query_overlap", 0.0) for chunk in retrieved_chunks) / max(1, chunk_count)
        conflicting = self._detect_conflict(retrieved_chunks)
        consistency_score = 0.0 if conflicting else 1.0

        if average_overlap < self.min_query_overlap:
            reason = "out_of_domain"
            answerable = False
        elif conflicting:
            reason = "conflicting_evidence"
            answerable = False
        elif top_similarity < self.min_similarity_threshold:
            reason = "low_confidence"
            answerable = False
        elif chunk_count < self.min_chunk_count:
            reason = "insufficient_support"
            answerable = False
        else:
            reason = None
            answerable = True

        answerability_score = round(
            min(
                1.0,
                (top_similarity * 0.5)
                + (min(chunk_count, 3) / 3 * 0.2)
                + (average_overlap * 0.2)
                + (consistency_score * 0.1),
            ),
            4,
        )

        return {
            "answerable": answerable,
            "answerability_score": answerability_score,
            "reason_category": reason,
            "supporting_metrics": {
                "top_similarity": round(top_similarity, 4),
                "chunk_count": chunk_count,
                "query_overlap": round(average_overlap, 4),
                "consistency_score": round(consistency_score, 4),
            },
        }
