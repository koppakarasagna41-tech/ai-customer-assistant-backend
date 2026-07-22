from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPreferenceCreate(BaseModel):
    user_id: str
    theme: str = "light"
    language: str = "en"
    email_notifications: bool = True
    push_notifications: bool = True


class UserPreferenceUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None


class UserPreferenceResponse(BaseModel):
    id: int
    user_id: str
    theme: str
    language: str
    email_notifications: bool
    push_notifications: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)