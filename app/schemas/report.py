from datetime import datetime

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    title: str = Field(..., description="Title of the report")
    format: str = Field(..., description="File format: pdf, csv, excel, or json")
    start_date: datetime = Field(..., description="Start date for data extraction")
    end_date: datetime = Field(..., description="End date for data extraction")
    include_sections: list[str] = Field(
        default=["tickets", "performance", "cost", "rag"],
        description="List of sections to include (e.g. tickets, performance, cost, rag)",
    )


class ScheduledReportConfig(BaseModel):
    id: str | None = Field(None, description="Unique ID of the scheduled report")
    title: str = Field(..., description="Title of the scheduled report")
    frequency: str = Field(..., description="Frequency of generation: daily, weekly, or monthly")
    recipients: list[str] = Field(..., description="Emails of recipients to receive the report")
    format: str = Field(..., description="File format: pdf, csv, excel, or json")
    is_active: bool = Field(True, description="Whether the schedule is active")
    next_run: datetime | None = Field(None, description="Timestamp for the next generation run")


class ReportMetadata(BaseModel):
    id: str = Field(..., description="Unique ID of the generated report")
    title: str = Field(..., description="Title of the report")
    format: str = Field(..., description="File format used")
    size_bytes: int = Field(..., description="Size of the report in bytes")
    created_at: datetime = Field(..., description="Timestamp of generation")
    download_url: str = Field(..., description="Download link for the report")
    created_by: str = Field(..., description="User or schedule that triggered the report")
