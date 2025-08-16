from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.const import CONF_ENTITY_ID, CONF_TYPE
from homeassistant.core import HomeAssistant, Context
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.components.device_automation import DEVICE_ACTION_SCHEMA
from homeassistant.components.select import (
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)

# One action type: set the colour of a Patlite tier (Select entity)
ACTION_TYPE_SET_COLOR = "set_color"

# Base schema for our action (entity + type); 'option' will be provided via capabilities
ACTION_SCHEMA = DEVICE_ACTION_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In([ACTION_TYPE_SET_COLOR]),
        vol.Required(CONF_ENTITY_ID): cv.entity_domain(SELECT_DOMAIN),
    }
)


async def async_get_actions(hass: HomeAssistant, device_id: str) -> list[dict[str, Any]]:
    """Return device actions for all Patlite Select entities on this device."""
    registry = er.async_get(hass)
    actions: list[dict[str, Any]] = []

    for entry in registry.entities.values():
        if entry.device_id != device_id:
            continue
        if entry.domain != SELECT_DOMAIN:
            continue

        actions.append(
            {
                CONF_TYPE: ACTION_TYPE_SET_COLOR,
                CONF_ENTITY_ID: entry.entity_id,
            }
        )

    return actions


async def async_get_action_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """Return extra fields (capabilities) for the selected action.

    We read the current Select entity's options and expose them as a dropdown.
    """
    entity_id = config[CONF_ENTITY_ID]
    state = hass.states.get(entity_id)
    options = []
    if state and isinstance(state.attributes, dict):
        # Select entities expose their options under the 'options' attribute
        options = list(state.attributes.get("options", []))

    schema = vol.Schema({vol.Required("option"): vol.In(options)}) if options else vol.Schema(
        {vol.Required("option"): cv.string}
    )
    return {"extra_fields": schema}


async def async_call_action_from_config(
    hass: HomeAssistant, config: ConfigType, variables: dict[str, Any], context: Context
) -> None:
    """Execute the configured action."""
    if config[CONF_TYPE] == ACTION_TYPE_SET_COLOR:
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {CONF_ENTITY_ID: config[CONF_ENTITY_ID], "option": config["option"]},
            blocking=True,
            context=context,
        )


async def async_validate_action_config(hass: HomeAssistant, config: ConfigType) -> ConfigType:
    """Validate the device action config."""
    return ACTION_SCHEMA(config)
