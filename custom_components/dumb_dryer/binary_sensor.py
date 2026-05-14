"""Binary sensor platform for Dumb Dryer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, STATE_COOLING, STATE_FINISHED, STATE_RUNNING
from .entity import DumbDryerEntity


@dataclass(frozen=True, kw_only=True)
class DryerBinaryDescription(BinarySensorEntityDescription):
    """Description for dryer binary sensors."""

    value_fn: Callable[[str, bool], bool]


DESCRIPTIONS: tuple[DryerBinaryDescription, ...] = (
    DryerBinaryDescription(
        key="running",
        translation_key="running",
        name="Running",
        icon="mdi:tumble-dryer",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda state, cycle_active: state == STATE_RUNNING,
    ),
    DryerBinaryDescription(
        key="cooling",
        translation_key="cooling",
        name="Cooling",
        icon="mdi:snowflake-thermometer",
        value_fn=lambda state, cycle_active: state == STATE_COOLING,
    ),
    DryerBinaryDescription(
        key="finished",
        translation_key="finished",
        name="Finished",
        icon="mdi:check-circle",
        value_fn=lambda state, cycle_active: state == STATE_FINISHED,
    ),
    DryerBinaryDescription(
        key="cycle_active",
        translation_key="cycle_active",
        name="Cycle Active",
        icon="mdi:progress-clock",
        value_fn=lambda state, cycle_active: cycle_active,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up dumb dryer binary sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DumbDryerBinarySensor(coordinator, description) for description in DESCRIPTIONS
    )


class DumbDryerBinarySensor(DumbDryerEntity, BinarySensorEntity):
    """Binary sensor for coordinator-backed dryer state."""

    entity_description: DryerBinaryDescription

    def __init__(self, coordinator, description: DryerBinaryDescription) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{self.coordinator.config_entry.entry_id}_{self.entity_description.key}"
        )

    @property
    def is_on(self) -> bool:
        """Return true if binary state is on."""
        return self.entity_description.value_fn(
            self.coordinator.data.state,
            self.coordinator.data.cycle_active,
        )
