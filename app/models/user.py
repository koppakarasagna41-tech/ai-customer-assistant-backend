from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

class User(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    role: str  # customer, support_agent, support_admin, supervisor, system_admin
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    permissions: List[str] = Field(default_factory=list)

class UserInDB(User):
    hashed_password: str
