from __future__ import annotations

import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorHealth:
    state: str
    sample_count: int
    last_sample_monotonic: float | None
    last_error: str | None


class HealthMonitor:
    def __init__(
        self,
        sensor_names: list[str],
        stale_after_seconds: Mapping[str, float] | None = None,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._lock = threading.Lock()
        self._monotonic = monotonic
        self._stale_after_seconds = dict(stale_after_seconds or {})
        self._state = {
            name: SensorHealth("starting", 0, None, None) for name in sensor_names
        }

    def mark_sample(self, name: str) -> None:
        now = self._monotonic()
        with self._lock:
            current = self._state[name]
            self._state[name] = SensorHealth(
                state="healthy",
                sample_count=current.sample_count + 1,
                last_sample_monotonic=now,
                last_error=None,
            )

    def mark_error(self, name: str, error: BaseException) -> None:
        with self._lock:
            current = self._state[name]
            self._state[name] = SensorHealth(
                state="degraded",
                sample_count=current.sample_count,
                last_sample_monotonic=current.last_sample_monotonic,
                last_error=f"{type(error).__name__}: {error}",
            )

    def snapshot(self) -> dict[str, SensorHealth]:
        with self._lock:
            return dict(self._state)

    def format_report(self) -> str:
        now = self._monotonic()
        rows = []
        for name, status in sorted(self.snapshot().items()):
            age_seconds = None
            age = "never"
            if status.last_sample_monotonic is not None:
                age_seconds = max(0.0, now - status.last_sample_monotonic)
                age = f"{age_seconds:.1f}s ago"

            display_state = status.state
            stale_after = self._stale_after_seconds.get(name)
            if (
                display_state == "healthy"
                and age_seconds is not None
                and stale_after is not None
                and age_seconds > stale_after
            ):
                display_state = "stale"

            detail = status.last_error or f"last sample {age}"
            rows.append(
                f"{name:<12} {display_state.upper():<9} "
                f"{status.sample_count:>6} samples  {detail}"
            )
        return "\n".join(rows)
