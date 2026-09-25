# Balloon4 Flight Computer

Raspberry Pi flight-computer software from the Balloon4 high-altitude balloon project.

Balloon4 began as a student team project in 2024. The original software collected environmental, motion, radiation, GPS and distance data on a Raspberry Pi during payload development and flight work.

I returned to the code in 2026 to make the project easier to understand, test and maintain.

## Current version

The maintained runtime lives in `src/balloon4`.

It now includes:

- isolated sensor workers, so one device can fail without preventing the other workers from starting
- one shared I2C bus with serialized access
- GPS reconnection after serial failures
- an ultrasonic echo timeout instead of an unbounded GPIO loop
- UTC timestamps plus monotonic elapsed time
- a separate directory and manifest for every run
- periodic disk sync for telemetry files
- health reporting for every enabled sensor
- clean shutdown on SIGINT and SIGTERM
- simulated hardware tests that run without a Raspberry Pi
- a small CLI for configuration checks, logging and status

The current runtime is tested in CI on Python 3.11 and 3.12.

It still needs to be validated on the original Raspberry Pi hardware before being treated as flight-ready software.

## Sensors

The maintained logger supports:

- MCP9808 temperature sensor
- BME680 environmental sensor
- BNO08X IMU
- GPS over UART
- Geiger counter on GPIO 17
- ultrasonic sensor on GPIO 12 and 13

The repository also keeps camera and RFM9x radio support. They are not enabled by default in the maintained logger because those paths have not been revalidated on the original payload hardware.

## How it works

Each enabled sensor gets its own worker.

A worker creates its hardware inside the worker thread, reads a sample, writes it to that run's CSV file and updates its health state. If initialization or reading fails, only that worker enters retry mode. The rest keep logging.

The three I2C sensors share one bus and one lock.

Every run gets its own directory under `data/`. The directory contains a manifest plus one CSV per sensor.

## Quick start

For a new Raspberry Pi, start with [docs/quick-start.md](docs/quick-start.md).

Once the Pi and sensors work manually, use [docs/raspberry-pi-setup.md](docs/raspberry-pi-setup.md) to start the logger automatically at boot.

Useful commands:

```bash
balloon4 --config config/flight.toml check
balloon4 --config config/flight.toml run
balloon4 --config config/flight.toml status
```

## Repository layout

```text
src/balloon4/       maintained flight-computer software
config/             flight configuration
tests/              simulated hardware and runtime tests
docs/               setup, hardware, architecture and operations
legacy/2024/        source snapshot from the original 2024 implementation
data/               runtime telemetry, ignored by Git
```

## Documentation

- [Raspberry Pi quick start](docs/quick-start.md)
- [Hardware notes](docs/hardware.md)
- [Architecture](docs/architecture.md)
- [Preflight checklist](docs/preflight.md)
- [Operations](docs/operations.md)
- [Automatic boot setup](docs/raspberry-pi-setup.md)

## Project history

This was a team project. Historical work was committed through personal accounts and the shared `balloon4computing` account, so Git history is the best source for individual contributions.

The exact repository state before the 2026 modernization is preserved on the `archive/flight-era-2024` branch. A source-only snapshot is also kept under `legacy/2024`.

The team balloon mission reached roughly 30 km. The complete flight telemetry used to substantiate that altitude is not preserved in this repository. The historical CSVs in Git history are bench and integration sessions, so they are not presented here as flight data.

## Engineering workflow

Changes go through focused pull requests and automated checks. See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and [SECURITY.md](SECURITY.md) for credential and hardware-safety guidance.

The repository uses CODEOWNERS, structured issue templates, Dependabot, and a pull-request title check. CI remains hardware-independent, so bench validation is recorded separately when a change touches real devices.

## Current limitations

- The v2 runtime has not been revalidated on the original payload hardware.
- Hardware dependency versions are not locked to a known-good flight image yet.
- RFM9x packet encoding exists, but radio transmission is not part of the default logger.
- Camera capture uses the current `rpicam-vid` command but remains optional.

Those items should be resolved on real hardware before another flight.
