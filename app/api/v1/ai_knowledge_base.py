from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_knowledge_base import (
    AIKnowledgeBaseCreate,
    AIKnowledgeBaseResponse,
    AIKnowledgeBaseUpdate,
)
from app.services.ai_knowledge_base_service import (
    AIKnowledgeBaseService,
    get_ai_knowledge_base_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AIKnowledgeBaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge(
    data: AIKnowledgeBaseCreate,
    service: AIKnowledgeBaseService = Depends(
        get_ai_knowledge_base_service
    ),
):
    return await service.create_knowledge(data)


@router.get(
    "/",
    response_model=list[AIKnowledgeBaseResponse],
)
async def get_all_knowledge(
    service: AIKnowledgeBaseService = Depends(
        get_ai_knowledge_base_service
    ),
):
    return await service.get_all_knowledge()


@router.get(
    "/{knowledge_id}",
    response_model=AIKnowledgeBaseResponse,
)
async def get_knowledge(
    knowledge_id: int,
    service: AIKnowledgeBaseService = Depends(
        get_ai_knowledge_base_service
    ),
):
    knowledge = await service.get_knowledge(
        knowledge_id
    )

    if not knowledge:
        raise HTTPException(
            status_code=404,
            detail="Knowledge not found",
        )

    return knowledge


@router.put(
    "/{knowledge_id}",
    response_model=AIKnowledgeBaseResponse,
)
async def update_knowledge(
    knowledge_id: int,
    data: AIKnowledgeBaseUpdate,
    service: AIKnowledgeBaseService = Depends(
        get_ai_knowledge_base_service
    ),
):
    knowledge = await service.update_knowledge(
        knowledge_id,
        data,
    )

    if not knowledge:
        raise HTTPException(
            status_code=404,
            detail="Knowledge not found",
        )

    return knowledge


@router.delete(
    "/{knowledge_id}",
)
async def delete_knowledge(
    knowledge_id: int,
    service: AIKnowledgeBaseService = Depends(
        get_ai_knowledge_base_service
    ),
):
    deleted = await service.delete_knowledge(
        knowledge_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Knowledge not found",
        )

    return {
        "message": "Knowledge deleted successfully"
    }