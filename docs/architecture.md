# Architecture

The 2026 runtime keeps the flight computer deliberately small.

## Runtime flow

1. `balloon4 run` loads `config/flight.toml`.
2. A run directory and manifest are created under `data/`.
3. The hardware context prepares shared Raspberry Pi resources.
4. Each enabled sensor starts in its own worker.
5. Workers write samples through the telemetry writer.
6. The health monitor reports sensor state and sample counts.
7. SIGINT or SIGTERM stops the workers and releases GPIO resources.

## Failure isolation

Sensor hardware is created inside its worker rather than before the process starts.

If GPS is disconnected at startup, the GPS worker reports a degraded state and retries later. Temperature, environment, IMU, Geiger and ultrasonic workers can continue.

The same pattern applies when a sensor raises during a read. The worker closes that device, records the error and builds a fresh device on the next retry.

## I2C

MCP9808, BME680 and BNO08X use the same physical I2C bus.

The hardware context creates that bus lazily and gives the three devices one shared lock. Reads are serialized so multiple Python threads do not talk over the same bus at the same time.

## Telemetry

Each run has a unique ID and directory.

A typical run looks like:

```text
data/
  20260925T030000Z-a1b2c3/
    manifest.json
    temperature.csv
    environment.csv
    imu.csv
    geiger.csv
    ultrasonic.csv
    gps.csv
```

Each CSV row includes an absolute UTC timestamp and monotonic elapsed seconds.

UTC makes datasets easy to compare with outside events. Elapsed time remains useful if the system clock is wrong or changes.

Files are flushed on every row and synced to disk periodically. The sync interval is configurable so durability can be balanced against SD-card writes.

## Health

Every worker reports:

- current state
- number of successful samples
- time of the most recent successful sample
- latest error

The health report is operational information. It is not a substitute for sensor-specific validation.

## Optional hardware

Camera and radio code are kept separate from the core logger.

The camera helper uses `rpicam-vid`.

The radio module currently defines a deterministic packet format. It does not claim reliable end-to-end telemetry until the RFM9x and ground-station path are tested again on hardware.

## Testing boundary

CI does not pretend to emulate Raspberry Pi electronics.

Instead, tests exercise the parts that should be deterministic on any computer:

- worker recovery
- telemetry files and manifests
- config validation
- GPS adapter behavior with fake serial hardware
- Geiger count handling with fake GPIO
- ultrasonic timeout logic
- health transitions
- radio packet encoding

The remaining validation belongs on the real payload.
