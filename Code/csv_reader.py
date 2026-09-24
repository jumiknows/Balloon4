import csv
import time
from pathlib import Path

from filelock import FileLock

BASE_DIR = Path(__file__).resolve().parent

file_paths = [
    BASE_DIR / "MCP9808" / "temperature_readings.csv",
    BASE_DIR / "BN0085" / "sensor_readings.csv",
    BASE_DIR / "BME680" / "sensor_readings.csv",
    BASE_DIR / "GEIGER" / "geiger_log.csv",
    BASE_DIR / "ULTRASONIC" / "sensor_readings.csv",
    BASE_DIR / "GPS" / "sensor_readings.csv",
]

file_locks = [FileLock(str(path) + ".lock") for path in file_paths]


def read_csv_files():
    while True:
        try:
            for file_path, file_lock in zip(file_paths, file_locks):
                with file_lock:
                    if not file_path.exists():
                        continue

                    with file_path.open(mode="r", newline="") as file:
                        reader = csv.reader(file)
                        last_row = None
                        for last_row in reader:
                            pass

                        if last_row:
                            print(f"Last entry in {file_path}: {last_row}")

            time.sleep(10)
        except Exception as exc:
            print(f"Error reading CSV files: {exc}")
            time.sleep(5)
