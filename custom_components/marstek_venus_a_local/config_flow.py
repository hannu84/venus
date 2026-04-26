"""Config flow for Marstek Venus A Local."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import MarstekApiError, MarstekVenusAApi
from .const import (
    CONF_DEVICE_HOST,
    CONF_PV1_FACTOR,
    CONF_SCAN_INTERVAL,
    CONF_UDP_PORT,
    DEFAULT_PV1_FACTOR,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UDP_PORT,
    DOMAIN,
)


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = MarstekVenusAApi(host=data[CONF_DEVICE_HOST], port=data[CONF_UDP_PORT])
    result = await api.async_fetch_all(pv1_factor=data[CONF_PV1_FACTOR])
    if result["battery_soc"] is None:
        raise MarstekApiError("Device answered but battery_soc is missing")
    return {"title": f"Marstek Venus A ({data[CONF_DEVICE_HOST]})"}


class MarstekVenusALocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Marstek Venus A Local."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(user_input)
            except (MarstekApiError, OSError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_DEVICE_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_HOST, default=user_input.get(CONF_DEVICE_HOST) if user_input else ""): str,
                vol.Required(CONF_UDP_PORT, default=user_input.get(CONF_UDP_PORT, DEFAULT_UDP_PORT) if user_input else DEFAULT_UDP_PORT): int,
                vol.Required(CONF_PV1_FACTOR, default=user_input.get(CONF_PV1_FACTOR, DEFAULT_PV1_FACTOR) if user_input else DEFAULT_PV1_FACTOR): vol.Coerce(float),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=user_input.get(CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())) if user_input else int(DEFAULT_SCAN_INTERVAL.total_seconds()),
                ): selector.NumberSelector(selector.NumberSelectorConfig(min=5, max=120, mode=selector.NumberSelectorMode.BOX)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle reconfigure."""
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return MarstekVenusALocalOptionsFlow(config_entry)


class MarstekVenusALocalOptionsFlow(config_entries.OptionsFlow):
    """Options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PV1_FACTOR,
                    default=self.config_entry.options.get(CONF_PV1_FACTOR, self.config_entry.data[CONF_PV1_FACTOR]),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(CONF_SCAN_INTERVAL, self.config_entry.data[CONF_SCAN_INTERVAL]),
                ): selector.NumberSelector(selector.NumberSelectorConfig(min=5, max=120, mode=selector.NumberSelectorMode.BOX)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
