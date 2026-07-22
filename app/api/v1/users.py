from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.schemas.user import UserResponse, UserUpdate
from app.services.auth_service import AuthService, get_auth_service
from app.services.user_service import UserService, get_user_service

router = APIRouter()


@router.get(
    "/users",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.list_users()


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: str = Path(..., description="User ID"),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    payload: UserUpdate,
    user_id: str = Path(..., description="User ID"),
    service: UserService = Depends(get_user_service),
):
    user = await service.update_user(user_id, payload)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: str = Path(..., description="User ID"),
    service: UserService = Depends(get_user_service),
):
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"success": True, "message": "User deleted successfully"}
