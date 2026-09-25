from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorHealth:
    state: str
    sample_count: int
    last_sample_monotonic: float | None
    last_error: str | None


class HealthMonitor:
    def __init__(self, sensor_names: list[str]) -> None:
        self._lock = threading.Lock()
        self._state = {
            name: SensorHealth("starting", 0, None, None) for name in sensor_names
        }

    def mark_sample(self, name: str) -> None:
        now = time.monotonic()
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
        now = time.monotonic()
        rows = []
        for name, status in sorted(self.snapshot().items()):
            age = "never"
            if status.last_sample_monotonic is not None:
                age = f"{now - status.last_sample_monotonic:.1f}s ago"
            detail = status.last_error or f"last sample {age}"
            rows.append(
                f"{name:<12} {status.state.upper():<9} "
                f"{status.sample_count:>6} samples  {detail}"
            )
        return "\n".join(rows)
