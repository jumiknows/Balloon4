# Hardware notes

This document records what the source code actually tells us about the Balloon4 payload.

Do not treat undocumented wiring, voltage or sensor addresses as known. Verify the physical payload before connecting replacement hardware.

## Maintained sensor interfaces

### MCP9808

Purpose: temperature

Interface: I2C

The I2C address used on the original payload is not documented in the repository. Confirm it on the hardware.

### BME680

Purpose: temperature, pressure and humidity

Interface: I2C

The maintained runtime shares the Pi I2C bus with the MCP9808 and BNO08X.

### BNO08X

Purpose: accelerometer, gyroscope and magnetometer

Interface: I2C

The old folder name `BN0085` was historical. The actual Python library and maintained code use BNO08X.

### GPS

Purpose: latitude, longitude, speed and altitude

Interface: UART

Maintained default device: `/dev/serial0`

The 2024 code used `/dev/ttyS0`. The maintained configuration uses the Raspberry Pi primary-UART alias instead.

### Geiger counter

Purpose: radiation counts and estimated dose rate

Interface: GPIO

Signal pin: BCM 17

The maintained code samples the pulse count once per worker interval. The dose conversion keeps the historical J305 ratio from the team code.

### Ultrasonic sensor

Purpose: distance

Interface: GPIO

Trigger pin: BCM 12

Echo pin: BCM 13

The maintained runtime applies a bounded echo timeout. A missing or stuck echo signal is treated as a failed sample rather than an infinite loop.

## Additional payload hardware

### RFM9x

Historical interface: SPI

Historical configuration used:

- 915 MHz
- chip select on D23
- reset on D24
- spreading factor 10
- 125 kHz bandwidth
- CRC enabled
- coding rate 8

The maintained runtime does not enable radio transmission by default. Recheck the physical module, antenna, regional radio requirements and ground station before enabling it.

### Camera

The maintained helper expects current Raspberry Pi camera applications and calls `rpicam-vid`.

Camera capture is not started by the core logger.

### Buzzer and microphone

These remain historical experiments under `legacy/2024`. They are not part of the maintained flight runtime.

## Raspberry Pi interfaces

Before running the payload, open:

```bash
sudo raspi-config
```

Under Interface Options:

- enable I2C
- enable SPI if the radio will be tested
- configure Serial so the login shell is disabled and the serial hardware is enabled

Reboot after changing interfaces.

You can confirm that the primary UART alias exists with:

```bash
ls -l /dev/serial0
```

For I2C troubleshooting, install the standard tools and inspect the bus:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

Compare any detected addresses against the actual sensor boards before changing code.

## Before connecting hardware

Confirm:

- the sensor's supply voltage
- common ground
- the physical pin number versus BCM numbering
- I2C addresses
- UART wiring direction
- SPI chip-select and reset wiring
- the Geiger module's output level
- the ultrasonic module's echo voltage

The repository does not contain enough information to safely infer every electrical detail.
