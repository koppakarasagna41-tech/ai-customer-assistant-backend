from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AgentCreate(BaseModel):
    name: str
    email: EmailStr
    department: str


class AgentResponse(BaseModel):
    agent_id: str
    name: str
    email: EmailStr
    department: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)