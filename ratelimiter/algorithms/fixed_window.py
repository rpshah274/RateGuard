import time
from .base import BaseRateLimiter
from ..backends.base import BaseBackend
class FixedWindowRateLimiter(BaseRateLimiter):
    def __init__(self, backend: BaseBackend, max_requests:int , window_size:int):
        self.backend = backend
        self.max_requests = max_requests
        self.window_size = window_size
        # self.counts = {}  # in-memory counts, replace with backend
    
    def is_allowed(self, user_id:int) -> bool:
        now = int(time.time())
        window_start = int(now // self.window_size)*self.window_size
        # unique key per user per window
        window_key = f"{user_id}:{window_start}"
        # increment and set TTL in same operation
        count = self.backend.increment(window_key, self.window_size)
        return count <= self.max_requests

        # Hardcoded in-memory implementation replaced by backend redis 
        
        # key = (user_id, window_start)

        # if key not in self.counts or self.counts[key][0] != window_start:
        #     self.counts[key] = (window_start, 0)

        # window_start, count = self.counts[key]
        
        # if count < self.max_requests:
        #     self.counts[key] = (window_start, count + 1)
        #     return True
        # else:
        #     return False