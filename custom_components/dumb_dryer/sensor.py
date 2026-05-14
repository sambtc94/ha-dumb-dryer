"""Sensor platform for Dumb Dryer."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VALID_STATES
from .entity import DumbDryerEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up dumb dryer sensor entities from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            DryerStateSensor(coordinator),
            DryerPowerSensor(coordinator),
        ]
    )


class DryerStateSensor(DumbDryerEntity, SensorEntity):
    """Expose dryer state."""

    _attr_name = "State"
    _attr_translation_key = "state"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:tumble-dryer"
    _attr_options = VALID_STATES

    @property
    def native_value(self) -> str:
        """Return current dryer state."""
        return self.coordinator.data.state

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return f"{self.coordinator.config_entry.entry_id}_state"


class DryerPowerSensor(DumbDryerEntity, SensorEntity):
    """Expose current power being evaluated."""

    _attr_name = "Power"
    _attr_translation_key = "power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_suggested_display_precision = 1

    @property
    def native_value(self) -> float:
        """Return current power."""
        return self.coordinator.data.power_w

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        return f"{self.coordinator.config_entry.entry_id}_power"
