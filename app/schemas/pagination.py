from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
