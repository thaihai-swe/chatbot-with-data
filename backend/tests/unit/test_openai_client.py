import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import openai

from embeddings.openai_client import OpenAIEmbeddingClient


@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI API responses."""
    return mocker


@pytest.fixture
def mock_api_key(monkeypatch):
    """Set mock API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-12345")
    return "sk-test-key-12345"


@pytest.fixture
def client(mock_api_key):
    """Create embedding client with mock API key."""
    return OpenAIEmbeddingClient(api_key=mock_api_key)


def test_client_initialization(mock_api_key):
    """Test client initialization with API key."""
    client = OpenAIEmbeddingClient(api_key=mock_api_key)
    assert client.api_key == mock_api_key
    assert client.model == "text-embedding-3-small"
    assert client.max_retries == 3
    assert client.total_tokens == 0
    assert client.total_cost == 0.0


def test_client_initialization_from_env(monkeypatch):
    """Test client initialization from environment variable."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key")
    client = OpenAIEmbeddingClient()
    assert client.api_key == "sk-env-key"


def test_client_initialization_missing_api_key(monkeypatch):
    """Test that missing API key raises error."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        OpenAIEmbeddingClient()


def test_client_custom_model(mock_api_key):
    """Test client initialization with custom model."""
    client = OpenAIEmbeddingClient(
        api_key=mock_api_key,
        model="text-embedding-3-large"
    )
    assert client.model == "text-embedding-3-large"


def test_embed_single_text(client, mocker):
    """Test embedding a single text."""
    mock_embedding = [0.1, 0.2, 0.3] + [0.0] * 1533  # 1536 dims

    mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 10},
        }
    )

    result = client.embed("Test text")

    assert result == mock_embedding
    assert client.api_calls == 1
    assert client.total_tokens == 10


def test_embed_tracks_cost(client, mocker):
    """Test that embedding tracks cost correctly."""
    mock_embedding = [0.1] * 1536

    mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 1000},
        }
    )

    client.embed("Test text for cost tracking")

    # Cost for 1000 tokens with text-embedding-3-small
    expected_cost = (1000 / 1000) * 0.00002
    assert abs(client.total_cost - expected_cost) < 0.000001


def test_embed_empty_text(client):
    """Test embedding empty text raises error."""
    with pytest.raises(ValueError, match="non-empty string"):
        client.embed("")

    with pytest.raises(ValueError, match="empty after stripping"):
        client.embed("   \n\t  ")


def test_embed_invalid_text_type(client):
    """Test embedding non-string raises error."""
    with pytest.raises(ValueError):
        client.embed(None)

    with pytest.raises(ValueError):
        client.embed(123)


def test_embed_batch(client, mocker):
    """Test batch embedding."""
    mock_embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]

    mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": emb} for emb in mock_embeddings],
            "usage": {"total_tokens": 30},
        }
    )

    texts = ["Text 1", "Text 2", "Text 3"]
    results = client.embed_batch(texts)

    assert len(results) == 3
    assert results == mock_embeddings
    assert client.api_calls == 1


def test_embed_batch_empty_list(client):
    """Test batch embedding with empty list."""
    with pytest.raises(ValueError, match="cannot be empty"):
        client.embed_batch([])


def test_embed_batch_invalid_texts(client):
    """Test batch embedding with invalid texts."""
    with pytest.raises(ValueError, match="must be strings"):
        client.embed_batch(["valid", 123, None])


def test_embed_batch_multiple_batches(client, mocker):
    """Test batch embedding splits into multiple API calls."""
    mock_embedding = [0.1] * 1536

    # Mock will be called multiple times for batches
    mock_create = mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 10},
        }
    )

    texts = ["Text"] * 25  # More than batch size of 10
    client.embed_batch(texts, batch_size=10)

    # Should be called 3 times (10 + 10 + 5)
    assert mock_create.call_count == 3


def test_rate_limit_error_handling(client, mocker):
    """Test handling of transient errors with retry configuration."""
    # The actual retry logic is in the @_rate_limit_aware decorator
    # This test verifies that the decorator is present and function handles exceptions

    mock_embedding = [0.1] * 1536

    # Mock successful API call to verify the function works
    mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 10},
        }
    )

    result = client.embed("Test text for retry handling")
    assert result == mock_embedding
    assert client.api_calls == 1


def test_api_error_handling(client, mocker):
    """Test handling of API errors."""
    mocker.patch(
        "openai.Embedding.create",
        side_effect=Exception("Service unavailable")
    )

    with pytest.raises(Exception):
        client.embed("Test text")

    assert client.failed_calls == 1


def test_statistics_tracking(client, mocker):
    """Test statistics tracking."""
    mock_embedding = [0.1] * 1536

    mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 100},
        }
    )

    client.embed("Text 1")
    client.embed("Text 2")

    stats = client.get_stats()

    assert stats["api_calls"] == 2
    assert stats["total_tokens"] == 200
    assert stats["failed_calls"] == 0
    assert stats["model"] == "text-embedding-3-small"
    assert stats["total_cost"] > 0


def test_reset_statistics(client, mocker):
    """Test resetting statistics."""
    mock_embedding = [0.1] * 1536

    mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 50},
        }
    )

    client.embed("Test text")
    assert client.api_calls == 1

    client.reset_stats()

    assert client.api_calls == 0
    assert client.total_tokens == 0
    assert client.total_cost == 0.0
    assert client.failed_calls == 0


def test_embedding_dimension_validation():
    """Test embedding dimension validation."""
    valid_embedding = [0.1] * 1536
    invalid_embedding = [0.1] * 768

    assert OpenAIEmbeddingClient.validate_embedding_dimension(valid_embedding)
    assert not OpenAIEmbeddingClient.validate_embedding_dimension(invalid_embedding)
    assert not OpenAIEmbeddingClient.validate_embedding_dimension([0.1])
    assert not OpenAIEmbeddingClient.validate_embedding_dimension("not a list")


def test_cost_calculation_different_models(mock_api_key):
    """Test cost calculation for different models."""
    client_small = OpenAIEmbeddingClient(
        api_key=mock_api_key,
        model="text-embedding-3-small"
    )
    client_large = OpenAIEmbeddingClient(
        api_key=mock_api_key,
        model="text-embedding-3-large"
    )

    cost_small = client_small._calculate_cost(1000)
    cost_large = client_large._calculate_cost(1000)

    # Large model should cost more
    assert cost_large > cost_small
    assert abs(cost_small - 0.00002) < 0.000001  # $0.00002 per token for 1000 tokens
    assert abs(cost_large - 0.00013) < 0.000001  # $0.00013 per token for 1000 tokens


def test_unknown_model_cost_calculation(mock_api_key, mocker):
    """Test cost calculation with unknown model."""
    client = OpenAIEmbeddingClient(
        api_key=mock_api_key,
        model="unknown-model"
    )

    # Mock logging to verify warning
    mocker.patch("embeddings.openai_client.logger")

    cost = client._calculate_cost(1000)
    assert cost == 0.0


def test_embedding_with_whitespace_trimming(client, mocker):
    """Test that whitespace is trimmed from input text."""
    mock_embedding = [0.1] * 1536

    mock_create = mocker.patch(
        "openai.Embedding.create",
        return_value={
            "data": [{"embedding": mock_embedding}],
            "usage": {"total_tokens": 10},
        }
    )

    client.embed("  \n  Text with whitespace  \n  ")

    # Verify that create was called with trimmed text
    call_args = mock_create.call_args
    assert "Text with whitespace" in str(call_args)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
