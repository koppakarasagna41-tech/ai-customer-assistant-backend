from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    success: bool = Field(True, description="Indicates if the API call was successful")
    message: str | None = Field(None, description="Informational message about the operation")
    data: T | None = Field(None, description="Response payload data")


class PaginatedData(BaseModel, Generic[T]):
    items: list[T] = Field(..., description="List of items in the current page")
    total: int = Field(..., description="Total number of items across all pages")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
