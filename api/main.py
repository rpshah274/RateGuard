import os
from fastapi import FastAPI
from api.routes import router
from contextlib import asynccontextmanager
from ratelimiter.backends.redis import RedisBackend
from ratelimiter.algorithms.token_bucket import TokenBucketRateLimiter
from ratelimiter.algorithms.sliding_window import SlidingWindowRateLimiter
from ratelimiter.algorithms.fixed_window import FixedWindowRateLimiter
from ratelimiter.middleware.fastapi import RateLimitMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    # backend = RedisBackend(url="redis://localhost:6379")
    backend = RedisBackend(url=os.getenv("REDIS_URL", "redis://localhost:6379"))
    app.state.backend = backend
    app.state.token_bucket_limiter = TokenBucketRateLimiter(backend=backend, capacity=3, refill_rate=1)
    app.state.sliding_window_limiter = SlidingWindowRateLimiter(backend=backend, max_requests=100, window_size=60)
    app.state.fixed_window_limiter = FixedWindowRateLimiter(backend=backend, max_requests=100, window_size=60)
    yield

app = FastAPI(
    title = 'RateGuard',
    description = 'Distributed Rate Limiting Service built with FastAPI and Redis',
    version = '1.0.0',
    lifespan = lifespan
)

app.add_middleware(RateLimitMiddleware, algorithm="token_bucket")
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "RateGuard API is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}