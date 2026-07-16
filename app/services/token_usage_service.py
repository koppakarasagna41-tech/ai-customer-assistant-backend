import threading
from typing import Dict, Any, List
from datetime import datetime, timedelta

class TokenUsageService:
    def __init__(self):
        self._lock = threading.Lock()
        self._history: List[Dict[str, Any]] = [
            {"timestamp": datetime.utcnow() - timedelta(days=5), "prompt_tokens": 12000, "completion_tokens": 4000, "total_tokens": 16000},
            {"timestamp": datetime.utcnow() - timedelta(days=4), "prompt_tokens": 15000, "completion_tokens": 5200, "total_tokens": 20200},
            {"timestamp": datetime.utcnow() - timedelta(days=3), "prompt_tokens": 18000, "completion_tokens": 6100, "total_tokens": 24100},
            {"timestamp": datetime.utcnow() - timedelta(days=2), "prompt_tokens": 14000, "completion_tokens": 4800, "total_tokens": 18800},
            {"timestamp": datetime.utcnow() - timedelta(days=1), "prompt_tokens": 22000, "completion_tokens": 7500, "total_tokens": 29500},
            {"timestamp": datetime.utcnow(), "prompt_tokens": 25000, "completion_tokens": 8200, "total_tokens": 33200},
        ]

    def track_usage(self, prompt_tokens: int, completion_tokens: int):
        with self._lock:
            now = datetime.utcnow()
            total = prompt_tokens + completion_tokens
            self._history.append({
                "timestamp": now,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total
            })
            # Limit history to last 100 entries to save memory
            if len(self._history) > 100:
                self._history.pop(0)

    def get_aggregated_usage(self, days: int = 7) -> Dict[str, int]:
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(days=days)
            prompt = 0
            completion = 0
            total = 0
            for entry in self._history:
                if entry["timestamp"] >= cutoff:
                    prompt += entry["prompt_tokens"]
                    completion += entry["completion_tokens"]
                    total += entry["total_tokens"]
            return {
                "prompt_tokens": prompt,
                "completion_tokens": completion,
                "total_tokens": total
            }

    def get_history(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._history)

_global_token_usage_service = TokenUsageService()

def get_token_usage_service() -> TokenUsageService:
    return _global_token_usage_service
