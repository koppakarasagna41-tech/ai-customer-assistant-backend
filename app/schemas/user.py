from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Plaintext password")
    role: str = Field("customer", description="User role (customer, support_agent, support_admin, supervisor, system_admin)")

class UserResponse(UserBase):
    user_id: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[str]

    class Config:
        from_attributes = True
