import time
from collections import deque
from .base import BaseRateLimiter
from ..backends.base import BaseBackend
class SlidingWindowRateLimiter(BaseRateLimiter):
    def __init__(self, backend: BaseBackend, max_requests: int, window_size: int):
        self.backend = backend
        self.redis_client = backend.redis_client
        self.max_requests = max_requests
        self.window_size = window_size
        # self.log = {}  # in-memory log, replace with backend redis sorted set

    def is_allowed(self, key:str) -> bool:
        now = time.time()
        # cutoff to check howmany requests were made in the current window
        cutoff = now - self.window_size

        # remove all timestamps that are outside the current window
        self.redis_client.zremrangebyscore(key,0,cutoff) 
        # count remaining timestamp in window
        count = self.redis_client.zcard(key) 
        if count >= self.max_requests:
            return False
        # add current timestamp 
        self.redis_client.zadd(key,{str(now):now})
        # set expiry on the key to avoid memory leak
        self.redis_client.expire(key,self.window_size)
        return True 

        # Asigning unique bucket if key not in log
        # if key not in self.log:
        #     self.log[key] = deque()
        # log = self.log[key]
        # # Remove timestamps that are outside the current window
        # while log and log[0] <= cutoff:
        #     log.popleft()
        # # Checking if the number of requests (i.e. len of queue) is less than the maximum allowed    
        # if len(log) < self.max_requests:
        #     self.log[key].append(now)
        #     return True
        # else:
        #     return False