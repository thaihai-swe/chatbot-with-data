from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from backend.chat.conflict import ConflictDetectionService

def test_conflict_threshold():
    mock_llm = MagicMock()
    # Mock LLM returning conflict_score=0.7
    mock_llm.generate_completion.return_value = '{"conflict_score": 0.7, "surfaced_correctly": true, "conflict_details": "Some details"}'
    
    service = ConflictDetectionService(mock_llm)
    
    # Test with threshold 0.8 -> has_conflict=False
    service.conflict_score_threshold = 0.8
    result_high_thresh = service.detect_conflict("answer", [{"text": "chunk"}])
    assert result_high_thresh["has_conflict"] is False
    assert result_high_thresh["conflict_score"] == 0.7
    
    # Test with threshold 0.6 -> has_conflict=True
    service.conflict_score_threshold = 0.6
    result_low_thresh = service.detect_conflict("answer", [{"text": "chunk"}])
    assert result_low_thresh["has_conflict"] is True
    assert result_low_thresh["conflict_score"] == 0.7
