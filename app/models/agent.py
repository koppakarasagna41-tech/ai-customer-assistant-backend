from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Agent(BaseModel):
    agent_id: str
    name: str
    email: str
    department: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
