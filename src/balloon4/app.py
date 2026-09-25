from __future__ import annotations

import signal
import threading
from pathlib import Path

from balloon4.config import FlightConfig, load_config
from balloon4.hardware import HardwareContext
from balloon4.health import HealthMonitor
from balloon4.telemetry import TelemetryWriter
from balloon4.worker import SensorWorker


def _config_summary(config: FlightConfig) -> dict[str, object]:
    return {
        "gps_port": config.gps_port,
        "health_interval_seconds": config.health_interval_seconds,
        "fsync_interval_seconds": config.fsync_interval_seconds,
        "ultrasonic_echo_timeout_seconds": config.ultrasonic_echo_timeout_seconds,
        "radio_enabled": config.radio_enabled,
        "camera_enabled": config.camera_enabled,
        "sensors": {
            name: {
                "enabled": values.enabled,
                "interval_seconds": values.interval_seconds,
            }
            for name, values in config.sensors.items()
        },
    }


def run(config_path: str | Path) -> None:
    config = load_config(config_path)
    enabled = [name for name, values in config.sensors.items() if values.enabled]
    if not enabled:
        raise RuntimeError("No sensors are enabled")

    stop_event = threading.Event()

    def request_stop(_signum: int, _frame: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    writer = TelemetryWriter(
        output_root=config.output_root,
        fsync_interval_seconds=config.fsync_interval_seconds,
    )
    writer.write_manifest(_config_summary(config))
    health = HealthMonitor(enabled)
    hardware = HardwareContext()

    try:
        factories = hardware.factories(config)
        workers = [
            SensorWorker(
                name=name,
                factory=factories[name],
                writer=writer,
                health=health,
                interval_seconds=config.sensors[name].interval_seconds,
                stop_event=stop_event,
            )
            for name in enabled
        ]
        threads = [
            threading.Thread(target=worker.run, name=f"sensor-{worker.name}")
            for worker in workers
        ]

        for thread in threads:
            thread.start()

        while not stop_event.wait(config.health_interval_seconds):
            print("\nBalloon4 health")
            print(health.format_report(), flush=True)

        for thread in threads:
            thread.join(timeout=10)
    finally:
        stop_event.set()
        hardware.cleanup()
