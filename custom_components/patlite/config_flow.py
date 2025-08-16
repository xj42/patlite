from __future__ import annotations

import ipaddress
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, UDP_PORT_DEFAULT
from homeassistant.const import CONF_HOST, CONF_PORT


def _is_valid_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        # permit simple hostnames too
        if not host or " " in host:
            return False
        return True


class PatliteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input.get(CONF_HOST, "").strip()
            port = int(user_input.get(CONF_PORT, UDP_PORT_DEFAULT))

            if not _is_valid_host(host):
                errors[CONF_HOST] = "invalid_host"

            if not errors:
                # Use host:port as unique ID to prevent duplicates
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Patlite @ {host}", data={CONF_HOST: host, CONF_PORT: port})

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=UDP_PORT_DEFAULT): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
