import pytest

from balloon4.hardware import GeigerSensor, GPSSensor


class FakeSerialPort:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.closed = False

    def close(self):
        self.closed = True


class FakeSerialModule:
    Serial = FakeSerialPort


class FakeGPSDevice:
    def __init__(self, uart, debug):
        self.uart = uart
        self.debug = debug
        self.commands = []
        self.has_fix = True
        self.latitude = 49.2
        self.longitude = -122.8
        self.speed_knots = 4.2
        self.altitude_m = 123.4

    def send_command(self, command):
        self.commands.append(command)

    def update(self):
        return True


class FakeGPSModule:
    GPS = FakeGPSDevice


class FakeGPIO:
    IN = 1
    FALLING = 2

    def __init__(self):
        self.callback = None
        self.removed = []

    def setup(self, _pin, _mode):
        return None

    def add_event_detect(self, _pin, _edge, callback):
        self.callback = callback

    def remove_event_detect(self, pin):
        self.removed.append(pin)


def test_gps_reports_fix_and_closes_serial_port():
    sensor = GPSSensor(FakeSerialModule, FakeGPSModule, "/dev/serial0")

    sample = sensor.read()

    assert sample["has_fix"] is True
    assert sample["altitude_m"] == 123.4
    assert sensor.uart.port == "/dev/serial0"

    sensor.close()
    assert sensor.uart.closed is True


def test_geiger_resets_counts_between_samples():
    gpio = FakeGPIO()
    sensor = GeigerSensor(gpio)

    gpio.callback(17)
    gpio.callback(17)
    first = sensor.read()
    second = sensor.read()

    assert first["counts_per_second"] == 2
    assert first["dose_rate_usvh"] == pytest.approx(0.3984)
    assert second["counts_per_second"] == 0

    sensor.close()
    assert gpio.removed == [17]
