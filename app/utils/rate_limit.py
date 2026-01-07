from __future__ import annotations

import time
from collections import defaultdict, deque


class SimpleRateLimiter:
    def __init__(self, max_attempts: int = 10, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        q = self._hits[key]

        while q and now - q[0] > self.window_seconds:
            q.popleft()

        if len(q) >= self.max_attempts:
            return False

        q.append(now)
        return True


rate_limiter = SimpleRateLimiter(max_attempts=10, window_seconds=300)
