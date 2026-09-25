# Preflight checklist

Use this after the software is installed and before a field or flight run.

## Power and boot

- [ ] The Pi starts from a cold power-on without a monitor or keyboard.
- [ ] The expected power source is connected and stable.
- [ ] The microSD card mounts normally.
- [ ] System time is reasonable before launch.
- [ ] The Balloon4 service starts after boot if automatic startup is enabled.

## Software

- [ ] `git status` shows the expected deployed revision.
- [ ] `balloon4 --config config/flight.toml check` succeeds.
- [ ] The intended sensors are enabled in `config/flight.toml`.
- [ ] GPS uses the expected serial device.
- [ ] There is enough free disk space for telemetry and any planned camera capture.

Check storage with:

```bash
df -h .
```

## Sensors

Run the logger manually before relying on the service:

```bash
balloon4 --config config/flight.toml run
```

Confirm:

- [ ] Temperature samples change.
- [ ] BME680 temperature, pressure and humidity are present.
- [ ] IMU values are present and respond to movement.
- [ ] GPS eventually reports a fix in an environment with sky view.
- [ ] Geiger pulses can be observed with the expected test procedure.
- [ ] Ultrasonic readings complete without timeout during the intended test.
- [ ] `balloon4 --config config/flight.toml status` shows recent rows after the logger has run.

## Failure test

Before a flight build is approved, deliberately test degraded operation on safe bench hardware.

- [ ] Start with one non-critical sensor unavailable and confirm the other workers continue.
- [ ] Reconnect that sensor and confirm its worker recovers.
- [ ] Interrupt GPS communication and confirm the process stays alive.
- [ ] Force an ultrasonic timeout and confirm the worker retries instead of hanging.
- [ ] Stop the process with SIGTERM and confirm GPIO is released.

## Optional radio

Only complete these if radio is part of the flight configuration.

- [ ] Antenna is connected before transmitting.
- [ ] Frequency and radio settings match the ground station.
- [ ] Ground station receives known test packets.
- [ ] Packet sequence and payload decode correctly.
- [ ] Range testing is complete.

Radio transmission is not enabled by default in the maintained logger.

## Optional camera

Only complete these if camera capture is planned.

- [ ] `rpicam-vid` is installed.
- [ ] The camera is detected.
- [ ] A short capture succeeds.
- [ ] Output is written to the intended storage location.
- [ ] Available disk space is appropriate for the planned capture.

## Final run

- [ ] Stop any manual logger before starting the systemd service.
- [ ] Reboot once.
- [ ] Confirm a fresh run directory was created.
- [ ] Confirm each required CSV receives new rows.
- [ ] Review `journalctl -u balloon4.service` for errors.
- [ ] Record the deployed Git commit and configuration with the flight notes.

## After recovery

- [ ] Shut the Pi down cleanly when practical.
- [ ] Copy the entire run directory before modifying data.
- [ ] Keep the original files read-only during analysis.
- [ ] Record anomalies while the test or flight is still fresh.
