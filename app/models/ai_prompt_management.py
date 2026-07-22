from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIPromptManagement(BaseModel):
    id: int
    prompt_name: str
    prompt_template: str
    prompt_version: str
    model_name: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
