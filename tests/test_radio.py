import json

import pytest

from balloon4.radio import encode_packet


def test_radio_packet_is_compact_and_deterministic():
    encoded = encode_packet(
        "temperature",
        42,
        {"temperature_c": 21.5, "ok": True},
    )

    decoded = json.loads(encoded)
    assert decoded == {
        "sensor": "temperature",
        "sequence": 42,
        "data": {"ok": True, "temperature_c": 21.5},
    }
    assert b" " not in encoded


def test_radio_packet_rejects_payload_over_limit():
    with pytest.raises(ValueError, match="configured limit"):
        encode_packet(
            "camera",
            43,
            {"payload": "x" * 500},
        )
