from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLog(BaseModel):
    id: int
    entity: str
    entity_id: str
    action: str
    performed_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
