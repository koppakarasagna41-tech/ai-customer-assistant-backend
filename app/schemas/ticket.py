from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=150, description="Brief summary of the issue")
    description: str = Field(..., min_length=10, description="Detailed explanation of the issue")
    category: str = Field(..., description="Ticket category (e.g., billing, technical, account)")
    priority: str = Field("medium", description="Ticket priority (low, medium, high, urgent)")


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=150)
    description: str | None = Field(None, min_length=10)
    category: str | None = None
    priority: str | None = None
    status: str | None = None


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., description="New status (open, in_progress, closed, escalated)")
    comment: str | None = Field(None, description="Optional comment regarding the status change")


class TicketPriorityUpdate(BaseModel):
    priority: str = Field(..., description="New priority (low, medium, high, urgent)")
    comment: str | None = Field(None, description="Optional comment explaining the priority change")


class TicketAgentAssign(BaseModel):
    assigned_agent_id: str = Field(..., description="ID of the agent being assigned")
    comment: str | None = Field(None, description="Optional comment regarding the assignment")


class TicketCommentCreate(BaseModel):
    author: str = Field(..., description="Author of the comment")
    content: str = Field(..., description="Content of the comment")


class TicketDashboardStats(BaseModel):
    total_count: int = Field(..., description="Total tickets")
    open_count: int = Field(..., description="Open tickets count")
    in_progress_count: int = Field(..., description="In progress tickets count")
    closed_count: int = Field(..., description="Closed tickets count")
    escalated_count: int = Field(..., description="Escalated tickets count")
    distribution_by_priority: dict[str, int] = Field(
        ..., description="Ticket distribution by priority"
    )
    distribution_by_category: dict[str, int] = Field(
        ..., description="Ticket distribution by category"
    )
