from __future__ import annotations

from backend.chat.citations import CitationService

def test_provenance_match_metadata():
    service = CitationService()
    
    answer_text = "Revenue grew 15% in Q3 [Source 1].\n\nThis is an uncited paragraph."
    retrieved_chunks = [
        {"chunk_id": "c1", "document_id": "d1", "text": "The company reported that revenue grew 15% in Q3.", "title": "Report"}
    ]
    
    provenance = service.build_provenance(answer_text, retrieved_chunks)
    claims = provenance["claims"]
    
    assert len(claims) == 2
    
    cited_claim = claims[0]
    assert cited_claim["match_score"] > 0.0
    assert cited_claim["match_method"] == "jaccard"
    assert cited_claim["matched_chunk_id"] == "c1"
    
    uncited_claim = claims[1]
    assert uncited_claim["match_score"] == 0.0
    assert uncited_claim["match_method"] == "none"
    assert uncited_claim["matched_chunk_id"] is None
