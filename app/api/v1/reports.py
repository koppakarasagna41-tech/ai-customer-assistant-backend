from fastapi import APIRouter, status, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.response import BaseResponse
from app.schemas.report import ReportRequest, ScheduledReportConfig, ReportMetadata
from app.services.report_service import get_report_service, ReportService

router = APIRouter()

@router.post(
    "/reports/generate",
    response_model=BaseResponse[ReportMetadata],
    status_code=status.HTTP_201_CREATED,
    summary="Generate a custom performance report",
    description="Manually trigger immediate generation of an enterprise performance report in the desired format (PDF, CSV, Excel, JSON)."
)
async def generate_custom_report(
    payload: ReportRequest,
    report_service: ReportService = Depends(get_report_service)
):
    report_metadata = report_service.generate_custom_report(payload)
    return BaseResponse(
        success=True,
        message="Custom report compiled and generated successfully.",
        data=report_metadata
    )

@router.get(
    "/reports/schedules",
    response_model=BaseResponse[List[ScheduledReportConfig]],
    status_code=status.HTTP_200_OK,
    summary="List all scheduled reports",
    description="Fetch a list of active and inactive daily, weekly, and monthly automated reports."
)
async def list_scheduled_reports(
    report_service: ReportService = Depends(get_report_service)
):
    schedules = report_service.get_scheduled_reports()
    return BaseResponse(
        success=True,
        message="Scheduled reports configuration fetched successfully.",
        data=schedules
    )

@router.post(
    "/reports/schedules",
    response_model=BaseResponse[ScheduledReportConfig],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new scheduled report job",
    description="Establish a recurring schedule for reports, notifying designated email recipients automatically."
)
async def create_scheduled_report(
    payload: ScheduledReportConfig,
    report_service: ReportService = Depends(get_report_service)
):
    new_schedule = report_service.create_scheduled_report(payload)
    return BaseResponse(
        success=True,
        message="Automated report schedule created successfully.",
        data=new_schedule
    )

@router.patch(
    "/reports/schedules/{schedule_id}/toggle",
    response_model=BaseResponse[ScheduledReportConfig],
    status_code=status.HTTP_200_OK,
    summary="Enable/Disable report schedule",
    description="Activate or suspend a scheduled report job by its identifier."
)
async def toggle_scheduled_report(
    schedule_id: str = Path(..., description="The unique scheduled report job ID"),
    is_active: bool = Query(..., description="Set True to activate, False to pause"),
    report_service: ReportService = Depends(get_report_service)
):
    updated_schedule = report_service.toggle_scheduled_report(schedule_id, is_active)
    if not updated_schedule:
        return BaseResponse(
            success=False,
            message=f"Schedule job with ID {schedule_id} not found.",
            data=None
        )
    return BaseResponse(
        success=True,
        message="Scheduled report status updated successfully.",
        data=updated_schedule
    )
