from __future__ import annotations
from typing import Any, Callable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import PatliteDevice


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    device: PatliteDevice = hass.data[DOMAIN][entry.entry_id]["device"]
    async_add_entities([PatliteFlashSwitch(device), PatliteBuzzerSwitch(device)])


class _BaseSwitch(SwitchEntity):
    def __init__(self, device: PatliteDevice, name: str, key: str):
        self._device = device
        self._attr_name = name
        self._attr_unique_id = f"{device.host}:{device.port}-{key}"
        self._attr_should_poll = False
        self._unsub: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        self._unsub = self._device.add_listener(self._device_updated)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    def _device_updated(self) -> None:
        self.schedule_update_ha_state()

    @property
    def available(self) -> bool:
        return True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"{self._device.host}:{self._device.port}")},
            "manufacturer": "Patlite",
            "name": f"Patlite @ {self._device.host}",
            "model": "UDP Tower",
        }


class PatliteFlashSwitch(_BaseSwitch):
    _attr_icon = "mdi:alarm-light-outline"
    def __init__(self, device: PatliteDevice):
        super().__init__(device, "Patlite Flash", "flash")

    @property
    def is_on(self) -> bool:
        return bool(self._device.flash)

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._device.set_flash(1)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._device.set_flash(0)
        self.async_write_ha_state()


class PatliteBuzzerSwitch(_BaseSwitch):
    _attr_icon = "mdi:volume-high"
    def __init__(self, device: PatliteDevice):
        super().__init__(device, "Patlite Buzzer", "buzzer")

    @property
    def is_on(self) -> bool:
        return bool(self._device.buzzer)

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._device.set_buzzer(1)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._device.set_buzzer(0)
        self.async_write_ha_state()
