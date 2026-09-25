from __future__ import annotations

import argparse
import csv
from pathlib import Path

from balloon4.app import run
from balloon4.config import load_config


def _latest_run(output_root: Path) -> Path | None:
    runs = sorted((path for path in output_root.glob("*") if path.is_dir()), reverse=True)
    return runs[0] if runs else None


def _last_csv_row(path: Path) -> list[str] | None:
    if not path.exists():
        return None
    with path.open(newline="") as file:
        rows = csv.reader(file)
        next(rows, None)
        last = None
        for row in rows:
            last = row
    return last


def command_check(config_path: str) -> int:
    config = load_config(config_path)
    print(f"Config OK: {Path(config_path).resolve()}")
    print(f"Output: {config.output_root}")
    for name, sensor in sorted(config.sensors.items()):
        state = "enabled" if sensor.enabled else "disabled"
        print(f"{name:<12} {state:<8} {sensor.interval_seconds:g}s")
    if config.radio_enabled:
        print("Radio is enabled in configuration but requires hardware validation.")
    if config.camera_enabled:
        print("Camera is enabled in configuration but is not started by the core logger.")
    return 0


def command_status(config_path: str) -> int:
    config = load_config(config_path)
    run_dir = _latest_run(config.output_root)
    if run_dir is None:
        print("No Balloon4 runs found.")
        return 1

    print(f"Latest run: {run_dir.name}")
    for path in sorted(run_dir.glob("*.csv")):
        last = _last_csv_row(path)
        print(f"{path.stem:<12} {last if last is not None else 'no samples'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="balloon4")
    parser.add_argument(
        "--config",
        default="config/flight.toml",
        help="Path to the flight TOML configuration.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run", help="Run the flight logger.")
    subparsers.add_parser("check", help="Validate configuration without touching hardware.")
    subparsers.add_parser("status", help="Show the last row from the latest run.")

    args = parser.parse_args()
    if args.command == "run":
        run(args.config)
        return 0
    if args.command == "check":
        return command_check(args.config)
    return command_status(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
