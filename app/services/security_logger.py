import logging
import threading
import uuid
from datetime import datetime
from typing import List, Dict, Any

class SecurityLogger:
    def __init__(self):
        self._lock = threading.Lock()
        self._events: List[Dict[str, Any]] = []
        self._total_scanned = 0
        self._blocked_count = 0
        
        self.logger = logging.getLogger("enterprise.security")
        self.logger.setLevel(logging.WARNING)

    def log_scan(self, prompt: str, is_safe: bool, risk_score: float, severity: str, risk_type: str, user_id: str = None, ip: str = None):
        with self._lock:
            self._total_scanned += 1
            if not is_safe:
                self._blocked_count += 1
            
            event = {
                "id": f"SEC_{uuid.uuid4().hex[:8]}",
                "timestamp": datetime.utcnow(),
                "prompt_snippet": prompt[:100] + ("..." if len(prompt) > 100 else ""),
                "risk_type": risk_type,
                "severity": severity,
                "risk_score": risk_score,
                "user_id": user_id,
                "ip_address": ip or "127.0.0.1"
            }
            self._events.append(event)
            # Limit memory footprint
            if len(self._events) > 200:
                self._events.pop(0)

            if not is_safe or severity in ["HIGH", "CRITICAL"]:
                self.logger.warning(
                    f"[AI SECURITY ALERT] Severity: {severity} | Risk: {risk_type} | Score: {risk_score} | Snippet: {event['prompt_snippet']}"
                )

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            critical_count = sum(1 for e in self._events if e["severity"] == "CRITICAL")
            avg_score = sum(e["risk_score"] for e in self._events) / max(1, len(self._events))
            return {
                "total_scanned": self._total_scanned,
                "malicious_blocked": self._blocked_count,
                "critical_alerts": critical_count,
                "average_risk_score": round(avg_score, 3),
                "recent_events": [dict(e) for e in reversed(self._events)]
            }

_global_security_logger = SecurityLogger()

def get_security_logger() -> SecurityLogger:
    return _global_security_logger
