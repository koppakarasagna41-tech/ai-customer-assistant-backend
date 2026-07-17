from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginCredentials, RefreshTokenRequest
from app.schemas.response import BaseResponse
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/auth/register",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user (Customer, Agent, Admin, etc.) in the system.",
)
async def register(payload: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        user = await service.register_user(payload)
        return BaseResponse(
            success=True,
            message="User registered successfully",
            data=UserResponse.from_attributes(user),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post(
    "/auth/login",
    response_model=BaseResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and retrieve tokens",
    description="Logs in a user with username/email and password, returning JWT tokens.",
)
async def login(payload: LoginCredentials, service: AuthService = Depends(get_auth_service)):
    try:
        token = await service.login(payload)
        return BaseResponse(success=True, message="Login successful", data=token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.post(
    "/auth/refresh",
    response_model=BaseResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Uses a valid refresh token to obtain a new access and refresh token.",
)
async def refresh(payload: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)):
    try:
        token = await service.refresh_token(payload.refresh_token)
        return BaseResponse(success=True, message="Token refreshed successfully", data=token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e


@router.post(
    "/auth/logout",
    response_model=BaseResponse[bool],
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logs out the current authenticated user (client-side token abandonment).",
)
async def logout(current_user: User = Depends(get_current_user)):
    return BaseResponse(success=True, message="Logout successful", data=True)


@router.get(
    "/auth/me",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user details",
    description="Retrieves the profile and permissions of the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return BaseResponse(
        success=True,
        message="Current user profile retrieved",
        data=UserResponse.from_attributes(current_user),
    )
