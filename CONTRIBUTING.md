# Contributing

Balloon4 is flight-computer software. Keep changes small, testable, and clear enough that someone can understand them without the original hardware beside them.

## Workflow

1. Start from the latest `main`.
2. Create one focused branch.
3. Add or update tests when behavior changes.
4. Run the checks below.
5. Open a pull request and explain what changed, how you tested it, and whether real hardware was involved.

Example branch names:

```text
feat/gps-health-reporting
fix/ultrasonic-timeout
test/i2c-worker-recovery
docs/preflight-checklist
```

## Local checks

```bash
python -m pip install -e ".[dev]"
ruff check src tests
pytest -q
python -m compileall -q src
balloon4 --config config/flight.toml check
```

## Hardware changes

A simulated test passing does not prove hardware behavior.

For sensor, GPIO, serial, I2C, camera, radio, boot, or power-related changes, state whether you tested on:

- CI only
- Raspberry Pi without payload hardware
- bench hardware
- integrated payload hardware

Do not describe a change as flight-ready until the relevant hardware has been validated.

## Commits and pull requests

Use clear Conventional Commit-style titles such as:

```text
fix: recover GPS worker after serial failure
test: cover BME680 initialization failure
docs: update Raspberry Pi boot setup
```

Prefer squash merge after review and passing CI.
