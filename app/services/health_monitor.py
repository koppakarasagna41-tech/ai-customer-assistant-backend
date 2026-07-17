import threading
from typing import Any


class HealthMonitorService:
    def __init__(self):
        self._lock = threading.Lock()
        self._response_times: list[float] = [
            45.0,
            52.0,
            61.0,
            48.0,
            55.0,
            72.0,
            50.0,
            49.0,
            51.0,
            58.0,
        ]
        self._errors_count = 12
        self._success_count = 4850

    def record_request(self, response_time_ms: float, is_error: bool = False):
        with self._lock:
            self._response_times.append(response_time_ms)
            if len(self._response_times) > 1000:
                self._response_times.pop(0)
            if is_error:
                self._errors_count += 1
            else:
                self._success_count += 1

    def get_health_metrics(self) -> dict[str, Any]:
        with self._lock:
            # Uptime is simulated high
            uptime = 99.98
            total_reqs = self._errors_count + self._success_count
            error_rate = round((self._errors_count / max(1, total_reqs)) * 100, 2)

            # P95 latency calculation
            if self._response_times:
                sorted_times = sorted(self._response_times)
                idx = int(len(sorted_times) * 0.95)
                p95_latency = round(sorted_times[min(idx, len(sorted_times) - 1)], 1)
            else:
                p95_latency = 52.0

            return {
                "api_uptime": uptime,
                "p95_latency_ms": p95_latency,
                "error_rate": error_rate,
                "total_requests": total_reqs,
                "status": "HEALTHY" if error_rate < 2.0 else "DEGRADED",
            }


_global_health_monitor = HealthMonitorService()


def get_health_monitor_service() -> HealthMonitorService:
    return _global_health_monitor
