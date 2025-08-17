from __future__ import annotations
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.components.dhcp import DhcpServiceInfo

from .const import DOMAIN, UDP_PORT_DEFAULT


class PatliteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    _discovered: dict[str, Any] | None = None  # store pending DHCP discovery

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            # If we already set unique_id earlier (e.g., via DHCP), abort if configured
            await self.async_set_unique_id(user_input.get("mac") or self.unique_id or user_input[CONF_HOST])
            self._abort_if_unique_id_configured()
            data = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: int(user_input.get(CONF_PORT, UDP_PORT_DEFAULT)),
            }
            return self.async_create_entry(title=f"Patlite {data[CONF_HOST]}", data=data)

        # If we have a pending DHCP discovery, suggest its values
        defaults = {}
        if self._discovered:
            defaults[CONF_HOST] = self._discovered["host"]
            defaults[CONF_PORT] = self._discovered.get("port", UDP_PORT_DEFAULT)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, UDP_PORT_DEFAULT)): int,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)

    async def async_step_import(self, import_config: dict[str, Any]) -> FlowResult:
        """Support YAML import if you add it later."""
        return await self.async_step_user(import_config)

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo) -> FlowResult:
        """Handle DHCP discovery.

        Called by HA when a device with a matching OUI/hostname appears on the network.
        """
        host = discovery_info.ip
        mac = (discovery_info.macaddress or "").lower()

        # Use MAC as unique_id to keep one entry per physical tower.
        if mac:
            await self.async_set_unique_id(mac)
            # If already configured, update host (IP may change via DHCP) and abort.
            self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        # Not configured yet — store discovery and ask user to confirm or edit port.
        self._discovered = {"host": host}
        # Go straight to the user form with suggested host/port
        return await self.async_step_user()
