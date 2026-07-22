from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.refresh_token import (
    RefreshTokenCreate,
    RefreshTokenResponse,
)
from app.services.refresh_token_service import (
    RefreshTokenService,
    get_refresh_token_service,
)

router = APIRouter()


@router.post(
    "/",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_refresh_token(
    refresh_token: RefreshTokenCreate,
    service: RefreshTokenService = Depends(
        get_refresh_token_service,
    ),
):
    return await service.create_refresh_token(refresh_token)


@router.get(
    "/{token}",
    response_model=RefreshTokenResponse,
)
async def get_refresh_token(
    token: str,
    service: RefreshTokenService = Depends(
        get_refresh_token_service,
    ),
):
    refresh_token = await service.get_refresh_token(token)

    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found",
        )

    return refresh_token


@router.put(
    "/revoke/{token}",
)
async def revoke_refresh_token(
    token: str,
    service: RefreshTokenService = Depends(
        get_refresh_token_service,
    ),
):
    revoked = await service.revoke_refresh_token(token)

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found",
        )

    return {
        "success": True,
        "message": "Refresh token revoked successfully",
    }


@router.delete(
    "/expired",
)
async def delete_expired_tokens(
    service: RefreshTokenService = Depends(
        get_refresh_token_service,
    ),
):
    deleted = await service.delete_expired_tokens()

    return {
        "success": True,
        "deleted_tokens": deleted,
    }