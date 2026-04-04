import redis
import json
import os
from datetime import timedelta

class RedisCache:
    def __init__(self):
        self.client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    def get_cache(self, key: str):
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set_cache(self, key: str, value: dict, expire_seconds: int = 3600):
        self.client.setex(key, expire_seconds, json.dumps(value))

    def invalidate_dashboard(self):
        """ Limpa todos os caches de dashboard (útil após um novo Sync) """
        keys = self.client.keys("dash:*")
        if keys:
            self.client.delete(*keys)

# Instância global
cache_service = RedisCache()