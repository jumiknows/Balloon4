# New member quick start: Raspberry Pi

This guide gets you from a blank microSD card to an SSH session on a Balloon4 Raspberry Pi. No monitor or keyboard is needed on the Pi.

## What you need

- Raspberry Pi Zero W or Zero 2 W, microSD card (16 GB or larger), card reader and a reliable power supply.
- A Windows, macOS or Linux laptop.
- A home Wi-Fi network **or** a phone with a mobile hotspot.

The original Raspberry Pi Zero (without "W") has no built-in Wi-Fi. It needs a supported USB Wi-Fi adapter or another network connection for this guide.

## 1. Choose your Wi-Fi

**At home:** Use the Wi-Fi network that your laptop can also join.

**Away from home:** Turn on your phone's Personal Hotspot / Mobile Hotspot. Set a network name and password you can recognize.

- iPhone: Settings > Personal Hotspot > Allow Others to Join. If available, turn on **Maximize Compatibility**.
- Android: Settings > Hotspot & tethering / Mobile Hotspot. If there is a Wi-Fi band option, choose **2.4 GHz**.

Pi Zero W and Zero 2 W use 2.4 GHz Wi-Fi. Keep the phone hotspot on during the Pi's first boot. Use a second device (your laptop) to connect to the same hotspot; don't rely on the phone itself for the SSH session.

The hotspot provides a local network. Mobile data is needed for downloads, but **SSH itself works locally** if the hotspot permits connected devices to talk to one another. Some hotspots isolate clients. If SSH never works even with the correct IP, use a home router or travel router instead.

## 2. Flash Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your laptop.
2. Insert the microSD card into the laptop.
3. Open Imager. Select your Pi model, **Raspberry Pi OS Lite** (the version recommended for your device) and the correct microSD card. Writing the image erases that card.
4. Open **OS customisation** before writing and enter:
   - Hostname: `balloon4`
   - Username: `balloon` (or your own choice)
   - A strong password
   - Wi-Fi name and password from Step 1
   - Your Wi-Fi country, time zone and keyboard layout
   - **Enable SSH** with password authentication for this first setup (SSH keys are preferable later)
5. Write the card, eject it safely, then insert it into the Pi.

Don't put your hotspot password or Pi password in GitHub or screenshots. If Imager has a different screen layout, look for the same *hostname, user, Wi-Fi and SSH* customisation settings. The [official headless setup guide](https://www.raspberrypi.com/documentation/computers/getting-started.html#headless-remote-setup) covers the current Imager workflow.

## 3. Power up and connect

1. Switch on your phone hotspot (if using one) and join it from your **laptop**.
2. Connect power to the Pi's **power** port, not the USB data port. Leave the card in place and let first boot finish.
3. Open PowerShell on Windows or Terminal on macOS/Linux:

~~~bash
ssh balloon@balloon4.local
~~~

Use your chosen username if it isn't `balloon`. On the first connection, check that you're connecting to your Pi and accept its SSH host key, then enter your Pi password (it won't show while you type).

If `balloon4.local` does not resolve, find the Pi's **local IP address** in your router's device list or the phone hotspot's connected-device list, if your phone shows addresses. Then use the actual address:

~~~bash
ssh balloon@192.168.1.123
~~~

The IP above is an **example**, not the Pi's real address. The laptop and Pi must be on the same local network. If your phone does not show the Pi's IP, switching to a normal Wi-Fi router is usually easier than guessing addresses.

You are connected when your terminal shows a prompt on the Pi, such as `balloon@balloon4:~ $`.

## 4. Prepare the Pi

Run these commands **inside the Pi's SSH terminal**:

~~~bash
sudo apt update
sudo apt install -y git python3-venv python3-pip
git clone https://github.com/jumiknows/Balloon4.git
cd Balloon4
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
~~~

Using a virtual environment keeps the project dependencies out of the OS-managed Python installation. Package installation needs internet access. Some older Pi Zero hardware and sensor libraries may require extra setup or compatible package versions.

## 5. Check the hardware and logger

**Do not start the full logger before the sensors are wired.** It initializes GPIO, I2C sensors and the GPS serial device. Check the wiring, supply voltage and pin assignments against the actual payload first.

Once hardware is connected and verified:

~~~bash
cd ~/Balloon4
source .venv/bin/activate
python Code/main.py
~~~

Look for fresh sensor logs in the module folders under `Code/`. For example, the temperature logger writes `Code/MCP9808/temperature_readings.csv`. An individual sensor can fail even when the others are working, so check each log before a field test.

To run the logger automatically whenever the Pi boots, follow [Boot startup](raspberry-pi-setup.md). You can disconnect SSH after the service is enabled; the logger runs on the Pi, not on your laptop.

## Quick fixes

| Problem | Check |
| --- | --- |
| SSH times out | Is the Pi powered, booted, and on the same Wi-Fi as the laptop? Does the hotspot isolate devices? Try the real IP or a home router. |
| Name `balloon4.local` not found | Use the Pi's real IP from the router/hotspot device list. |
| SSH connection refused | SSH may not be enabled. Recheck Imager's remote-access setting or enable SSH with a monitor/keyboard. |
| Permission denied | Use the username and password set in Imager, not an assumed default `pi` account. |
| Pi not joining hotspot | Recheck the exact SSID/password, keep the hotspot active and enable 2.4 GHz / iPhone Maximize Compatibility. |
| Sensor import or GPIO error | Verify the virtual environment, hardware connections, I2C/SPI/UART configuration, and supported libraries for your Pi model. |

Official reference: [Raspberry Pi remote access and SSH](https://www.raspberrypi.com/documentation/computers/remote-access.html).
