import threading

from balloon4.health import HealthMonitor
from balloon4.worker import SensorWorker


class RecordingWriter:
    def __init__(self):
        self.rows = []

    def write(self, sensor_name, sample):
        self.rows.append((sensor_name, dict(sample)))


class FakeSensor:
    def __init__(self, sample=None, error=None):
        self.sample = sample or {"value": 1}
        self.error = error
        self.closed = False

    def read(self):
        if self.error is not None:
            error = self.error
            self.error = None
            raise error
        return self.sample

    def close(self):
        self.closed = True


def make_worker(factory):
    writer = RecordingWriter()
    health = HealthMonitor(["test"])
    worker = SensorWorker(
        name="test",
        factory=factory,
        writer=writer,
        health=health,
        interval_seconds=1.0,
        stop_event=threading.Event(),
        retry_seconds=0.01,
    )
    return worker, writer, health


def test_worker_recovers_after_factory_failure():
    attempts = 0

    def factory():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("device missing")
        return FakeSensor({"temperature_c": 21.5})

    worker, writer, health = make_worker(factory)

    assert worker.step() is False
    assert health.snapshot()["test"].state == "degraded"

    assert worker.step() is True
    assert writer.rows == [("test", {"temperature_c": 21.5})]
    status = health.snapshot()["test"]
    assert status.state == "healthy"
    assert status.sample_count == 1


def test_worker_recreates_sensor_after_read_failure():
    sensors = [
        FakeSensor(error=OSError("serial disconnected")),
        FakeSensor({"has_fix": True}),
    ]

    def factory():
        return sensors.pop(0)

    worker, writer, health = make_worker(factory)

    assert worker.step() is False
    assert worker.sensor is None
    assert worker.step() is True

    assert writer.rows == [("test", {"has_fix": True})]
    assert health.snapshot()["test"].sample_count == 1
