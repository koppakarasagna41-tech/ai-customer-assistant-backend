import uuid
from datetime import datetime, timedelta

from app.schemas.report import ReportMetadata, ReportRequest, ScheduledReportConfig
from app.services.export_service import ExportService, get_export_service
from app.services.metrics_service import MetricsService, get_metrics_service


class ReportService:
    def __init__(
        self, metrics_service: MetricsService = None, export_service: ExportService = None
    ):
        self.metrics_service = metrics_service or get_metrics_service()
        self.export_service = export_service or get_export_service()
        self._schedules: list[ScheduledReportConfig] = [
            ScheduledReportConfig(
                id="SCH_001",
                title="Daily Executive Performance Report",
                frequency="daily",
                recipients=["executive-team@company.com"],
                format="pdf",
                is_active=True,
                next_run=datetime.utcnow() + timedelta(days=1),
            ),
            ScheduledReportConfig(
                id="SCH_002",
                title="Weekly Operational KPI Dashboard Export",
                frequency="weekly",
                recipients=["support-operations@company.com", "managers@company.com"],
                format="csv",
                is_active=True,
                next_run=datetime.utcnow() + timedelta(days=5),
            ),
            ScheduledReportConfig(
                id="SCH_003",
                title="Monthly Financial & Cost Analysis Summary",
                frequency="monthly",
                recipients=["finance-billing@company.com", "executive-team@company.com"],
                format="excel",
                is_active=False,
                next_run=datetime.utcnow() + timedelta(days=20),
            ),
        ]

    def generate_custom_report(self, request: ReportRequest) -> ReportMetadata:
        metrics = self.metrics_service.get_comprehensive_metrics()
        export_res = self.export_service.perform_export(request.format, metrics)

        return ReportMetadata(
            id="REP_" + uuid.uuid4().hex[:8],
            title=request.title,
            format=request.format,
            size_bytes=export_res.size_bytes,
            created_at=datetime.utcnow(),
            download_url=export_res.download_url,
            created_by="manual",
        )

    def get_scheduled_reports(self) -> list[ScheduledReportConfig]:
        return self._schedules

    def create_scheduled_report(self, config: ScheduledReportConfig) -> ScheduledReportConfig:
        config.id = "SCH_" + uuid.uuid4().hex[:8]
        if not config.next_run:
            if config.frequency == "daily":
                config.next_run = datetime.utcnow() + timedelta(days=1)
            elif config.frequency == "weekly":
                config.next_run = datetime.utcnow() + timedelta(weeks=1)
            else:
                config.next_run = datetime.utcnow() + timedelta(days=30)
        self._schedules.append(config)
        return config

    def toggle_scheduled_report(
        self, schedule_id: str, is_active: bool
    ) -> ScheduledReportConfig | None:
        for sch in self._schedules:
            if sch.id == schedule_id:
                sch.is_active = is_active
                return sch
        return None


_global_report_service = ReportService()


def get_report_service() -> ReportService:
    return _global_report_service
