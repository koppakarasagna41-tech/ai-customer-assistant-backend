class DashboardRepository:
    """
    Dashboard data is collected by other services
    (KPI, Metrics, Trend Analysis, Cache).

    This repository is kept as a placeholder so the
    project follows the same architecture as the other
    modules.
    """

    def __init__(self):
        pass


_global_dashboard_repository = DashboardRepository()


def get_dashboard_repository() -> DashboardRepository:
    return _global_dashboard_repository
