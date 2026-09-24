import csv
import time
from pathlib import Path

import board
import busio
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
)
from adafruit_bno08x.i2c import BNO08X_I2C
from filelock import FileLock

i2c = busio.I2C(board.SCL, board.SDA)

sensor_file_path = Path(__file__).with_name("sensor_readings.csv")
sensor_lock = FileLock(str(sensor_file_path) + ".lock")


class GyroscopeSensor:
    def __init__(self):
        self.initialize_file()
        self.sensor = None
        self.initialize_sensor()

    def initialize_file(self):
        if not sensor_file_path.exists():
            with sensor_file_path.open(mode="w", newline="") as file:
                csv.writer(file).writerow(
                    [
                        "Timestamp",
                        "Accel X",
                        "Accel Y",
                        "Accel Z",
                        "Gyro X",
                        "Gyro Y",
                        "Gyro Z",
                        "Magnet X",
                        "Magnet Y",
                        "Magnet Z",
                    ]
                )

    def initialize_sensor(self):
        try:
            self.sensor = BNO08X_I2C(i2c)
            self.sensor.enable_feature(BNO_REPORT_ACCELEROMETER)
            self.sensor.enable_feature(BNO_REPORT_GYROSCOPE)
            self.sensor.enable_feature(BNO_REPORT_MAGNETOMETER)
        except Exception as exc:
            print(f"Error initializing BNO08X: {exc}")
            self.sensor = None

    def log_data(self):
        while True:
            try:
                if self.sensor is None:
                    self.initialize_sensor()
                if self.sensor is None:
                    time.sleep(5)
                    continue

                with sensor_lock:
                    with sensor_file_path.open(mode="a", newline="") as file:
                        writer = csv.writer(file)
                        while True:
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            accel = self.sensor.acceleration
                            gyro = self.sensor.gyro
                            magnet = self.sensor.magnetic
                            writer.writerow([timestamp, *accel, *gyro, *magnet])
                            file.flush()
                            print(
                                f"Motion - {timestamp}: "
                                f"accel={accel}, gyro={gyro}, magnet={magnet}"
                            )
                            time.sleep(1)
            except Exception as exc:
                print(f"Error logging motion sensors: {exc}")
                self.sensor = None
                time.sleep(5)
