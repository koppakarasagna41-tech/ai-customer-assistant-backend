from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user_preference import (
    UserPreferenceCreate,
    UserPreferenceResponse,
    UserPreferenceUpdate,
)
from app.services.user_preference_service import (
    UserPreferenceService,
    get_user_preference_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=UserPreferenceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_preference(
    preference: UserPreferenceCreate,
    service: UserPreferenceService = Depends(
        get_user_preference_service,
    ),
):
    return await service.create_preference(preference)


@router.get(
    "/{user_id}",
    response_model=UserPreferenceResponse,
)
async def get_preference(
    user_id: str,
    service: UserPreferenceService = Depends(
        get_user_preference_service,
    ),
):
    preference = await service.get_preference(user_id)

    if preference is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preference not found",
        )

    return preference


@router.put(
    "/{user_id}",
    response_model=UserPreferenceResponse,
)
async def update_preference(
    user_id: str,
    preference: UserPreferenceUpdate,
    service: UserPreferenceService = Depends(
        get_user_preference_service,
    ),
):
    updated = await service.update_preference(
        user_id,
        preference,
    )

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preference not found",
        )

    return updated