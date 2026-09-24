import csv
import time
from pathlib import Path

import adafruit_bme680
import board
import busio
from filelock import FileLock

i2c = busio.I2C(board.SCL, board.SDA)

pressure_file_path = Path(__file__).with_name("sensor_readings.csv")
pressure_lock = FileLock(str(pressure_file_path) + ".lock")


class PressureSensor:
    def __init__(self):
        self.initialize_file()
        try:
            self.sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
        except Exception as exc:
            print(f"Error initializing BME680: {exc}")
            self.sensor = None

    def initialize_file(self):
        if not pressure_file_path.exists():
            with pressure_file_path.open(mode="w", newline="") as file:
                csv.writer(file).writerow(
                    ["Timestamp", "Temperature (C)", "Pressure (hPa)", "Humidity (RH)"]
                )

    def log_data(self):
        while True:
            try:
                if self.sensor is None:
                    self.sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

                with pressure_lock:
                    with pressure_file_path.open(mode="a", newline="") as file:
                        writer = csv.writer(file)
                        while True:
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            temperature = self.sensor.temperature
                            pressure = self.sensor.pressure
                            humidity = self.sensor.humidity
                            writer.writerow([timestamp, temperature, pressure, humidity])
                            file.flush()
                            print(
                                f"Environment - {timestamp}: "
                                f"{temperature:.2f} C, {pressure:.2f} hPa, {humidity:.2f}% RH"
                            )
                            time.sleep(1)
            except Exception as exc:
                print(f"Error logging environmental data: {exc}")
                self.sensor = None
                time.sleep(5)
