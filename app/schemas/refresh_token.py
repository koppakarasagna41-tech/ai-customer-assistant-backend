from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RefreshTokenCreate(BaseModel):
    user_id: str
    refresh_token: str
    expires_at: datetime


class RefreshTokenResponse(BaseModel):
    id: int
    user_id: str
    refresh_token: str
    expires_at: datetime
    is_revoked: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)