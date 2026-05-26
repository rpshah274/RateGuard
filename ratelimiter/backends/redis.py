import redis
import time
from typing import Optional
from .base import BaseBackend

class RedisBackend(BaseBackend):
    def __init__(self, url: str = "redis://localhost:6379"):
        self.redis_client = redis.Redis.from_url(url, decode_responses=True)

    def increment(self, key: str, ttl: int) -> int:
        pipeline = self.redis_client.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, ttl)
        results = pipeline.execute()
        return results[0]
    
    def get(self, key: str) -> Optional[int]:
        # get value from redis, return None if key doesn't exist else int(value)
        value = self.redis_client.get(key)
        if value is None:
            return None
        return int(value)

    def expire(self, key: str, ttl: int) -> None:
        # just set expiry on existing key
        self.redis_client.expire(key, ttl)

    def delete(self, key: str) -> None:
        # delete the key
        self.redis_client.delete(key)