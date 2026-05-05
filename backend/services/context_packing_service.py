class ContextPackingService:
    def __init__(self, token_budget=200):
        self.token_budget = token_budget

    def estimate_tokens(self, text):
        return len((text or "").split())

    def pack(self, chunks, token_budget=None, strategy="greedy"):
        budget = token_budget or self.token_budget
        selected = []
        used = 0
        for chunk in sorted(chunks, key=lambda item: item.get("retrieval_score", 0.0), reverse=True):
            chunk_tokens = self.estimate_tokens(chunk.get("full_text") or chunk.get("content_snippet"))
            if selected and used + chunk_tokens > budget:
                continue
            if not selected and chunk_tokens > budget:
                selected.append({**chunk, "estimated_tokens": chunk_tokens})
                used = min(chunk_tokens, budget)
                break
            selected.append({**chunk, "estimated_tokens": chunk_tokens})
            used += chunk_tokens
            if used >= budget:
                break
        return {
            "selected_chunks": selected,
            "total_tokens": used,
            "budget_remaining": max(0, budget - used),
            "strategy": strategy,
        }
