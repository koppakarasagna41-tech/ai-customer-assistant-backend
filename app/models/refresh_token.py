from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RefreshToken(BaseModel):
    id: int | None = None
    user_id: str
    refresh_token: str
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
