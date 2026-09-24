import sys
import threading
from pathlib import Path

import RPi.GPIO as GPIO

BASE_DIR = Path(__file__).resolve().parent

for module_dir in ("MCP9808", "BN0085", "BME680", "GEIGER", "ULTRASONIC", "GPS"):
    sys.path.insert(0, str(BASE_DIR / module_dir))

from temperature_sensor import TemperatureSensor
from gyroscope_sensor import GyroscopeSensor
from pressure_sensor import PressureSensor
from geiger_counter import GeigerCounter
from ultrasonic_sensor import UltrasonicSensor
from gps_sensor import GPSSensor
from csv_reader import read_csv_files


def main():
    GPIO.setmode(GPIO.BCM)

    sensors = [
        TemperatureSensor(),
        GyroscopeSensor(),
        PressureSensor(),
        GeigerCounter(),
        UltrasonicSensor(),
        GPSSensor(),
    ]

    threads = [threading.Thread(target=sensor.log_data) for sensor in sensors]
    threads.append(threading.Thread(target=read_csv_files))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
