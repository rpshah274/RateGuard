import time
import pytest
from ratelimiter.algorithms.fixed_window import FixedWindowRateLimiter
from ratelimiter.backends.memory import MemoryBackend

@pytest.fixture
def limiter():
    # create a fresh limiter before each test
    backend = MemoryBackend()
    # backend = RedisBackend(url="redis://localhost:6379")
    # backend.redis_client.flushall()
    return FixedWindowRateLimiter(backend=backend, max_requests=3, window_size=60)

class TestFixedWindow:

    def test_allows_requests_within_limit(self, limiter):
        # 3 requests should all be allowed
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True

    def test_blocks_requests_over_limit(self, limiter):
        # 4th request should be blocked
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True
        assert limiter.is_allowed("user_1") == False

    def test_resets_after_window_expires(self, limiter):
        # exhaust limit
        for _ in range(3):
            limiter.is_allowed("user_1") == True
        assert limiter.is_allowed("user_1") == False

        # force window to expire by manipulating time
        # we use a tiny window_size to make this practical
        backend = MemoryBackend()
        fast_limiter = FixedWindowRateLimiter(backend=backend, max_requests=3, window_size=1)
        
        for _ in range(3):
            fast_limiter.is_allowed("user_1") == True
        assert fast_limiter.is_allowed("user_1") == False

        time.sleep(1.1)  # wait for window to expire
        assert fast_limiter.is_allowed("user_1") == True  # should reset

    def test_different_users_independent(self, limiter):
        # user_1 hits limit
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True
        assert limiter.is_allowed("user_1") == False

        # user_2 unaffected
        assert limiter.is_allowed("user_2") == True

    def test_exactly_at_limit(self, limiter):
        # 3rd request should still be allowed
        limiter.is_allowed("user_1")
        limiter.is_allowed("user_1")
        assert limiter.is_allowed("user_1") == True  # exactly at limit