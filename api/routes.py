from pydantic import BaseModel
from fastapi import APIRouter, Request, HTTPException
from ratelimiter.algorithms.token_bucket import TokenBucketRateLimiter
from ratelimiter.algorithms.sliding_window import SlidingWindowRateLimiter
from ratelimiter.algorithms.fixed_window import FixedWindowRateLimiter
router = APIRouter()

class RateLimitRequest(BaseModel):
    key: str             #UserID
    algorithm: str       #token_bucket, sliding_window, fixed_window
    # limit: int           #Number of allowed requests
    # window: int          #Time window in seconds
    max_requests: int | None = None  #For sliding_window and fixed_window
    window_size: int | None = None    #For sliding_window and fixed_window
    capacity: int | None = None       #For token_bucket
    refill_rate: float | None = None #For token_bucket

class RateLimitResponse(BaseModel):
    allowed: bool                   #Whether the request is allowed or not T/F
    remaining: int                  #Number of remaining tokens
    retry_after: int | None =None   #Time to wait before next request

@router.post("/check", response_model=RateLimitResponse)
async def check_rate_limit(request: Request , body: RateLimitRequest):
    backend = request.app.state.backend
    if body.algorithm == "token_bucket":
        limiter = request.app.state.token_bucket_limiter
    elif body.algorithm == "sliding_window":
        limiter = request.app.state.sliding_window_limiter
    elif body.algorithm == "fixed_window":
        limiter = request.app.state.fixed_window_limiter

    if body.algorithm == "token_bucket":
        if body.capacity is None or body.refill_rate is None:
            raise HTTPException(status_code=400, detail="token_bucket requires capacity and refill_rate")
        if body.capacity <= 0 or body.refill_rate <= 0:
            raise HTTPException(status_code=400, detail="capacity and refill_rate must be greater than 0")
        limiter = TokenBucketRateLimiter(backend=backend, capacity=body.capacity, refill_rate=body.refill_rate)
        retry_after = None

    elif body.algorithm == "sliding_window":
        if body.max_requests is None or body.window_size is None:
            raise HTTPException(status_code=400, detail="sliding_window requires max_requests and window_size")
        if body.max_requests <= 0 or body.window_size <= 0:
            raise HTTPException(status_code=400, detail="max_requests and window_size must be greater than 0")
        limiter = SlidingWindowRateLimiter(backend=backend, max_requests=body.max_requests, window_size=body.window_size)
        retry_after = body.window_size
    
    elif body.algorithm == "fixed_window":
        if body.max_requests is None or body.window_size is None:
            raise HTTPException(status_code=400, detail="fixed_window requires max_requests and window_size")
        if body.max_requests <= 0 or body.window_size <= 0:
            raise HTTPException(status_code=400, detail="max_requests and window_size must be greater than 0")
        limiter = FixedWindowRateLimiter(backend=backend, max_requests=body.max_requests, window_size=body.window_size)
        retry_after = body.window_size
    else:
        raise HTTPException(status_code=400, detail=f"Invalid algorithm : {body.algorithm}")
    allowed = limiter.is_allowed(body.key)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return RateLimitResponse(allowed=allowed, remaining=0, retry_after=None if allowed else retry_after)  # body.window)