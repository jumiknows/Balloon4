import csv
import time
from pathlib import Path

import adafruit_mcp9808
import board
import busio
from filelock import FileLock

i2c = busio.I2C(board.SCL, board.SDA)

temperature_file_path = Path(__file__).with_name("temperature_readings.csv")
temperature_lock = FileLock(str(temperature_file_path) + ".lock")


class TemperatureSensor:
    def __init__(self):
        self.initialize_file()
        try:
            self.sensor = adafruit_mcp9808.MCP9808(i2c)
        except Exception as exc:
            print(f"Error initializing MCP9808: {exc}")
            self.sensor = None

    def initialize_file(self):
        if not temperature_file_path.exists():
            with temperature_file_path.open(mode="w", newline="") as file:
                csv.writer(file).writerow(["Timestamp", "Temperature (C)"])

    def log_data(self):
        while True:
            try:
                if self.sensor is None:
                    self.sensor = adafruit_mcp9808.MCP9808(i2c)

                with temperature_lock:
                    with temperature_file_path.open(mode="a", newline="") as file:
                        writer = csv.writer(file)
                        while True:
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            temperature = self.sensor.temperature
                            writer.writerow([timestamp, temperature])
                            file.flush()
                            print(f"Temperature - {timestamp}: {temperature:.2f} C")
                            time.sleep(1)
            except Exception as exc:
                print(f"Error logging temperature: {exc}")
                self.sensor = None
                time.sleep(5)
