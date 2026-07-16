from pydantic import BaseModel, Field
from typing import Optional

class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code specific to the domain")
    message: str = Field(..., description="Human-readable description of the error")
    field: Optional[str] = Field(None, description="The field that caused the error, if applicable")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Always False for error responses")
    error: ErrorDetail = Field(..., description="Details of the error")
