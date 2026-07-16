from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class UserContext(BaseModel):
    user_id: Optional[str] = Field(None, description="Unique identifier for the user")
    session_id: Optional[str] = Field(None, description="Session identifier for tracking conversation")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or metadata")
