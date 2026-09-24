# Start Balloon4 automatically when the Pi boots

First complete the [new member quick start](quick-start.md), connect over SSH and confirm the logger works manually with the actual sensors connected.

The original project used automatic startup, but its exact flight-device service configuration is not preserved here. This is an example for a **new setup** using the virtual environment from the quick start.

## 1. Check your username and project path

~~~bash
whoami
pwd
ls ~/Balloon4/.venv/bin/python
~~~

The example below assumes you chose **balloon** as your username and cloned the repo to `/home/balloon/Balloon4`. Replace these paths and the `User=` value if yours are different.

## 2. Create the service

~~~bash
sudo nano /etc/systemd/system/balloon4.service
~~~

Paste:

~~~ini
[Unit]
Description=Balloon4 sensor logger
After=multi-user.target

[Service]
Type=simple
User=balloon
WorkingDirectory=/home/balloon/Balloon4
ExecStart=/home/balloon/Balloon4/.venv/bin/python /home/balloon/Balloon4/Code/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
~~~

Save and exit Nano (Ctrl+O, Enter, Ctrl+X).

## 3. Enable and check it

~~~bash
sudo systemctl daemon-reload
sudo systemctl enable --now balloon4.service
sudo systemctl status balloon4.service
journalctl -u balloon4.service -b -n 50 --no-pager
~~~

If everything works, reboot and check again:

~~~bash
sudo reboot
~~~

After reconnecting over SSH:

~~~bash
sudo systemctl status balloon4.service
journalctl -u balloon4.service -b -n 50 --no-pager
~~~

The Pi logs to local CSV files even when you disconnect SSH or turn off the phone hotspot. A hotspot is needed for remote access, not for the configured service to keep running.

## Useful commands

~~~bash
sudo systemctl stop balloon4.service
sudo systemctl start balloon4.service
sudo systemctl restart balloon4.service
sudo systemctl disable --now balloon4.service
~~~

Only run **one copy** of the logger at a time. Stop the service before running `python Code/main.py` manually to avoid two processes trying to use the same sensors.

## Hardware notes

The code expects connected sensors. The GPS uses `/dev/ttyS0`, the Geiger counter uses BCM GPIO 17, and the ultrasonic sensor uses BCM GPIO 12 and 13. Check the payload wiring, power, I2C, UART and SPI setup before running or rebooting the service.

This example has not been tested on the original flight computer. Verify each sensor's CSV output and the service's restart behaviour on the actual Pi before using it for field work.
