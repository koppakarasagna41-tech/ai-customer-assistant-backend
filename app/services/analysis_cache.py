import hashlib
import threading
from typing import Dict, Any, Optional

class AnalysisCache:
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self.max_size = max_size

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Optional[Dict[str, Any]]:
        if not text:
            return None
        key = self._hash_text(text)
        with self._lock:
            return self._cache.get(key)

    def set(self, text: str, data: Dict[str, Any]) -> None:
        if not text:
            return
        key = self._hash_text(text)
        with self._lock:
            if len(self._cache) >= self.max_size:
                # Evict an element (simple FIFO eviction for thread safety)
                first_key = next(iter(self._cache))
                self._cache.pop(first_key, None)
            self._cache[key] = data

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

_global_cache = AnalysisCache()

def get_analysis_cache() -> AnalysisCache:
    return _global_cache
