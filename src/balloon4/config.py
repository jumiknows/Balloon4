from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SensorConfig:
    enabled: bool
    interval_seconds: float


@dataclass(frozen=True)
class FlightConfig:
    output_root: Path
    health_interval_seconds: float
    fsync_interval_seconds: float
    gps_port: str
    ultrasonic_echo_timeout_seconds: float
    sensors: dict[str, SensorConfig]
    radio_enabled: bool
    camera_enabled: bool


def load_config(path: str | Path) -> FlightConfig:
    config_path = Path(path).resolve()
    with config_path.open("rb") as file:
        raw = tomllib.load(file)

    project_root = config_path.parent.parent
    flight = raw.get("flight", {})
    sensor_table = raw.get("sensors", {})

    sensors: dict[str, SensorConfig] = {}
    for name, values in sensor_table.items():
        interval = float(values.get("interval_seconds", 1.0))
        if interval <= 0:
            raise ValueError(f"{name}.interval_seconds must be greater than zero")
        sensors[name] = SensorConfig(
            enabled=bool(values.get("enabled", True)),
            interval_seconds=interval,
        )

    required = {"temperature", "environment", "imu", "geiger", "ultrasonic", "gps"}
    missing = required.difference(sensors)
    if missing:
        raise ValueError(f"Missing sensor configuration: {', '.join(sorted(missing))}")

    output_root = Path(flight.get("output_root", "data"))
    if not output_root.is_absolute():
        output_root = project_root / output_root

    health_interval = float(flight.get("health_interval_seconds", 10.0))
    fsync_interval = float(flight.get("fsync_interval_seconds", 5.0))
    echo_timeout = float(raw.get("ultrasonic", {}).get("echo_timeout_seconds", 0.05))

    if health_interval <= 0 or fsync_interval <= 0 or echo_timeout <= 0:
        raise ValueError("Flight timing values must be greater than zero")

    return FlightConfig(
        output_root=output_root,
        health_interval_seconds=health_interval,
        fsync_interval_seconds=fsync_interval,
        gps_port=str(raw.get("gps", {}).get("port", "/dev/serial0")),
        ultrasonic_echo_timeout_seconds=echo_timeout,
        sensors=sensors,
        radio_enabled=bool(raw.get("radio", {}).get("enabled", False)),
        camera_enabled=bool(raw.get("camera", {}).get("enabled", False)),
    )
