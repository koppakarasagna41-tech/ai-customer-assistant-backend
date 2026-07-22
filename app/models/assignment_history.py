from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssignmentHistory(BaseModel):
    id: int
    ticket_id: str
    agent_id: str
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)
