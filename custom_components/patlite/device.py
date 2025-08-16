from __future__ import annotations
import logging
import socket
from typing import Final, Callable

from .const import NUM_TIERS, UDP_TIMEOUT_S, DEFAULT_ON_COLOR

_LOGGER: Final = logging.getLogger(__name__)

# PNS "Detailed Motion Control" (fixed header for 5 tiers + flash + buzzer)
_PNS_HEADER = bytes([0x41, 0x42, 0x44, 0x00, 0x00, 0x07])
_PNS_DATA_LEN = 7  # 5 colors + flash + buzzer


class PatliteDevice:
    """Patlite towers using 'Detailed Motion Control'"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.tier_colors: list[int] = [0x00] * NUM_TIERS  # 00..09
        self.tier_enabled: list[bool] = [False] * NUM_TIERS
        self.flash: int = 0  # 01=ON, 00=OFF
        self.buzzer: int = 0  # 00 stop, 01..0B patterns
        self._last_nonzero_color: list[int | None] = [None] * NUM_TIERS

        # --- simple listeners for HA entities ---
        self._listeners: list[Callable[[], None]] = []

    # ---------- Public API ----------
    def set_tier_color(self, tier: int, code: int) -> None:
        self._validate_tier(tier)
        code = int(code)
        if not (0x00 <= code <= 0xFF):
            raise ValueError("Invalid color code")
        self.tier_colors[tier] = code
        if code:
            self._last_nonzero_color[tier] = code
            self.tier_enabled[tier] = True  # UI power follows color
        self._send()
        self._notify()

    def set_tier_power(self, tier: int, on: bool) -> None:
        self._validate_tier(tier)
        self.tier_enabled[tier] = bool(on)
        if on:
            if self.tier_colors[tier] == 0x00:
                last = self._last_nonzero_color[tier]
                self.tier_colors[tier] = last if last is not None else DEFAULT_ON_COLOR
        else:
            self.tier_colors[tier] = 0x00
        self._send()
        self._notify()

    def set_flash(self, value: int | bool) -> None:
        self.flash = 1 if bool(value) else 0
        self._send()
        self._notify()

    def set_buzzer(self, value: int | bool | int) -> None:
        if isinstance(value, bool):
            self.buzzer = 1 if value else 0
        else:
            pat = int(value)
            if not (0x00 <= pat <= 0x0B):
                raise ValueError("Buzzer pattern out of range (0x00..0x0B)")
            self.buzzer = pat
        self._send()
        self._notify()

    # Legacy compatibility
    def set_tier_onoff(self, tier: int, on: bool) -> None:
        self.set_tier_power(tier, on)

    def set_tier_state(self, tier: int, state) -> None:
        if isinstance(state, bool):
            self.set_tier_power(tier, state)
            return
        code = int(state)
        if not (0x00 <= code <= 0xFF):
            raise ValueError(f"color code out of range: {code}")
        self.set_tier_color(tier, code)
        self.set_tier_power(tier, code != 0x00)

    def get_last_color_code(self, tier: int) -> int | None:
        self._validate_tier(tier)
        return self._last_nonzero_color[tier]

    # ---------- Listener API ----------
    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a callback invoked after state changes. Returns unsubscribe."""
        self._listeners.append(listener)
        def _unsub():
            try:
                self._listeners.remove(listener)
            except ValueError:
                pass
        return _unsub

    def _notify(self) -> None:
        for cb in list(self._listeners):
            try:
                cb()
            except Exception as exc:
                _LOGGER.debug("Listener callback error: %s", exc)

    # ---------- Helpers ----------
    def _validate_tier(self, tier: int) -> None:
        if not (0 <= tier < NUM_TIERS):
            raise ValueError("Tier out of range")

    def _build_packet(self) -> bytes:
        """
        Build PNS 'Detailed Motion Control' frame:
          [ 'A','B','D', 0x00, 0x00, 0x07, T1, T2, T3, T4, T5, Flash, Buzzer ]
        """
        colors = list(self.tier_colors[:5])
        while len(colors) < 5:
            colors.append(0x00)
        # Ensure 'on' tiers have a non-zero color
        for i in range(5):
            if self.tier_enabled[i] and colors[i] == 0x00:
                last = self._last_nonzero_color[i]
                colors[i] = last if last is not None else DEFAULT_ON_COLOR
        data = bytes(colors) + bytes([self.flash & 0x01, self.buzzer & 0xFF])
        assert len(data) == _PNS_DATA_LEN, f"PNS data must be 7 bytes, got {len(data)}"
        return _PNS_HEADER + data

    def _send(self) -> None:
        pkt = self._build_packet()
        _LOGGER.debug(
            "TX %s:%s PNS colors=%s flash=%s buzzer=%s pkt=%s",
            self.host, self.port, self.tier_colors[:5], self.flash, self.buzzer, pkt.hex()
        )
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(UDP_TIMEOUT_S)
                s.sendto(pkt, (self.host, self.port))
        except Exception as exc:
            _LOGGER.exception("UDP send failed: %s", exc)
