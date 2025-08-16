from __future__ import annotations
from typing import Any
import os, shutil
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PORT
from .device import PatliteDevice

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SELECT, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    host: str = entry.data[CONF_HOST]
    port: int = int(entry.data[CONF_PORT])

    device = PatliteDevice(host, port)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = {"device": device}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    src = os.path.join(os.path.dirname(__file__), "www/tower.gif")
    dest_dir = os.path.join(hass.config.path("www"))
    dest = os.path.join(dest_dir, "tower.gif")
    if not os.path.exists(dest):
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copyfile(src, dest)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
    return unload_ok
