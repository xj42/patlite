from __future__ import annotations
from typing import Any, Callable

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, NUM_TIERS
from .device import PatliteDevice


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    device: PatliteDevice = hass.data[DOMAIN][entry.entry_id]["device"]
    async_add_entities([PatliteTierLight(device, i) for i in range(NUM_TIERS)])


class PatliteTierLight(LightEntity):
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_icon = "mdi:alarm-light"  # tower-light icon
    def __init__(self, device: PatliteDevice, tier: int):
        self._device = device
        self._tier = tier
        self._attr_name = f"Patlite Tier {tier+1}"
        self._attr_unique_id = f"{device.host}:{device.port}-tier{tier}"
        self._attr_should_poll = False
        self._unsub: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        # Subscribe to device state changes so the switch reflects updates made by other entities
        self._unsub = self._device.add_listener(self._device_updated)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    def _device_updated(self) -> None:
        # Called from device thread; schedule HA state update
        self.schedule_update_ha_state()

    @property
    def is_on(self) -> bool:
        return self._device.tier_enabled[self._tier]

    @property
    def available(self) -> bool:
        return True

    @property
    def color_mode(self) -> ColorMode:
        return ColorMode.ONOFF

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, f"{self._device.host}:{self._device.port}")},
            "manufacturer": "Patlite",
            "name": f"Patlite @ {self._device.host}",
            "model": "UDP Tower",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._device.set_tier_power(self._tier, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._device.set_tier_power(self._tier, False)
        self.async_write_ha_state()
