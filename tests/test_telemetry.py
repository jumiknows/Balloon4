import csv
import json

import pytest

from balloon4.telemetry import TelemetryWriter


def test_writer_creates_run_manifest_and_sensor_csv(tmp_path):
    writer = TelemetryWriter(
        output_root=tmp_path,
        fsync_interval_seconds=999,
        run_id="test-run",
    )

    writer.write_manifest({"gps_port": "/dev/serial0"})
    writer.write("temperature", {"temperature_c": 21.5})
    writer.write("temperature", {"temperature_c": 21.75})

    manifest = json.loads((writer.run_dir / "manifest.json").read_text())
    assert manifest["run_id"] == "test-run"
    assert manifest["config"]["gps_port"] == "/dev/serial0"

    with (writer.run_dir / "temperature.csv").open(newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["temperature_c"] == "21.5"
    assert rows[0]["timestamp_utc"].endswith("+00:00")
    assert float(rows[1]["elapsed_seconds"]) >= float(rows[0]["elapsed_seconds"])


def test_writer_rejects_schema_changes(tmp_path):
    writer = TelemetryWriter(
        output_root=tmp_path,
        fsync_interval_seconds=999,
        run_id="test-run",
    )
    writer.write("gps", {"has_fix": False, "latitude": None})

    with pytest.raises(ValueError, match="telemetry fields changed"):
        writer.write("gps", {"latitude": None, "has_fix": False})
