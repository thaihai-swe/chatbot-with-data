from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from providers.base import BaseLLMProvider
from providers.factory import get_llm_provider
from chat.knowledge_products import KnowledgeProductService
from repositories.collection_repository import CollectionRepository

router = APIRouter(prefix="/collections/{collection_id}/generate", tags=["generate"])

class FlashcardResponse(BaseModel):
    question: str
    answer: str

class TextProductResponse(BaseModel):
    content: str

def get_knowledge_product_service(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider)
) -> KnowledgeProductService:
    return KnowledgeProductService(llm_provider=llm_provider)

@router.post("/study-guide", response_model=TextProductResponse)
async def generate_study_guide(
    collection_id: str,
    document_id: Optional[str] = Query(None),
    service: KnowledgeProductService = Depends(get_knowledge_product_service)
) -> TextProductResponse:
    try:
        content = service.generate_study_guide(collection_id, document_id)
        return TextProductResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/briefing-doc", response_model=TextProductResponse)
async def generate_briefing_doc(
    collection_id: str,
    document_id: Optional[str] = Query(None),
    service: KnowledgeProductService = Depends(get_knowledge_product_service)
) -> TextProductResponse:
    try:
        content = service.generate_briefing_doc(collection_id, document_id)
        return TextProductResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/faq", response_model=TextProductResponse)
async def generate_faq(
    collection_id: str,
    document_id: Optional[str] = Query(None),
    service: KnowledgeProductService = Depends(get_knowledge_product_service)
) -> TextProductResponse:
    try:
        content = service.generate_faq(collection_id, document_id)
        return TextProductResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/timeline", response_model=TextProductResponse)
async def generate_timeline(
    collection_id: str,
    document_id: Optional[str] = Query(None),
    service: KnowledgeProductService = Depends(get_knowledge_product_service)
) -> TextProductResponse:
    try:
        content = service.generate_timeline(collection_id, document_id)
        return TextProductResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/glossary", response_model=TextProductResponse)
async def generate_glossary(
    collection_id: str,
    document_id: Optional[str] = Query(None),
    service: KnowledgeProductService = Depends(get_knowledge_product_service)
) -> TextProductResponse:
    try:
        content = service.generate_glossary(collection_id, document_id)
        return TextProductResponse(content=content)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/flashcards", response_model=List[FlashcardResponse])
async def generate_flashcards(
    collection_id: str,
    document_id: Optional[str] = Query(None),
    service: KnowledgeProductService = Depends(get_knowledge_product_service)
) -> List[FlashcardResponse]:
    try:
        cards = service.generate_flashcards(collection_id, document_id)
        return [FlashcardResponse(question=c["question"], answer=c["answer"]) for c in cards]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
