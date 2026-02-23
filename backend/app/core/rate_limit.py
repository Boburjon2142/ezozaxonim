from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status


class SimpleRateLimiter:
    def __init__(self, max_requests: int = 8, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.store = defaultdict(deque)

    def check(self, key: str) -> None:
        now = datetime.now(timezone.utc)
        q = self.store[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"code": "rate_limited", "message": "Too many requests"},
            )
        q.append(now)


rate_limiter = SimpleRateLimiter()
