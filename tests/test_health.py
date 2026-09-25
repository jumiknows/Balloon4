from balloon4.health import HealthMonitor


def test_health_moves_from_starting_to_degraded_to_healthy():
    health = HealthMonitor(["gps"])

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
