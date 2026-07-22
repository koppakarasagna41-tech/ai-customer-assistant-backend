from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    type: str = "info"


class NotificationUpdate(BaseModel):
    is_read: bool


class NotificationResponse(BaseModel):
    id: int
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
