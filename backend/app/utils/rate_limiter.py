from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitRule:
    max_requests: int
    window_seconds: int


class InMemoryRateLimiter:
    """
    Simple per-client sliding-window rate limiter.

    Intended for single-process development/small deployments.
    For multiple backend instances, replace with a shared store
    such as Redis.
    """

    def __init__(
        self,
        rules: dict[str, RateLimitRule],
    ) -> None:
        self.rules = rules
        self._requests: dict[
            tuple[str, str],
            deque[float],
        ] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(
        self,
        client_id: str,
        path: str,
    ) -> tuple[bool, int]:
        rule = self.rules.get(path)

        if rule is None:
            return True, 0

        now = time.monotonic()
        key = (client_id, path)

        with self._lock:
            timestamps = self._requests[key]

            cutoff = now - rule.window_seconds

            while (
                timestamps
                and timestamps[0] <= cutoff
            ):
                timestamps.popleft()

            if len(timestamps) >= rule.max_requests:
                retry_after = max(
                    1,
                    int(
                        timestamps[0]
                        + rule.window_seconds
                        - now
                    ),
                )

                return False, retry_after

            timestamps.append(now)

            return True, 0

    def reset(self) -> None:
        """
        Clear all in-memory rate-limit state.

        Primarily useful for tests.
        """
        with self._lock:
            self._requests.clear()