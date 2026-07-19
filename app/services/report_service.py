import uuid
from datetime import datetime, timedelta

from app.schemas.report import (
    ReportMetadata,
    ReportRequest,
    ScheduledReportConfig,
)
from app.services.export_service import ExportService, get_export_service
from app.services.metrics_service import MetricsService, get_metrics_service


class ReportService:
    def __init__(
        self,
        metrics_service: MetricsService = None,
        export_service: ExportService = None,
    ):
        self.metrics_service = metrics_service or get_metrics_service()
        self.export_service = export_service or get_export_service()

        self._schedules: list[ScheduledReportConfig] = [
            ScheduledReportConfig(
                schedule_id="SCH_001",
                report_type="daily_performance",
                frequency="daily",
                recipients=["executive-team@company.com"],
                format="pdf",
                is_active=True,
            ),
            ScheduledReportConfig(
                schedule_id="SCH_002",
                report_type="weekly_kpi",
                frequency="weekly",
                recipients=[
                    "support-operations@company.com",
                    "managers@company.com",
                ],
                format="csv",
                is_active=True,
            ),
            ScheduledReportConfig(
                schedule_id="SCH_003",
                report_type="monthly_finance",
                frequency="monthly",
                recipients=[
                    "finance-billing@company.com",
                    "executive-team@company.com",
                ],
                format="excel",
                is_active=False,
            ),
        ]

    def generate_custom_report(
        self,
        request: ReportRequest,
    ) -> ReportMetadata:

        metrics = self.metrics_service.get_comprehensive_metrics()

        export_res = self.export_service.perform_export(
            request.format,
            metrics,
        )

        return ReportMetadata(
           report_id="REP_" + uuid.uuid4().hex[:8],
            title=request.report_type,
            format=request.format,
            size_bytes=export_res.size_bytes,
            created_at=datetime.utcnow(),
            download_url=export_res.download_url,
            created_by="manual",
        )

    def get_scheduled_reports(self):
        return self._schedules

    def create_scheduled_report(
        self,
        config: ScheduledReportConfig,
    ):

        config.schedule_id = config.schedule_id or (
            "SCH_" + uuid.uuid4().hex[:8]
        )

        self._schedules.append(config)

        return config

    def toggle_scheduled_report(
        self,
        schedule_id: str,
        is_active: bool,
    ):

        for sch in self._schedules:
            if sch.schedule_id == schedule_id:
                sch.is_active = is_active
                return sch

        return None


_global_report_service = ReportService()


def get_report_service() -> ReportService:
 return _global_report_service