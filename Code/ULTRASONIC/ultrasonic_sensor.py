import csv
import time
from pathlib import Path

import RPi.GPIO as GPIO
from filelock import FileLock

ultrasonic_file_path = Path(__file__).with_name("sensor_readings.csv")
ultrasonic_lock = FileLock(str(ultrasonic_file_path) + ".lock")


class UltrasonicSensor:
    def __init__(self):
        self.initialize_file()
        self.trig_pin = 12
        self.echo_pin = 13
        self.delay_time = 0.2

        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def initialize_file(self):
        if not ultrasonic_file_path.exists():
            with ultrasonic_file_path.open(mode="w", newline="") as file:
                csv.writer(file).writerow(
                    ["Timestamp", "PingTravelTime", "Distance (inches)"]
                )

    def log_data(self):
        while True:
            try:
                with ultrasonic_lock:
                    with ultrasonic_file_path.open(mode="a", newline="") as file:
                        writer = csv.writer(file)
                        while True:
                            GPIO.output(self.trig_pin, 0)
                            time.sleep(2e-6)
                            GPIO.output(self.trig_pin, 1)
                            time.sleep(10e-6)
                            GPIO.output(self.trig_pin, 0)

                            while GPIO.input(self.echo_pin) == 0:
                                pass
                            echo_start = time.time()

                            while GPIO.input(self.echo_pin) == 1:
                                pass
                            echo_stop = time.time()

                            travel_time = echo_stop - echo_start
                            distance_cm = (travel_time * 34444) / 2
                            distance_in = distance_cm * 0.3937008
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                            writer.writerow([timestamp, travel_time, distance_in])
                            file.flush()
                            print(
                                f"Ultrasonic - {timestamp}: "
                                f"{distance_in:.1f} in | {distance_cm:.1f} cm"
                            )
                            time.sleep(self.delay_time)
            except Exception as exc:
                print(f"Error logging ultrasonic sensor: {exc}")
                time.sleep(5)
