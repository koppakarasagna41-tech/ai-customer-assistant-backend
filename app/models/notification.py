from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Notification(BaseModel):
    id: int | None = None
    user_id: str
    title: str
    message: str
    type: str = "info"
    is_read: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
