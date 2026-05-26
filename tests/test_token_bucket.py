import time
import pytest
from ratelimiter.algorithms.token_bucket import TokenBucketRateLimiter
from ratelimiter.backends.redis import RedisBackend

@pytest.fixture
def limiter():
    # create a fresh limiter before each test
    backend = RedisBackend(url="redis://localhost:6379")
    backend.redis_client.flushall()
    return TokenBucketRateLimiter(backend=backend, capacity=3, refill_rate=1)

class TestTokenBucket:

    def test_allows_requests_within_capacity(self, limiter):
        # 3 requests should all be allowed
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True

    def test_blocks_requests_over_capacity(self, limiter):
        # 4th request should be blocked
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True
        assert limiter.is_allowed("user_1") == False

    def test_resets_after_time(self, limiter):
        # exhaust capacity
        for _ in range(3):
            limiter.is_allowed("user_1")
        assert limiter.is_allowed("user_1") == False

        # wait for 1 token to refill (refill_rate=1 token/second)
        time.sleep(1.1)
        assert limiter.is_allowed("user_1") == True

    def test_different_users_independent(self, limiter):
        # user_1 hits limit
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True
        assert limiter.is_allowed("user_1") == False

        # user_2 unaffected
        assert limiter.is_allowed("user_2") == True

    def test_burst_up_to_capacity(self, limiter):
        # 3 requests should be allowed immediately, then block
        for _ in range(3):
            assert limiter.is_allowed("user_1") == True
        assert limiter.is_allowed("user_1") == False