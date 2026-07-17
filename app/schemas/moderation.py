from pydantic import BaseModel, Field


class ContentModerationRequest(BaseModel):
    content: str = Field(..., description="The content to moderate")


class ModerationCategory(BaseModel):
    flagged: bool
    score: float


class ContentModerationResult(BaseModel):
    flagged: bool
    categories: dict[str, ModerationCategory]
    action_taken: str = Field(..., description="Action taken: ALLOW, BLOCK, MASK")
    filtered_content: str
