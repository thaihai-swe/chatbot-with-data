from backend.chat.citations import CitationService, split_paragraphs
service = CitationService()
text = """Form 10-K deadline: - Version A: 60 days after fiscal year end. - Version B: 75 days after fiscal year end.

Chief Risk Officer reporting: - Version A: reports directly to board. - Version B: reports to CEO.

[Source 95dbd4b7-b02a-48ef-b037-a89e6b55320a - compliance_guide_conflict]"""

retrieved_chunks = [
    {
        "chunk_id": "chunk_1", 
        "document_id": "doc1", 
        "text": "Quarterly Filings - Form 10-Q due 40 days after quarter end. Annual Filings - Form 10-K due 60 days after fiscal year end."
    },
    {
        "chunk_id": "chunk_2", 
        "document_id": "doc1", 
        "text": "Chief Risk Officer reporting directly to board. Chief Risk Officer reporting to CEO."
    }
]

prov = service.build_provenance(text, retrieved_chunks)
for i, c in enumerate(prov["claims"]):
    print(f"Claim {i} cited: {c['cited']}")
    print(f"Text: {c['text']}")
