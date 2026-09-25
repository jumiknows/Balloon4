from __future__ import annotations

import time
from collections.abc import Callable


def wait_for_level(
    read_level: Callable[[], int],
    target: int,
    timeout_seconds: float,
    monotonic: Callable[[], float] = time.monotonic,
) -> float:
    deadline = monotonic() + timeout_seconds
    while read_level() != target:
        if monotonic() >= deadline:
            raise TimeoutError(f"GPIO did not reach level {target} before timeout")
    return monotonic()
