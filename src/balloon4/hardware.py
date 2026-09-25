from __future__ import annotations

from collections.abc import Callable, Mapping
import threading
import time

from balloon4.config import FlightConfig
from balloon4.sensors.ultrasonic import wait_for_level


class _NoopClose:
    def close(self) -> None:
        return None


class LockedSensor(_NoopClose):
    def __init__(self, sensor: object, lock: threading.Lock) -> None:
        self.sensor = sensor
        self.lock = lock

    def read(self) -> Mapping[str, object]:
        with self.lock:
            return self.sensor.read()  # type: ignore[attr-defined]

    def close(self) -> None:
        close = getattr(self.sensor, "close", None)
        if callable(close):
            close()


class MCP9808Sensor(_NoopClose):
    def __init__(self, device: object) -> None:
        self.device = device

    def read(self) -> Mapping[str, object]:
        return {"temperature_c": float(self.device.temperature)}  # type: ignore[attr-defined]


class BME680Sensor(_NoopClose):
    def __init__(self, device: object) -> None:
        self.device = device

    def read(self) -> Mapping[str, object]:
        return {
            "temperature_c": float(self.device.temperature),  # type: ignore[attr-defined]
            "pressure_hpa": float(self.device.pressure),  # type: ignore[attr-defined]
            "humidity_rh": float(self.device.humidity),  # type: ignore[attr-defined]
        }


class BNO08XSensor(_NoopClose):
    def __init__(self, device: object) -> None:
        self.device = device

    def read(self) -> Mapping[str, object]:
        acceleration = self.device.acceleration  # type: ignore[attr-defined]
        gyro = self.device.gyro  # type: ignore[attr-defined]
        magnetic = self.device.magnetic  # type: ignore[attr-defined]
        return {
            "accel_x": acceleration[0],
            "accel_y": acceleration[1],
            "accel_z": acceleration[2],
            "gyro_x": gyro[0],
            "gyro_y": gyro[1],
            "gyro_z": gyro[2],
            "magnetic_x": magnetic[0],
            "magnetic_y": magnetic[1],
            "magnetic_z": magnetic[2],
        }


class GPSSensor:
    def __init__(self, serial_module: object, gps_module: object, port: str) -> None:
        self.uart = serial_module.Serial(port, baudrate=9600, timeout=10)  # type: ignore[attr-defined]
        self.gps = gps_module.GPS(self.uart, debug=False)  # type: ignore[attr-defined]
        self.gps.send_command(b"PMTK314,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1")
        self.gps.send_command(b"PMTK220,1000")

    def read(self) -> Mapping[str, object]:
        self.gps.update()
        return {
            "has_fix": bool(self.gps.has_fix),
            "latitude": self.gps.latitude if self.gps.has_fix else None,
            "longitude": self.gps.longitude if self.gps.has_fix else None,
            "speed_knots": self.gps.speed_knots if self.gps.has_fix else None,
            "altitude_m": self.gps.altitude_m if self.gps.has_fix else None,
        }

    def close(self) -> None:
        self.uart.close()


class GeigerSensor(_NoopClose):
    def __init__(self, gpio: object, pin: int = 17, dose_ratio_per_cpm: float = 0.00332) -> None:
        self.gpio = gpio
        self.pin = pin
        self.dose_ratio_per_cpm = dose_ratio_per_cpm
        self._count = 0
        self._count_lock = threading.Lock()
        self.gpio.setup(self.pin, self.gpio.IN)
        self.gpio.add_event_detect(self.pin, self.gpio.FALLING, callback=self._impulse)

    def _impulse(self, _channel: int) -> None:
        with self._count_lock:
            self._count += 1

    def read(self) -> Mapping[str, object]:
        with self._count_lock:
            cps = self._count
            self._count = 0
        return {
            "counts_per_second": cps,
            "dose_rate_usvh": cps * 60 * self.dose_ratio_per_cpm,
        }

    def close(self) -> None:
        try:
            self.gpio.remove_event_detect(self.pin)
        except Exception:
            pass


