from __future__ import annotations
from typing import Any, Callable

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, COLOR_MAP, INV_COLOR_MAP, NUM_TIERS
from .device import PatliteDevice

OPTIONS = list(COLOR_MAP.keys())


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    device: PatliteDevice = hass.data[DOMAIN][entry.entry_id]["device"]
    entities = [PatliteTierSelect(device, tier=i) for i in range(NUM_TIERS)]
    async_add_entities(entities)


class PatliteTierSelect(SelectEntity):
    _attr_icon = "mdi:palette"
    def __init__(self, device: PatliteDevice, tier: int):
        self._device = device
        self._tier = tier
        self._attr_name = f"Patlite Tier {tier+1} Color"
        self._attr_unique_id = f"{device.host}:{device.port}-tier{tier}-color"
        self._attr_options = OPTIONS
        self._attr_should_poll = False
        self._unsub: Callable[[], None] | None = None

    @property
    def current_option(self) -> str | None:
        code = self._device.tier_colors[self._tier]
        if code == 0x00:
            last = self._device.get_last_color_code(self._tier)
            return INV_COLOR_MAP.get(last, "Off") if last is not None else "Off"
        return INV_COLOR_MAP.get(code, "Off")

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, f"{self._device.host}:{self._device.port}")},
            "manufacturer": "Patlite",
            "name": f"Patlite @ {self._device.host}",
            "model": "UDP Tower",
        }

    async def async_select_option(self, option: str) -> None:
        if option not in COLOR_MAP:
            raise ValueError(f"Invalid color option: {option}")
        if option == "Off":
            # Power off but do not overwrite the last chosen color
            self._device.set_tier_power(self._tier, False)
        else:
            code = COLOR_MAP[option]
            self._device.set_tier_color(self._tier, code)
            self._device.set_tier_power(self._tier, True)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self._unsub = self._device.add_listener(self._device_updated)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    def _device_updated(self) -> None:
        # called from driver; schedule HA state refresh
        self.schedule_update_ha_state()