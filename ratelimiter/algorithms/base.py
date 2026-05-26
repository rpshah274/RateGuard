from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int | None = None
class BaseRateLimiter(ABC):
    @abstractmethod
    def is_allowed(self, key: str) -> bool:
        """Check if the request is allowed based on the rate limit."""
        pass