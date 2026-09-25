import pytest

from balloon4.config import load_config


BASE_CONFIG = """
[flight]
output_root = "data"
health_interval_seconds = 10
fsync_interval_seconds = 5

[gps]
port = "/dev/serial0"

[ultrasonic]
echo_timeout_seconds = 0.05

[sensors.temperature]
enabled = true
interval_seconds = 1

[sensors.environment]
enabled = true
interval_seconds = 1

[sensors.imu]
enabled = true
interval_seconds = 1

[sensors.geiger]
enabled = true
interval_seconds = 1

[sensors.ultrasonic]
enabled = true
interval_seconds = 0.2

[sensors.gps]
enabled = true
interval_seconds = 1
"""


def write_config(tmp_path, text: str):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = config_dir / "flight.toml"
    path.write_text(text)
    return path


def test_load_config_resolves_output_relative_to_project_root(tmp_path):
    path = write_config(tmp_path, BASE_CONFIG)
    config = load_config(path)

    assert config.output_root == tmp_path / "data"
    assert config.gps_port == "/dev/serial0"
    assert config.sensors["ultrasonic"].interval_seconds == 0.2
    assert config.radio_enabled is False


def test_load_config_rejects_non_positive_sensor_interval(tmp_path):
    invalid = BASE_CONFIG.replace("interval_seconds = 0.2", "interval_seconds = 0")
    path = write_config(tmp_path, invalid)

    with pytest.raises(ValueError, match="interval_seconds"):
        load_config(path)


def test_load_config_requires_all_core_sensor_entries(tmp_path):
    marker = """
[sensors.gps]
enabled = true
interval_seconds = 1
"""
    path = write_config(tmp_path, BASE_CONFIG.replace(marker, ""))

    with pytest.raises(ValueError, match="Missing sensor configuration"):
        load_config(path)
