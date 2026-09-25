from __future__ import annotations

import json
from collections.abc import Mapping


def encode_packet(sensor: str, sequence: int, sample: Mapping[str, object]) -> bytes:
    packet = {
        "sensor": sensor,
        "sequence": sequence,
        "data": dict(sample),
    }
    return json.dumps(packet, separators=(",", ":"), sort_keys=True).encode("utf-8")
