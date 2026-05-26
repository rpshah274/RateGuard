import time
from typing import Optional
from .base import BaseBackend

class MemoryBackend(BaseBackend):
    def __init__(self):
        # format  key -> (value, expiry_timestamp)
        self.storage = {}
    
    def _is_expired(self, key: str) -> bool:
        now = time.time()
        if key in self.storage:
            value, expiry = self.storage[key]
            if now > expiry:
                del self.storage[key]
                return True
            return False
        return True
    
    def increment(self, key, ttl):
        now = time.time()
        # if expired or not in storage, reset to 1 with new expiry time
        if self._is_expired(key):
            self.storage[key] = (1, now + ttl)
        else:
            # no need to update expiry just update value
            value, expiry = self.storage[key]
            self.storage[key] = (value + 1, expiry)
        return self.storage[key][0] 
    
    def get(self, key: str) -> Optional[int]:
        if self._is_expired(key):
            return None
        value,_ =self.storage[key]
        return value

    def expire(self, key: str, ttl: int) -> None:
        now = time.time()
        # updating expiry time         
        if key in self.storage:
            value, _ = self.storage[key]
            self.storage[key] = (value, now + ttl)

    def delete(self, key: str) -> None:
        if key in self.storage:
            del self.storage[key]
            return True