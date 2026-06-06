"""In-memory TTL cache for external API responses."""

import time
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        ts, value = entry
        if time.time() - ts > self.ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any):
        self._store[key] = (time.time(), value)

    def clear(self):
        self._store.clear()


tomtom_cache = TTLCache(ttl_seconds=300)
groq_cache = TTLCache(ttl_seconds=3600)
