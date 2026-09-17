"""Redis based cache storage"""
from django.core.cache import cache

__all__ = ('CACHE',)


class _CacheStorage:
    def __init__(self, timeout: int = 3600):
        self.timeout = timeout

    def get(self, key):
        """Get value from cache"""
        return cache.get(f"hdrezka:{key}")

    def set(self, key, value):
        """Store some cache"""
        cache.set(f"hdrezka:{key}", value, timeout=self.timeout)


CACHE = _CacheStorage()
