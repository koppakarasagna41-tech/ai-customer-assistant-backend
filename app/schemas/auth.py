from pydantic import BaseModel, Field


class LoginCredentials(BaseModel):
    username_or_email: str = Field(..., description="Username or Email address of the user")
    password: str = Field(..., description="Plaintext password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token")
