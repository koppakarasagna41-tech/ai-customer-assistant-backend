import logging
import time
from typing import Any

from app.schemas.retrieval import RetrievedChunk

logger = logging.getLogger("app.services.retrieval_cache")


class RetrievalCache:
    """
    Thread-safe in-memory cache for retrieved chunks.
    Saves API tokens and lowers response latency.
    """

    def __init__(self, ttl_seconds: int = 300, max_size: int = 100):
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._cache: dict[str, dict[str, Any]] = {}

    def _clean_expired(self):
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if now - v["timestamp"] > self.ttl]
        for k in expired_keys:
            del self._cache[k]

    def get(self, query: str, filters: dict | None = None) -> list[RetrievedChunk] | None:
        self._clean_expired()
        cache_key = self._generate_key(query, filters)

        entry = self._cache.get(cache_key)
        if entry:
            logger.info(f"Retrieval cache hit for query: '{query[:30]}...'")
            return entry["data"]
        return None

    def set(self, query: str, chunks: list[RetrievedChunk], filters: dict | None = None) -> None:
        self._clean_expired()

        # Eviction if max size reached
        if len(self._cache) >= self.max_size:
            # Remove oldest
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]

        cache_key = self._generate_key(query, filters)
        self._cache[cache_key] = {"timestamp": time.time(), "data": chunks}
        logger.info(f"Cached retrieval results for query: '{query[:30]}...'")

    def _generate_key(self, query: str, filters: dict | None) -> str:
        # Generate stable string key
        filter_str = ""
        if filters:
            sorted_items = sorted(filters.items())
            filter_str = ":".join([f"{k}={v}" for k, v in sorted_items])

        normalized_query = " ".join(query.strip().lower().split())
        return f"{normalized_query}||{filter_str}"

    def clear(self):
        self._cache.clear()


_retrieval_cache_instance = RetrievalCache()


def get_retrieval_cache() -> RetrievalCache:
    return _retrieval_cache_instance
