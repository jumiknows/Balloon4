from __future__ import annotations

import json
from collections.abc import Mapping

DEFAULT_MAX_PACKET_BYTES = 240


def encode_packet(
    sensor: str,
    sequence: int,
    sample: Mapping[str, object],
    max_bytes: int = DEFAULT_MAX_PACKET_BYTES,
) -> bytes:
    packet = {
        "sensor": sensor,
        "sequence": sequence,
        "data": dict(sample),
    }
    encoded = json.dumps(packet, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if len(encoded) > max_bytes:
        raise ValueError(
            f"Telemetry packet is {len(encoded)} bytes; configured limit is {max_bytes}"
        )
    return encoded
