from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ActivityLogCreate(BaseModel):
    ticket_id: str
    action: str
    performed_by: str


class ActivityLogResponse(BaseModel):
    id: int
    ticket_id: str
    action: str
    performed_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)