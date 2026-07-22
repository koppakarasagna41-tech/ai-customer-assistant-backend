from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserPreference(BaseModel):
    id: int
    user_id: str
    theme: str
    language: str
    email_notifications: bool
    push_notifications: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)