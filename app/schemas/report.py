from datetime import datetime

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    report_type: str = Field(
        ..., description="Type of report to generate"
    )

    format: str = Field(
        ..., description="File format: pdf, csv, excel, or json"
    )

    days: int = Field(
        ..., description="Number of days to include"
    )

    filters: dict = Field(
        default_factory=dict,
        description="Optional filters"
    )


class ScheduledReportConfig(BaseModel):
    schedule_id: str = Field(
        ..., description="Unique schedule id"
    )

    report_type: str = Field(
        ..., description="Report type"
    )

    frequency: str = Field(
        ..., description="daily, weekly or monthly"
    )

    recipients: list[str] = Field(
        ..., description="Recipient email list"
    )

    format: str = Field(
        ..., description="Report format"
    )

    is_active: bool = Field(
        True,
        description="Schedule status"
    )


class ReportMetadata(BaseModel):
    report_id: str = Field(
        ..., description="Unique ID of the generated report"
    )

    title: str = Field(
        ..., description="Title of the report"
    )

    format: str = Field(
        ..., description="File format used"
    )

    size_bytes: int = Field(
        ..., description="Size of the report in bytes"
    )

    created_at: datetime = Field(
        ..., description="Timestamp of generation"
    )

    download_url: str = Field(
        ..., description="Download link for the report"
    )

    created_by: str = Field(
        ..., description="User or schedule that triggered the report"
    )
