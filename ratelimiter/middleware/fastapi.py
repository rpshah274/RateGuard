from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, algorithm: str = "token_bucket"):
        super().__init__(app)
        self.algorithm = algorithm

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/check":
            return await call_next(request)
        key = request.headers.get("X-User-ID")
        algorithm = request.headers.get("X-RateLimit-Algorithm", self.algorithm).strip().lower()
        # limit = int(request.headers.get("X-RateLimit-Limit", 100))
        # window = int(request.headers.get("X-RateLimit-Window", 60))
        if not key:
            key = request.client.host
    
        if algorithm == "token_bucket":
            limiter = request.app.state.token_bucket_limiter
        elif algorithm == "sliding_window":
            limiter = request.app.state.sliding_window_limiter
        elif algorithm == "fixed_window":
            limiter = request.app.state.fixed_window_limiter
        else:
            return JSONResponse(status_code=400, content={"detail": f"Invalid algorithm : {algorithm}"})

        allowed = limiter.is_allowed(key)
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        response = await call_next(request)
        return response