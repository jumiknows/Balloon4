import csv
import time
from pathlib import Path

import adafruit_gps
import serial
from filelock import FileLock

gps_file_path = Path(__file__).with_name("sensor_readings.csv")
gps_lock = FileLock(str(gps_file_path) + ".lock")


class GPSSensor:
    def __init__(self):
        self.initialize_file()
        self.uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)
        self.gps.send_command(b"PMTK314,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1")
        self.gps.send_command(b"PMTK220,1000")

    def initialize_file(self):
        if not gps_file_path.exists():
            with gps_file_path.open(mode="w", newline="") as file:
                csv.writer(file).writerow(
                    ["Timestamp", "Latitude", "Longitude", "Velocity (knots)", "Altitude (m)"]
                )

    def log_data(self):
        while True:
            try:
                with gps_lock:
                    with gps_file_path.open(mode="a", newline="") as file:
                        writer = csv.writer(file)
                        while True:
                            self.gps.update()

                            if self.gps.has_fix:
                                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                row = [
                                    timestamp,
                                    self.gps.latitude,
                                    self.gps.longitude,
                                    self.gps.speed_knots,
                                    self.gps.altitude_m,
                                ]
                                writer.writerow(row)
                                file.flush()
                                print(
                                    f"GPS - {timestamp}: "
                                    f"lat={row[1]}, lon={row[2]}, "
                                    f"speed={row[3]} knots, altitude={row[4]} m"
                                )
                            else:
                                print("GPS - waiting for fix")

                            time.sleep(1)
            except Exception as exc:
                print(f"Error logging GPS data: {exc}")
                time.sleep(5)
