"""Config flow for Dumb Dryer integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    CONF_COOLING_THRESHOLD,
    CONF_FINISHED_HOLD,
    CONF_OFF_THRESHOLD,
    CONF_POWER_SENSOR,
    CONF_RUNNING_THRESHOLD,
    CONF_START_DEBOUNCE,
    CONF_STOP_DEBOUNCE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_COOLING_THRESHOLD,
    DEFAULT_FINISHED_HOLD,
    DEFAULT_OFF_THRESHOLD,
    DEFAULT_RUNNING_THRESHOLD,
    DEFAULT_START_DEBOUNCE,
    DEFAULT_STOP_DEBOUNCE,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    """Build UI schema for config and options."""
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, "Dryer")): selector.TextSelector(),
            vol.Required(
                CONF_POWER_SENSOR,
                default=defaults.get(CONF_POWER_SENSOR),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor"], multiple=False)
            ),
            vol.Required(
                CONF_OFF_THRESHOLD,
                default=defaults.get(CONF_OFF_THRESHOLD, DEFAULT_OFF_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=3000, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
            vol.Required(
                CONF_COOLING_THRESHOLD,
                default=defaults.get(CONF_COOLING_THRESHOLD, DEFAULT_COOLING_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=3000, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
            vol.Required(
                CONF_RUNNING_THRESHOLD,
                default=defaults.get(CONF_RUNNING_THRESHOLD, DEFAULT_RUNNING_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=5000, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
            vol.Required(
                CONF_START_DEBOUNCE,
                default=defaults.get(CONF_START_DEBOUNCE, DEFAULT_START_DEBOUNCE),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=900, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
            vol.Required(
                CONF_STOP_DEBOUNCE,
                default=defaults.get(CONF_STOP_DEBOUNCE, DEFAULT_STOP_DEBOUNCE),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=1800, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
            vol.Required(
                CONF_FINISHED_HOLD,
                default=defaults.get(CONF_FINISHED_HOLD, DEFAULT_FINISHED_HOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=3600, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
            vol.Required(
                CONF_UPDATE_INTERVAL,
                default=defaults.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=5, max=120, mode=selector.NumberSelectorMode.BOX, step=1)
            ),
        }
    )


class DumbDryerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Dumb Dryer."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_thresholds(user_input)
            if not errors:
                await self.async_set_unique_id(user_input[CONF_POWER_SENSOR])
                self._abort_if_unique_id_configured()
                name = user_input.get(CONF_NAME, "Dryer")
                data = {key: value for key, value in user_input.items() if key != CONF_NAME}
                return self.async_create_entry(title=name, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get options flow handler."""
        return DumbDryerOptionsFlow(config_entry)


class DumbDryerOptionsFlow(config_entries.OptionsFlow):
    """Handle Dumb Dryer options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_thresholds(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        defaults = {**self._config_entry.data, **self._config_entry.options, CONF_NAME: self._config_entry.title}
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(defaults),
            errors=errors,
        )


def _validate_thresholds(values: dict[str, Any]) -> dict[str, str]:
    """Validate threshold relationships."""
    off_threshold = float(values[CONF_OFF_THRESHOLD])
    cooling_threshold = float(values[CONF_COOLING_THRESHOLD])
    running_threshold = float(values[CONF_RUNNING_THRESHOLD])

    if not off_threshold <= cooling_threshold <= running_threshold:
        return {"base": "invalid_thresholds"}
    return {}
