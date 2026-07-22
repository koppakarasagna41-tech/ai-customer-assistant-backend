from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttachmentCreate(BaseModel):
    ticket_id: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)
    file_path: str = Field(..., min_length=1)
    file_type: str = Field(..., min_length=1)
    file_size: int = Field(..., ge=0)


class AttachmentResponse(BaseModel):
    id: int
    ticket_id: str
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
