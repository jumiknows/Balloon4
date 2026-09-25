import pytest

from balloon4.sensors.ultrasonic import wait_for_level


class FakeClock:
    def __init__(self, step=0.01):
        self.value = 0.0
        self.step = step

    def __call__(self):
        value = self.value
        self.value += self.step
        return value


def test_wait_for_level_returns_when_gpio_changes():
    levels = iter([0, 0, 1])

    def read_level():
        return next(levels)

    clock = FakeClock()
    reached_at = wait_for_level(read_level, target=1, timeout_seconds=1, monotonic=clock)

    assert reached_at >= 0


def test_wait_for_level_times_out_instead_of_hanging():
    clock = FakeClock(step=0.02)

    with pytest.raises(TimeoutError, match="GPIO did not reach level"):
        wait_for_level(
            lambda: 0,
            target=1,
            timeout_seconds=0.05,
            monotonic=clock,
        )
