from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentHistoryCreate(BaseModel):
    ticket_id: str
    agent_id: str


class AssignmentHistoryResponse(BaseModel):
    id: int
    ticket_id: str
    agent_id: str
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)
