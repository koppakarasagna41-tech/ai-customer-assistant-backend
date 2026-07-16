import time
import threading
from typing import Dict, Any, Optional

class CacheService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expire_times: Dict[str, float] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                expire_at = self._expire_times.get(key, 0.0)
                if expire_at == 0.0 or expire_at > time.time():
                    return self._cache[key]
                else:
                    # Expired, clean up
                    self._cache.pop(key, None)
                    self._expire_times.pop(key, None)
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        with self._lock:
            self._cache[key] = value
            if ttl_seconds > 0:
                self._expire_times[key] = time.time() + ttl_seconds
            else:
                self._expire_times[key] = 0.0

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)
            self._expire_times.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._expire_times.clear()

_global_cache = CacheService()

def get_cache_service() -> CacheService:
    return _global_cache
