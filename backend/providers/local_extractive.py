import re


class LocalExtractiveProvider:
    def _query_terms(self, question):
        return re.findall(r"[a-z0-9]+", (question or "").lower())

    def _candidate_sentences(self, chunk_text):
        return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+|\n+", chunk_text or "") if segment.strip()]

    def generate(self, question, packed_context, conversation_history=None):
        query_terms = set(self._query_terms(question))
        ranked_sentences = []
        for index, chunk in enumerate(packed_context):
            for sentence in self._candidate_sentences(chunk.get("full_text") or chunk.get("content_snippet")):
                score = sum(1 for term in query_terms if term in sentence.lower())
                if score <= 0:
                    continue
                ranked_sentences.append((score, index, sentence))
        ranked_sentences.sort(key=lambda item: (item[0], -item[1]), reverse=True)

        used_indices = []
        selected_sentences = []
        for _score, chunk_index, sentence in ranked_sentences:
            if chunk_index not in used_indices:
                used_indices.append(chunk_index)
            if sentence not in selected_sentences:
                selected_sentences.append(sentence)
            if len(selected_sentences) >= 3:
                break

        if not selected_sentences and packed_context:
            selected_sentences.append((packed_context[0].get("content_snippet") or "").strip())
            used_indices.append(0)

        answer_text = " ".join(selected_sentences).strip()
        if answer_text and not answer_text.endswith("."):
            answer_text += "."

        return {
            "answer_text": answer_text or "I could not extract a grounded answer from the provided context.",
            "citation_indices": used_indices or [0],
            "generation_metadata": {
                "model": "local-extractive-v1",
                "tokens_used": len(answer_text.split()),
                "finish_reason": "completed",
            },
        }
