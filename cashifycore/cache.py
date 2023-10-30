from caching import CashifyCache as CoreCache
from app.config import settings


# create singleton cache
class SingletonCache:
    _instance = None
    _cache = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls, cache_type: str, redis_url: str = None):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._cache = CoreCache(
                app_name=settings.app_name,
                cache_type=cache_type,
                redis_cache_url=redis_url
            )
        return cls._cache


class CashifyCache:
    _cache = None

    def __init__(self, cache_type: str, redis_url: str = None):
        self._cache = SingletonCache.instance(cache_type, redis_url)

    def cache(self):
        return self._cache
