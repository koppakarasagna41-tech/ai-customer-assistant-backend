from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIEscalationLogicCreate(BaseModel):
    ticket_id: str
    escalation_reason: str
    escalation_level: str
    assigned_team: str | None = None
    status: str
    auto_escalated: bool = True


class AIEscalationLogicUpdate(BaseModel):
    escalation_reason: str | None = None
    escalation_level: str | None = None
    assigned_team: str | None = None
    status: str | None = None
    auto_escalated: bool | None = None


class AIEscalationLogicResponse(BaseModel):
    id: int
    ticket_id: str
    escalation_reason: str
    escalation_level: str
    assigned_team: str | None = None
    status: str
    auto_escalated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)