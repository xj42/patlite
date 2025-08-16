from __future__ import annotations

DOMAIN = "patlite"

# Colors supported by the tower; adjust to match your device protocol
COLOR_MAP: dict[str, int] = {
    "Off": 0x00,
    "Red": 0x01,
    "Amber": 0x02,
    "Lemon": 0x03,
    "Green": 0x04,
    "Sky Blue": 0x05,
    "Blue": 0x06,
    "Purple": 0x07,
    "Pink": 0x08,
    "White":0x09
}
INV_COLOR_MAP: dict[int, str] = {v: k for k, v in COLOR_MAP.items()}

NUM_TIERS = 5

# Network defaults
UDP_PORT_DEFAULT = 10000  # change if your device uses another port
UDP_TIMEOUT_S = 2.0
DEFAULT_ON_COLOR = 0x01  # Red by default
BIT_ORDER_MSB_FIRST = False