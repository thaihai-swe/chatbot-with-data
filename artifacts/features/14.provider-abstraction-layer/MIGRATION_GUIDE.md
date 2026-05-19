# Provider Abstraction Layer - Migration Guide

## Overview

This guide helps you migrate from direct OpenAI client usage to the new provider abstraction layer introduced in Feature 14.

## What Changed

### Before (Direct OpenAI Usage)

```python
from embeddings.openai_client import OpenAIEmbeddingClient
from llm.client import LLMClient

# Direct instantiation
embedding_client = OpenAIEmbeddingClient(
    api_key=settings.embedding_api_key,
    api_base=settings.embedding_api_base,
    model=config.ingestion.embedding_model,
)
```

### After (Provider Abstraction)

```python
from providers.base import BaseEmbeddingProvider, BaseLLMProvider
from providers.factory import get_embedding_provider, get_llm_provider
from fastapi import Depends

# Dependency injection
def get_my_service(
    embedding_provider: BaseEmbeddingProvider = Depends(get_embedding_provider),
    llm_provider: BaseLLMProvider = Depends(get_llm_provider)
) -> MyService:
    return MyService(embedding_provider, llm_provider)
```

## Environment Variable Changes

### New Variables

Add these to your `.env` file:

```bash
# Provider selection
LLM_PROVIDER=openai                    # or "openai-compatible"
EMBEDDING_PROVIDER=openai              # or "openai-compatible"
```

### Custom Base URL Migration

**Old approach:**
```bash
OPENAI_API_BASE=http://localhost:20128/v1
```

**New approach:**
```bash
LLM_PROVIDER=openai-compatible
EMBEDDING_PROVIDER=openai-compatible
OPENAI_API_BASE=http://localhost:20128/v1
```

The key difference: You must now explicitly set the provider type to `openai-compatible` when using a custom base URL.

## Configuration Examples

### Example 1: Standard OpenAI

```bash
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

### Example 2: OpenRouter or Custom Endpoint

```bash
LLM_PROVIDER=openai-compatible
EMBEDDING_PROVIDER=openai-compatible
OPENAI_API_KEY=sk-your-custom-key
OPENAI_API_BASE=http://localhost:20128/v1
CHAT_MODEL=rag-combo
EMBEDDING_MODEL=openrouter/openai/text-embedding-3-small
```

### Example 3: Mixed Providers

```bash
# Use OpenAI for LLM, custom endpoint for embeddings
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai-compatible
OPENAI_API_KEY=sk-openai-key
EMBEDDING_API_KEY=sk-custom-key
EMBEDDING_API_BASE=http://localhost:11434/v1
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=custom-embedding-model
```

## Service Migration Checklist

If you have custom services that use OpenAI clients directly:

- [ ] Replace `OpenAIEmbeddingClient` imports with `BaseEmbeddingProvider`
- [ ] Replace `LLMClient` imports with `BaseLLMProvider`
- [ ] Update constructor to accept provider interfaces
- [ ] Update factory function to use `Depends(get_embedding_provider)` or `Depends(get_llm_provider)`
- [ ] Update method calls from `client.embed()` to `provider.embed()`
- [ ] Update method calls from `client.generate_completion()` to `provider.generate_completion()`

## Verification Steps

### 1. Check Environment Variables

```bash
# Verify your .env file has the new variables
grep -E "LLM_PROVIDER|EMBEDDING_PROVIDER" backend/.env
```

### 2. Test Provider Selection

```python
# In Python shell or test script
from providers.factory import get_llm_provider, get_embedding_provider

llm = get_llm_provider()
embedding = get_embedding_provider()

print(f"LLM Provider: {type(llm).__name__}")
print(f"Embedding Provider: {type(embedding).__name__}")
```

Expected output:
```
LLM Provider: OpenAILLMProvider
Embedding Provider: OpenAIEmbeddingProvider
```

### 3. Test Custom Base URL

```bash
# Set custom endpoint
export LLM_PROVIDER=openai-compatible
export OPENAI_API_BASE=http://localhost:20128/v1

# Run a simple query
python -c "
from providers.factory import get_llm_provider
provider = get_llm_provider()
response = provider.generate_completion([{'role': 'user', 'content': 'Hello'}])
print(response)
"
```

## Troubleshooting

### Issue: "No module named 'providers'"

**Cause:** Import path issue or providers module not found.

**Solution:** Ensure you're importing from the correct path:
```python
from providers.base import BaseLLMProvider
from providers.factory import get_llm_provider
```

### Issue: Provider not switching when changing environment variables

**Cause:** Factory functions use `@lru_cache()` for singleton pattern.

**Solution:** Restart your application after changing environment variables. The cache is cleared on restart.

### Issue: "OpenAI API key not found"

**Cause:** Missing or incorrect API key configuration.

**Solution:** Verify your `.env` file has:
```bash
OPENAI_API_KEY=your-key-here
# Or for separate embedding key:
EMBEDDING_API_KEY=your-embedding-key
```

### Issue: Custom endpoint not being used

**Cause:** Provider type not set to `openai-compatible`.

**Solution:** Explicitly set the provider type:
```bash
LLM_PROVIDER=openai-compatible
EMBEDDING_PROVIDER=openai-compatible
OPENAI_API_BASE=http://your-custom-endpoint/v1
```

## Backward Compatibility

The abstraction layer preserves all existing behavior:

- ✅ Retry logic with exponential backoff
- ✅ Cost tracking and usage statistics
- ✅ Batch processing with rate limiting
- ✅ Streaming support for LLM responses
- ✅ Error handling and logging

No changes to API responses or behavior are expected.

## Future Provider Support

The abstraction layer is designed to support additional providers in the future:

- Anthropic (Claude)
- Ollama (local models)
- HuggingFace embeddings
- Azure OpenAI
- Custom providers

To add a new provider, implement the `BaseLLMProvider` or `BaseEmbeddingProvider` interface and register it in the factory functions.

## Support

If you encounter issues during migration:

1. Check this guide's troubleshooting section
2. Verify environment variables are set correctly
3. Review the implementation status document: `IMPLEMENTATION_STATUS.md`
4. Check service logs for detailed error messages

---

**Migration Date:** 2026-05-19  
**Feature:** 14.provider-abstraction-layer  
**Status:** Complete
