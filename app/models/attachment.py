from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Attachment(BaseModel):
    id: int | None = None
    ticket_id: str
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)