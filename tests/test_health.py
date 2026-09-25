from balloon4.health import HealthMonitor


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def __call__(self):
        return self.value


def test_health_moves_from_starting_to_degraded_to_healthy():
    clock = FakeClock()
    health = HealthMonitor(["gps"], monotonic=clock)

    assert health.snapshot()["gps"].state == "starting"

    health.mark_error("gps", OSError("no serial device"))
    degraded = health.snapshot()["gps"]
    assert degraded.state == "degraded"
    assert degraded.sample_count == 0
    assert "no serial device" in degraded.last_error

    health.mark_sample("gps")
    recovered = health.snapshot()["gps"]
    assert recovered.state == "healthy"
    assert recovered.sample_count == 1
    assert recovered.last_error is None


def test_health_report_marks_old_samples_stale():
    clock = FakeClock()
    health = HealthMonitor(
        ["gps"],
        stale_after_seconds={"gps": 5.0},
        monotonic=clock,
    )

    health.mark_sample("gps")
    assert "HEALTHY" in health.format_report()

    clock.value = 6.0
    report = health.format_report()

    assert "STALE" in report
    assert "last sample 6.0s ago" in report
