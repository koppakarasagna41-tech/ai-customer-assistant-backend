from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AIPromptManagementCreate(BaseModel):
    prompt_name: str
    prompt_template: str
    prompt_version: str
    model_name: str | None = None
    is_active: bool = True


class AIPromptManagementUpdate(BaseModel):
    prompt_name: str | None = None
    prompt_template: str | None = None
    prompt_version: str | None = None
    model_name: str | None = None
    is_active: bool | None = None


class AIPromptManagementResponse(BaseModel):
    id: int
    prompt_name: str
    prompt_template: str
    prompt_version: str
    model_name: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
