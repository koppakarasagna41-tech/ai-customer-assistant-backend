from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai_prompt_management import (
    AIPromptManagementCreate,
    AIPromptManagementResponse,
    AIPromptManagementUpdate,
)
from app.services.ai_prompt_management_service import (
    AIPromptManagementService,
    get_ai_prompt_management_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=AIPromptManagementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt(
    data: AIPromptManagementCreate,
    service: AIPromptManagementService = Depends(
        get_ai_prompt_management_service
    ),
):
    return await service.create_prompt(data)


@router.get(
    "/",
    response_model=list[AIPromptManagementResponse],
)
async def get_all_prompts(
    service: AIPromptManagementService = Depends(
        get_ai_prompt_management_service
    ),
):
    return await service.get_all_prompts()


@router.get(
    "/{prompt_id}",
    response_model=AIPromptManagementResponse,
)
async def get_prompt(
    prompt_id: int,
    service: AIPromptManagementService = Depends(
        get_ai_prompt_management_service
    ),
):
    prompt = await service.get_prompt(prompt_id)

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found",
        )

    return prompt


@router.put(
    "/{prompt_id}",
    response_model=AIPromptManagementResponse,
)
async def update_prompt(
    prompt_id: int,
    data: AIPromptManagementUpdate,
    service: AIPromptManagementService = Depends(
        get_ai_prompt_management_service
    ),
):
    prompt = await service.update_prompt(
        prompt_id,
        data,
    )

    if not prompt:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found",
        )

    return prompt


@router.delete(
    "/{prompt_id}",
)
async def delete_prompt(
    prompt_id: int,
    service: AIPromptManagementService = Depends(
        get_ai_prompt_management_service
    ),
):
    deleted = await service.delete_prompt(
        prompt_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Prompt not found",
        )

    return {
        "message": "Prompt deleted successfully"
    }