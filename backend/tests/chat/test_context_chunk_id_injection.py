def test_context_chunk_id_injection():
    from backend.chat.context import ContextService

    service = ContextService()
    chunks = [
        {"chunk_id": "abc-123-def", "title": "Doc Title", "page_number": 5, "text": "This is content"},
        {"chunk_id": "xyz-987-uvw", "title": "Another Doc", "text": "More content"}
    ]
    
    result = service.assemble_context(
        query_text="What is this?",
        retrieved_chunks=chunks,
        chat_history=[]
    )
    
    context_str = result["context_string"]
    
    assert "[Source abc-123-def]" in context_str
    assert "Title: Doc Title" in context_str
    assert "Page: 5" in context_str
    assert "Content: This is content" in context_str
    
    assert "[Source xyz-987-uvw]" in context_str
    assert "Title: Another Doc" in context_str
    assert "Page: N/A" in context_str
    assert "Content: More content" in context_str
