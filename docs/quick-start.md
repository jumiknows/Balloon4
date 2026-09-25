# New member quick start

This gets a new Raspberry Pi from a blank microSD card to a Balloon4 configuration check and SSH session.

You do not need a monitor or keyboard on the Pi.

## What you need

- Raspberry Pi Zero W or Zero 2 W
- microSD card, 16 GB or larger
- card reader
- reliable power supply
- Windows, macOS or Linux laptop
- home Wi-Fi or a phone hotspot

The original Pi Zero without the W has no built-in Wi-Fi. It needs a supported USB Wi-Fi adapter or another network connection.

## 1. Pick a network

At home, use the same Wi-Fi network as your laptop.

Away from home, a phone hotspot is convenient.

On iPhone:

1. Open Settings.
2. Open Personal Hotspot.
3. Turn on Allow Others to Join.
4. If available, turn on Maximize Compatibility.

On Android:

1. Open Settings.
2. Open Hotspot and tethering or Mobile Hotspot.
3. Turn on the hotspot.
4. If there is a Wi-Fi band option, use 2.4 GHz.

Keep the hotspot on while the Pi boots.

Join the same hotspot from your laptop. Some phones isolate connected devices from one another. If SSH does not work even with the correct IP, use a normal Wi-Fi router or travel router instead.

## 2. Flash Raspberry Pi OS

Install Raspberry Pi Imager on your laptop.

Insert the microSD card and select:

- your Pi model
- Raspberry Pi OS Lite recommended for that device
- the correct microSD card

Before writing the card, open OS customisation and set:

- hostname: `balloon4`
- username: `balloon`, or another username you will remember
- a strong password
- Wi-Fi name and password
- Wi-Fi country
- time zone
- keyboard layout
- SSH enabled with password authentication for first setup

Writing the image erases the selected card.

Do not put Pi or hotspot passwords in GitHub, screenshots or shared notes.

## 3. Connect over SSH

Insert the card into the Pi and power it on.

Connect your laptop to the same network.

Try:

```bash
ssh balloon@balloon4.local
```

Use your actual username if it is different.

If `balloon4.local` does not resolve, find the Pi in your router or hotspot's connected-device list and use its real local IP:

```bash
ssh balloon@192.168.1.123
```

That address is only an example.

## 4. Enable the Pi interfaces

Run:

```bash
sudo raspi-config
```

Under Interface Options:

- enable I2C
- enable SPI if you plan to test the radio
- configure Serial so the login shell is disabled and serial hardware is enabled

Reboot after changing interfaces:

```bash
sudo reboot
```

Reconnect with SSH.

## 5. Install Balloon4

Inside the Pi:

```bash
sudo apt update
sudo apt install -y git python3-venv python3-pip

git clone --depth 1 https://github.com/jumiknows/Balloon4-Flight-Computer.git Balloon4
cd Balloon4

python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -e ".[hardware]"
```

The shallow clone avoids downloading old camera videos that remain in Git history.

## 6. Check the software first

Before connecting or starting all sensors:

```bash
balloon4 --config config/flight.toml check
```

This validates the configuration without opening GPIO, I2C or UART devices.

## 7. Check the actual payload wiring

Read [hardware.md](hardware.md).

Do not assume undocumented voltage, wiring or I2C addresses.

Once the hardware has been checked:

```bash
balloon4 --config config/flight.toml run
```

The terminal will print a health report periodically.

In another SSH session, you can inspect the newest run:

```bash
cd ~/Balloon4
source .venv/bin/activate
balloon4 --config config/flight.toml status
```

## 8. Start automatically at boot

After manual tests pass, follow [raspberry-pi-setup.md](raspberry-pi-setup.md).

Before field use, complete [preflight.md](preflight.md).

## Common problems

### SSH times out

Check that the Pi is powered and the laptop is on the same network.

Try the Pi's real local IP instead of `balloon4.local`.

If you are using a phone hotspot, the phone may isolate clients.

### SSH says permission denied

Use the username and password configured in Raspberry Pi Imager. Current Raspberry Pi OS images do not depend on an assumed default `pi` account.

### The Pi does not join the hotspot

Check the exact network name and password.

Use 2.4 GHz or iPhone Maximize Compatibility when available.

### GPS does not open

Check:

```bash
ls -l /dev/serial0
```

Then confirm the serial login shell is disabled and the serial hardware is enabled.

### I2C sensors do not appear

Confirm I2C is enabled and review [hardware.md](hardware.md).

### One sensor is degraded

The maintained logger is designed to keep the other workers running. Read the health error, stop the logger if hardware needs to be touched, fix the device and restart.

## Next reading

- [Hardware notes](hardware.md)
- [Preflight checklist](preflight.md)
- [Operations](operations.md)
- [Architecture](architecture.md)
