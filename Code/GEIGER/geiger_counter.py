import csv
import time
from pathlib import Path

import RPi.GPIO as GPIO
from filelock import FileLock

geiger_file_path = Path(__file__).with_name("geiger_log.csv")
geiger_lock = FileLock(str(geiger_file_path) + ".lock")


class GeigerCounter:
    def __init__(self):
        self.initialize_file()
        self.geiger_pin = 17
        self.usvh_ratio = 0.00332
        self.tube_counts = 0

        GPIO.setup(self.geiger_pin, GPIO.IN)
        GPIO.add_event_detect(self.geiger_pin, GPIO.FALLING, callback=self.impulse)

    def initialize_file(self):
        if not geiger_file_path.exists():
            with geiger_file_path.open(mode="w", newline="") as file:
                csv.writer(file).writerow(["Time", "CPS", "uSv/h"])

    def impulse(self, _channel):
        self.tube_counts += 1

    def log_data(self):
        while True:
            try:
                start_time = time.time()
                while time.time() - start_time <= 1:
                    time.sleep(0.001)

                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                cps = self.tube_counts
                usvh = cps * 60 * self.usvh_ratio

                with geiger_lock:
                    with geiger_file_path.open(mode="a", newline="") as file:
                        csv.writer(file).writerow([current_time, cps, usvh])
                        file.flush()

                print(f"Geiger - {current_time}: {cps} CPS, {usvh} uSv/h")
                self.tube_counts = 0
            except Exception as exc:
                print(f"Error logging Geiger counter: {exc}")
                time.sleep(5)
