# Start Balloon4 automatically at boot

Do this only after the quick-start guide works with the real sensors.

## 1. Confirm the install

```bash
cd ~/Balloon4
source .venv/bin/activate
balloon4 --config config/flight.toml check
which balloon4
```

The example below assumes:

- username `balloon`
- repository at `/home/balloon/Balloon4`
- virtual environment at `/home/balloon/Balloon4/.venv`

Change the paths if your setup is different.

## 2. Create the service

```bash
sudo nano /etc/systemd/system/balloon4.service
```

Paste:

```ini
[Unit]
Description=Balloon4 flight data logger
After=local-fs.target

[Service]
Type=simple
User=balloon
WorkingDirectory=/home/balloon/Balloon4
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/balloon/Balloon4/.venv/bin/balloon4 --config /home/balloon/Balloon4/config/flight.toml run
Restart=on-failure
RestartSec=5
KillSignal=SIGTERM
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
```

Save with Ctrl+O, Enter, then Ctrl+X.

## 3. Enable it

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now balloon4.service
```

Check:

```bash
sudo systemctl status balloon4.service
journalctl -u balloon4.service -b -n 100 --no-pager
```

## 4. Reboot test

```bash
sudo reboot
```

Reconnect over SSH and check again:

```bash
sudo systemctl status balloon4.service
journalctl -u balloon4.service -b -n 100 --no-pager
```

Then inspect the latest run:

```bash
cd ~/Balloon4
source .venv/bin/activate
balloon4 --config config/flight.toml status
```

A fresh boot should create a fresh run directory.

## Useful commands

```bash
sudo systemctl stop balloon4.service
sudo systemctl start balloon4.service
sudo systemctl restart balloon4.service
sudo systemctl disable --now balloon4.service
```

Never run a manual logger while the service is already using the payload hardware.

## Before field use

Complete [preflight.md](preflight.md).

The service definition is tested structurally in the repository, but the full boot flow still needs validation on the actual Raspberry Pi and sensors.
