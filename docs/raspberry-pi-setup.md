# Raspberry Pi setup

The original Balloon4 payload ran unattended, so the Raspberry Pi was configured to start the data logger when it booted.

The exact deployment configuration from the flight hardware was not preserved in this repository. The following systemd unit reproduces that behaviour on a current Raspberry Pi OS installation.

## 1. Clone and install

```bash
git clone https://github.com/jumiknows/Balloon4.git
cd Balloon4
python3 -m pip install -r requirements.txt
```

Confirm the logger starts manually before enabling boot startup:

```bash
python3 Code/main.py
```

## 2. Create a systemd service

Update the user and paths below to match the Pi.

```ini
[Unit]
Description=Balloon4 sensor logger
After=multi-user.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Balloon4
ExecStart=/usr/bin/python3 /home/pi/Balloon4/Code/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save it as:

```text
/etc/systemd/system/balloon4.service
```

Then enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable balloon4.service
sudo systemctl start balloon4.service
```

Check the logger:

```bash
sudo systemctl status balloon4.service
journalctl -u balloon4.service
```

## Hardware notes

The logger expects the sensors to be wired to the Raspberry Pi interfaces used by the Python modules. GPS uses `/dev/ttyS0`, the Geiger counter uses BCM GPIO 17, and the ultrasonic sensor uses BCM GPIO 12 and 13.

Run hardware tests before relying on the service for a flight or field test.
