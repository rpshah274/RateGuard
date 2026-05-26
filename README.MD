# RateGuard

RateGuard is a distributed rate limiting service built with FastAPI and Redis.

It supports multiple rate limiting algorithms and exposes a simple API for checking whether a request should be allowed or blocked.

## Features

- Token Bucket rate limiting
- Sliding Window rate limiting
- Fixed Window rate limiting
- Redis-backed shared state
- FastAPI middleware support
- `/check` endpoint for manual checks
- Locust benchmark support
- Docker Compose setup

## Tech Stack

- Python
- FastAPI
- Redis
- Docker
- Locust
- Pytest

## API

### Health Check
```http
GET /health
```

### Check Rate Limit
```http
POST /check
```

### Token bucket example:
```json 
{
  "key": "user_123",
  "algorithm": "token_bucket",
  "capacity": 3,
  "refill_rate": 1
}
```

### Sliding window example:
```json
{
  "key": "user_123",
  "algorithm": "sliding_window",
  "max_requests": 100,
  "window_size": 60
}
```

### Fixed window example:
```json
{
  "key": "user_123",
  "algorithm": "fixed_window",
  "max_requests": 100,
  "window_size": 60
}
```
### Responses:
when the request is allowed.
```text
200 OK 
```
when the request is rate limited.
```text
429 Too Many Requests
```

## Run Locally
Start Redis:
```powershell
docker compose up redis
```

Start the API:
```powershell
uvicorn api.main:app --reload
```

Open API docs:
```text
http://localhost:8000/docs
```

Run With Docker Compose
```bash
docker compose up --build
```

API will be available at: http://localhost:8000

## Run Tests
Make sure Redis is running, then:

```powershell
pytest tests/
```

For code coverage:
```bash
pytest tests/ --cov=ratelimiter --cov-report=term-missing
```
## Test Coverage

| Module | Statements | Coverage |
|---|---|---|
| algorithms/fixed_window.py | 14 | 100% |
| algorithms/sliding_window.py | 20 | 100% |
| algorithms/token_bucket.py | 15 | 100% |
| backends/memory.py | 36 | 64% |
| backends/redis.py | 22 | 50% |
| middleware/fastapi.py | 26 | 0% |
| **Total** | **166** | **67%** |

## Run Benchmarks
Start the API, then run Locust:

```powershell
locust -f benchmarks/locustfile.py --host http://localhost:8000
```

Open Locust UI:
```text
http://localhost:8089
```

Suggested test:
```text
Users: 30
Ramp up: 10
Run time: 2m
```

## Project Structure
```text
api/                  FastAPI app and routes
ratelimiter/          Rate limiting algorithms, backends, middleware
benchmarks/           Locust benchmark file
tests/                Pytest test suite
docker-compose.yml    API + Redis services
Dockerfile            API container image
```
## Algorithms
### Token Bucket
Allows bursts up to a configured capacity and refills tokens over time.

### Sliding Window
Tracks request timestamps and allows only a maximum number of requests within a rolling time window.

### Fixed Window
Counts requests in fixed time windows and resets when the window changes.

## Benchmark Results

Tested with Locust — 50 users, 60 seconds

| Metric | Value |
|---|---|
| Requests/sec | 150 |
| Median latency | 7ms |
| p95 latency | 16ms |
| p99 latency | 25ms |
| Rate limited (429s) | ~49% |

## Current Limitations
- `remaining` field in response is hardcoded to 0 — full token counting not yet implemente
