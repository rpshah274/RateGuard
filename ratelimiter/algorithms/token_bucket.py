import time
from .base import BaseRateLimiter
from ..backends.base import BaseBackend
LUA_SCRIPT = """     
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local ttl = tonumber (ARGV[4])
        
        local data = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(data[1])
        local last_refill = tonumber(data[2])

        if tokens == nil then
            tokens = capacity
            last_refill = now
        end

        local elapsed = now - last_refill
        local new_tokens = tokens + (elapsed * refill_rate)

        if new_tokens > capacity then
            new_tokens = capacity
        end

        if new_tokens < 1 then
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('EXPIRE', key, ttl)
            return {0, new_tokens}
        else
            new_tokens = new_tokens - 1
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('EXPIRE', key, ttl)
            return {1, new_tokens}
        end
"""
class TokenBucketRateLimiter(BaseRateLimiter):
    def __init__(self, backend: BaseBackend, capacity: int, refill_rate: float):
        self.redis_client = backend.redis_client
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.script = self.redis_client.register_script(LUA_SCRIPT)

        # self.buckets = {} # In-memory bucket state: {key: (tokens, last_refill_time)}

    def is_allowed(self, key:str) -> bool:

        # Here we can get race conditions to solve using redis we use Lua script to make it atomic
        now = int(time.time())
        ttl = int(self.capacity / self.refill_rate)*2 
        # result = self.script(keys=[key],args=[self.capacity, self.refill_rate , now , ttl])
        result = self.script(keys=[f"tb:{key}"], args=[self.capacity, self.refill_rate, now, ttl])
        # allowed = bool(result[0])
        # remaining = int(float(result[1]))

        # return RateLimitResult(
        #     allowed=allowed,
        #     remaining=remaining,
        #     retry_after=None if allowed else 1
        # )
        return  bool(result[0])
    
        # Asigning unique bucket to new user
        # if key not in self.buckets:
        #     self.buckets[key] = (self.capacity, now)  # (current tokens, last refill time)
        # tokens,last_refill_time = self.buckets[key]
        # # Calculate the number of tokens to add based on the time elapsed since the last refill
        # elapsed_time = now - last_refill_time
        # tokens += int(elapsed_time * self.refill_rate)
        
        # tokens = min(tokens, self.capacity)  # Ensure tokens do not exceed capacity

        # if tokens < 1:
        #     self.buckets[key] = (tokens,now)
        #     return False
        # # If there are enough tokens, consume one and update the bucket
        # self.buckets[key] = (tokens - 1, now)
        # return True