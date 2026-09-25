# Operations

## Validate configuration

This command does not touch Raspberry Pi hardware:

```bash
balloon4 --config config/flight.toml check
```

Use it after editing the configuration.

## Run manually

Stop the systemd service first if it is enabled:

```bash
sudo systemctl stop balloon4.service
```

Then:

```bash
cd ~/Balloon4
source .venv/bin/activate
balloon4 --config config/flight.toml run
```

Press Ctrl+C to stop cleanly.

## Check the latest telemetry

```bash
balloon4 --config config/flight.toml status
```

This reads the last row of each CSV in the newest run directory. It replaces the old background CSV-reader thread, so diagnostics no longer compete with the logger for file locks.

## Run directories

Every logger start creates a new directory under `data/`.

Keep the whole directory together. The manifest identifies the run and records the configuration summary.

The `data/` directory is intentionally ignored by Git.

## Service commands

```bash
sudo systemctl status balloon4.service
sudo systemctl restart balloon4.service
sudo systemctl stop balloon4.service
sudo systemctl start balloon4.service
journalctl -u balloon4.service -b
```

Do not run the service and a manual logger at the same time.

## Copy data off the Pi

From another computer on the same network:

```bash
scp -r balloon@balloon4.local:~/Balloon4/data ./balloon4-data
```

Use the actual username, hostname or IP for the Pi.

## Update the deployed code

Do this on bench hardware, not immediately before launch.

```bash
cd ~/Balloon4
sudo systemctl stop balloon4.service
git pull --ff-only
source .venv/bin/activate
python -m pip install -e ".[hardware]"
balloon4 --config config/flight.toml check
```

Then run the preflight checks before restarting the service.

## Troubleshooting a degraded sensor

The health report shows the latest error for each worker.

A degraded sensor is retried automatically. If it repeatedly fails:

1. Stop the logger.
2. Check wiring and power.
3. Confirm the relevant Pi interface is enabled.
4. Test the device by itself if a vendor example is available.
5. Review the service log.
6. Restart only after the underlying issue is understood.

Repeated retries are not evidence that the hardware is healthy.
