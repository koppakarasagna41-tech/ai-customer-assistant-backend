from app.schemas.kpi import KPIDetail, KPIOverview
from app.services.metrics_service import MetricsService, get_metrics_service


class KPIService:
    def __init__(self, metrics_service: MetricsService = None):
        self.metrics_service = metrics_service or get_metrics_service()

    def get_kpi_overview(self) -> KPIOverview:
        m = self.metrics_service.get_ticket_metrics()
        rag = self.metrics_service.get_rag_metrics()
        costs = self.metrics_service.get_comprehensive_metrics()["cost"]

        # Resolution rate calculation
        resolution_rate = round((m["resolved_tickets"] / max(1, m["total_tickets"])) * 100, 2)

        return KPIOverview(
            ticket_resolution_rate=KPIDetail(
                name="Ticket Resolution Rate",
                value=resolution_rate,
                target=90.0,
                unit="%",
                status="ON_TRACK" if resolution_rate >= 85.0 else "AT_RISK",
                trend="UP",
                change_percentage=1.4,
            ),
            avg_response_time=KPIDetail(
                name="Average Response Time",
                value=m["avg_response_time_min"],
                target=15.0,
                unit="min",
                status="ON_TRACK" if m["avg_response_time_min"] <= 15.0 else "BEHIND",
                trend="DOWN",
                change_percentage=-8.5,
            ),
            customer_satisfaction=KPIDetail(
                name="Customer Satisfaction Score",
                value=m["customer_satisfaction_score"],
                target=4.5,
                unit="pts",
                status="ON_TRACK" if m["customer_satisfaction_score"] >= 4.5 else "AT_RISK",
                trend="UP",
                change_percentage=2.1,
            ),
            ai_handling_rate=KPIDetail(
                name="AI Autonomous Handling Rate",
                value=rag["success_rate"],
                target=85.0,
                unit="%",
                status="ON_TRACK" if rag["success_rate"] >= 80.0 else "AT_RISK",
                trend="UP",
                change_percentage=3.8,
            ),
            cost_efficiency=KPIDetail(
                name="AI Cost Efficiency",
                value=costs["cost_per_ticket"],
                target=0.05,
                unit="USD",
                status="ON_TRACK" if costs["cost_per_ticket"] <= 0.05 else "AT_RISK",
                trend="DOWN",
                change_percentage=-12.4,
            ),
        )


_global_kpi_service = KPIService()


def get_kpi_service() -> KPIService:
    return _global_kpi_service
