from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIEscalationLogic(BaseModel):
    id: int
    ticket_id: str
    escalation_reason: str
    escalation_level: str
    assigned_team: str | None = None
    status: str
    auto_escalated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)