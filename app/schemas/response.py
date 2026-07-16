from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool = Field(True, description="Indicates if the API call was successful")
    message: Optional[str] = Field(None, description="Informational message about the operation")
    data: Optional[T] = Field(None, description="Response payload data")

class PaginatedData(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items in the current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
