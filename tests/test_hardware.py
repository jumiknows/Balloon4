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


class FakeClock:
    def __init__(self, values):
        self.values = iter(values)

    def __call__(self):
        return next(self.values)


def test_gps_reports_fix_and_closes_serial_port():
    sensor = GPSSensor(FakeSerialModule, FakeGPSModule, "/dev/serial0")

    sample = sensor.read()

    assert sample["has_fix"] is True
    assert sample["altitude_m"] == 123.4
    assert sensor.uart.port == "/dev/serial0"

    sensor.close()
    assert sensor.uart.closed is True


def test_geiger_uses_actual_sample_window():
    gpio = FakeGPIO()
    clock = FakeClock([10.0, 12.0, 13.0])
    sensor = GeigerSensor(gpio, monotonic=clock)

    gpio.callback(17)
    gpio.callback(17)
    first = sensor.read()
    second = sensor.read()

    assert first["pulse_count"] == 2
    assert first["window_seconds"] == pytest.approx(2.0)
    assert first["counts_per_second"] == pytest.approx(1.0)
    assert first["dose_rate_usvh"] == pytest.approx(0.1992)
    assert second["pulse_count"] == 0
    assert second["window_seconds"] == pytest.approx(1.0)

    sensor.close()
    assert gpio.removed == [17]
