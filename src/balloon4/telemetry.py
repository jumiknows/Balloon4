from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys
import threading
import time
from typing import Mapping
import uuid


class TelemetryWriter:
    def __init__(
        self,
        output_root: Path,
        fsync_interval_seconds: float,
        run_id: str | None = None,
    ) -> None:
        self.started_monotonic = time.monotonic()
        self.started_utc = datetime.now(timezone.utc)
        self.run_id = run_id or (
            self.started_utc.strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
        )
        self.run_dir = output_root / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.fsync_interval_seconds = fsync_interval_seconds
        self._locks: dict[str, threading.Lock] = {}
        self._fields: dict[str, list[str]] = {}
        self._last_fsync: dict[str, float] = {}

    def write_manifest(self, config_summary: Mapping[str, object]) -> None:
        manifest = {
            "run_id": self.run_id,
            "started_utc": self.started_utc.isoformat(),
            "hostname": platform.node(),
            "python": sys.version.split()[0],
            "software_commit": os.getenv("BALLOON4_COMMIT", "unknown"),
            "config": dict(config_summary),
        }
        path = self.run_dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    def write(self, sensor_name: str, sample: Mapping[str, object]) -> None:
        lock = self._locks.setdefault(sensor_name, threading.Lock())
        with lock:
            sample_fields = list(sample.keys())
            expected_fields = self._fields.get(sensor_name)
            if expected_fields is None:
                self._fields[sensor_name] = sample_fields
            elif sample_fields != expected_fields:
                raise ValueError(
                    f"{sensor_name} telemetry fields changed from "
                    f"{expected_fields} to {sample_fields}"
                )

            path = self.run_dir / f"{sensor_name}.csv"
            is_new = not path.exists()
            elapsed = time.monotonic() - self.started_monotonic
            timestamp = datetime.now(timezone.utc).isoformat()
            row = {
                "timestamp_utc": timestamp,
                "elapsed_seconds": f"{elapsed:.3f}",
                **sample,
            }
            fields = ["timestamp_utc", "elapsed_seconds", *sample_fields]

            with path.open("a", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                if is_new:
                    writer.writeheader()
                writer.writerow(row)
                file.flush()

                now = time.monotonic()
                last_fsync = self._last_fsync.get(sensor_name, 0.0)
                if now - last_fsync >= self.fsync_interval_seconds:
                    os.fsync(file.fileno())
                    self._last_fsync[sensor_name] = now
