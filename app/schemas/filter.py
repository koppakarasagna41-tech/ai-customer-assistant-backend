from enum import StrEnum

from pydantic import BaseModel, Field


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class TicketFilterParams(BaseModel):
    category: str | None = Field(None, description="Filter by ticket category")
    priority: str | None = Field(None, description="Filter by priority (low, medium, high)")
    status: str | None = Field(
        None, description="Filter by ticket status (open, in_progress, closed, escalated)"
    )
    assigned_agent_id: str | None = Field(None, description="Filter by assigned agent ID")
    search_query: str | None = Field(None, description="Search query matching title or description")
    sort_by: str | None = Field("created_at", description="Field to sort by")
    sort_order: SortOrder | None = Field(SortOrder.DESC, description="Sorting direction")
