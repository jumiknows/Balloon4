# Balloon4 Flight Computer

Python flight-computer software for a Raspberry Pi Zero used in the Balloon4 student high-altitude balloon project.

The payload had to collect data without someone logged into the Pi, so the software was designed to start with the computer and keep logging sensor data throughout the run.

## What it did

`Code/main.py` starts the sensor modules in parallel threads.

| Module | Purpose |
| --- | --- |
| MCP9808 | Temperature |
| BNO08X | Acceleration, gyroscope and magnetometer |
| BME680 | Temperature, pressure and humidity |
| Geiger counter | Radiation counts and estimated dose rate |
| Ultrasonic sensor | Distance measurements |
| GPS | Position, speed and altitude |
| RFM9x | 915 MHz LoRa radio support |
| Camera | Timelapse and video capture with `libcamera` |

Each sensor logger writes its own CSV file so one device can fail or restart without taking down the rest of the data collection.

```text
Raspberry Pi Zero
      |
      +-- sensor threads
      |    +-- temperature
      |    +-- motion
      |    +-- environment
      |    +-- radiation
      |    +-- distance
      |    +-- GPS
      |
      +-- local CSV logs
      +-- camera capture
      +-- RFM9x radio support
```

## Repository layout

```text
Code/
  main.py             current modular entry point
  MCP9808/            temperature
  BN0085/             motion
  BME680/             environment
  GEIGER/             radiation
  GPS/                position
  ULTRASONIC/         distance
  RFM9X/              LoRa radio
  CAMERA/             camera capture
  Buzzer/             buzzer experiments
  MICROPHONE/         microphone experiments
  driver.py           earlier all-in-one prototype
docs/
  quick-start.md       first-time Pi setup, Wi-Fi and SSH
  raspberry-pi-setup.md  boot-time startup
```

Generated sensor logs, lock files, Python caches and camera captures are intentionally kept out of Git.

## Start here

New to Raspberry Pi? Follow the [quick start guide](docs/quick-start.md) to flash the microSD card, connect over SSH using home Wi-Fi or a phone hotspot, install dependencies and run the logger.

For unattended operation, follow the [boot startup guide](docs/raspberry-pi-setup.md) after verifying the sensors work.

The active logger runs with `python Code/main.py` from the virtual environment set up in the quick start guide. Hardware is required; this is not a desktop simulator.

## Project history

Balloon4 was a team project. Historical work was committed through a mix of personal accounts and the shared `balloon4computing` project account, so the Git history should be read as team history rather than a clean map of individual ownership.

This repository is preserved as a student engineering project and reference implementation. It is not maintained as production flight software.
