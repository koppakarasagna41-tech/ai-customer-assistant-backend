from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str = Field(..., description="The OAuth2 JWT access token")
    refresh_token: str = Field(..., description="The refresh token used to get a new access token")
    token_type: str = Field("bearer", description="Token type, typically Bearer")
    expires_in: int = Field(..., description="Access token lifetime in seconds")

class TokenPayload(BaseModel):
    sub: str = Field(..., description="Subject of the token (user_id)")
    role: str = Field(..., description="User role")
    type: str = Field(..., description="Token type (access or refresh)")
