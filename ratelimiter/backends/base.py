from abc import ABC, abstractmethod
from typing import Optional
class BaseBackend(ABC):
    @abstractmethod
    def increment(self, key: str, ttl: int) -> int:
        """Increment counter for key, set TTL if new. Returns new count."""
        pass
    @abstractmethod
    def get(self, key: str) -> Optional[int]:
        """Get current count for key."""
        pass
    @abstractmethod
    def expire(self, key: str, ttl: int) -> None:
        """Set TTL on a key."""
        pass
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key."""
        pass