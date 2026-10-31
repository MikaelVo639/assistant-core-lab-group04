"""A tiny in-memory rate limiter (per client, per minute). Enough to teach the idea of 429.

shortcut: state is per process, so N workers allow N x the limit; move to Redis when scaling out.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, per_minute: int):
        self.per_minute = per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()  # sync endpoints run in a thread pool

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            for k in [k for k, q in self._hits.items() if now - q[-1] > 60]:  # forget idle clients: bounded memory
                del self._hits[k]
            q = self._hits[key]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= self.per_minute:
                return False
            q.append(now)
            return True
