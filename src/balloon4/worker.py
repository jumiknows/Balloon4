from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Protocol
import threading


class Sensor(Protocol):
    def read(self) -> Mapping[str, object]:
        ...

    def close(self) -> None:
        ...


class TelemetrySink(Protocol):
    def write(self, sensor_name: str, sample: Mapping[str, object]) -> None:
        ...


class HealthSink(Protocol):
    def mark_sample(self, name: str) -> None:
        ...

    def mark_error(self, name: str, error: BaseException) -> None:
        ...


class SensorWorker:
    def __init__(
        self,
        name: str,
        factory: Callable[[], Sensor],
        writer: TelemetrySink,
        health: HealthSink,
        interval_seconds: float,
        stop_event: threading.Event,
        retry_seconds: float = 5.0,
    ) -> None:
        self.name = name
        self.factory = factory
        self.writer = writer
        self.health = health
        self.interval_seconds = interval_seconds
        self.stop_event = stop_event
        self.retry_seconds = retry_seconds
        self.sensor: Sensor | None = None

    def step(self) -> bool:
        try:
            if self.sensor is None:
                self.sensor = self.factory()
            sample = self.sensor.read()
            self.writer.write(self.name, sample)
            self.health.mark_sample(self.name)
            return True
        except Exception as exc:
            self.health.mark_error(self.name, exc)
            self._close_sensor()
            return False

    def run(self) -> None:
        while not self.stop_event.is_set():
            succeeded = self.step()
            delay = self.interval_seconds if succeeded else self.retry_seconds
            self.stop_event.wait(delay)
        self._close_sensor()

    def _close_sensor(self) -> None:
        if self.sensor is None:
            return
        try:
            self.sensor.close()
        except Exception as exc:
            self.health.mark_error(self.name, exc)
        finally:
            self.sensor = None
