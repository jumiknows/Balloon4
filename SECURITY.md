# Security and Safety

Balloon4 is embedded flight-computer software. Security mistakes can expose credentials, while reliability mistakes can affect hardware or telemetry.

## Do not commit

- Wi-Fi passwords
- SSH keys
- API tokens
- radio credentials or private network configuration
- private location data that should not be published
- credentials copied from a Raspberry Pi image

Use example values in documentation and tests.

## Reporting

If you find a credential, private key, or vulnerability that should not be public, contact the repository owner privately instead of pasting the sensitive value into an issue.

For ordinary reliability bugs, open a normal issue with reproduction steps.

## Flight safety

The maintained runtime has not been revalidated on the original payload hardware. CI and simulated hardware tests are development evidence, not flight certification.

Changes involving GPIO, I2C, UART, timing, boot services, storage, radio, or power behavior should be bench-tested before flight use.
