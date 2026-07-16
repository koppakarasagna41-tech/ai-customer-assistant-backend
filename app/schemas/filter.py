from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class TicketFilterParams(BaseModel):
    category: Optional[str] = Field(None, description="Filter by ticket category")
    priority: Optional[str] = Field(None, description="Filter by priority (low, medium, high)")
    status: Optional[str] = Field(None, description="Filter by ticket status (open, in_progress, closed, escalated)")
    assigned_agent_id: Optional[str] = Field(None, description="Filter by assigned agent ID")
    search_query: Optional[str] = Field(None, description="Search query matching title or description")
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_order: Optional[SortOrder] = Field(SortOrder.DESC, description="Sorting direction")