class UltrasonicSensor(_NoopClose):
    def __init__(
        self,
        gpio: object,
        trig_pin: int = 12,
        echo_pin: int = 13,
        echo_timeout_seconds: float = 0.05,
    ) -> None:
        self.gpio = gpio
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.echo_timeout_seconds = echo_timeout_seconds
        self.gpio.setup(self.trig_pin, self.gpio.OUT)
        self.gpio.setup(self.echo_pin, self.gpio.IN)

    def read(self) -> Mapping[str, object]:
        self.gpio.output(self.trig_pin, 0)
        time.sleep(2e-6)
        self.gpio.output(self.trig_pin, 1)
        time.sleep(10e-6)
        self.gpio.output(self.trig_pin, 0)

        echo_start = wait_for_level(
            lambda: self.gpio.input(self.echo_pin),
            target=1,
            timeout_seconds=self.echo_timeout_seconds,
        )
        echo_stop = wait_for_level(
            lambda: self.gpio.input(self.echo_pin),
            target=0,
            timeout_seconds=self.echo_timeout_seconds,
        )

        travel_seconds = echo_stop - echo_start
        distance_cm = travel_seconds * 34444.0 / 2
        return {
            "echo_seconds": travel_seconds,
            "distance_cm": distance_cm,
            "distance_in": distance_cm * 0.3937008,
        }


class HardwareContext:
    def __init__(self) -> None:
        try:
            import board
            import busio
            import RPi.GPIO as GPIO
        except ImportError as exc:
            raise RuntimeError(
                "Raspberry Pi hardware libraries are unavailable. "
                "Install the hardware extra on the Pi."
            ) from exc

        self.board = board
        self.busio = busio
        self.gpio = GPIO
        self.gpio.setmode(self.gpio.BCM)
        self._i2c: object | None = None
        self._i2c_lock = threading.Lock()
        self._bus_creation_lock = threading.Lock()

    def _get_i2c(self) -> object:
        with self._bus_creation_lock:
            if self._i2c is None:
                self._i2c = self.busio.I2C(self.board.SCL, self.board.SDA)
            return self._i2c

    def _i2c_factory(self, builder: Callable[[object], object]) -> Callable[[], LockedSensor]:
        def factory() -> LockedSensor:
            with self._i2c_lock:
                sensor = builder(self._get_i2c())
            return LockedSensor(sensor, self._i2c_lock)

        return factory

    def factories(self, config: FlightConfig) -> dict[str, Callable[[], object]]:
        def temperature_builder(i2c: object) -> MCP9808Sensor:
            import adafruit_mcp9808

            return MCP9808Sensor(adafruit_mcp9808.MCP9808(i2c))

        def environment_builder(i2c: object) -> BME680Sensor:
            import adafruit_bme680

            return BME680Sensor(adafruit_bme680.Adafruit_BME680_I2C(i2c))

        def imu_builder(i2c: object) -> BNO08XSensor:
            from adafruit_bno08x import (
                BNO_REPORT_ACCELEROMETER,
                BNO_REPORT_GYROSCOPE,
                BNO_REPORT_MAGNETOMETER,
            )
            from adafruit_bno08x.i2c import BNO08X_I2C

            device = BNO08X_I2C(i2c)
            device.enable_feature(BNO_REPORT_ACCELEROMETER)
            device.enable_feature(BNO_REPORT_GYROSCOPE)
            device.enable_feature(BNO_REPORT_MAGNETOMETER)
            return BNO08XSensor(device)

        def gps_factory() -> GPSSensor:
            import adafruit_gps
            import serial

            return GPSSensor(serial, adafruit_gps, config.gps_port)

        return {
            "temperature": self._i2c_factory(temperature_builder),
            "environment": self._i2c_factory(environment_builder),
            "imu": self._i2c_factory(imu_builder),
            "geiger": lambda: GeigerSensor(self.gpio),
            "ultrasonic": lambda: UltrasonicSensor(
                self.gpio,
                echo_timeout_seconds=config.ultrasonic_echo_timeout_seconds,
            ),
            "gps": gps_factory,
        }

    def cleanup(self) -> None:
        try:
            self.gpio.cleanup()
        except Exception:
            pass
