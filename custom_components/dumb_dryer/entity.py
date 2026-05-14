"""Shared entities for Dumb Dryer."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DryerCoordinator


class DumbDryerEntity(CoordinatorEntity[DryerCoordinator]):
    """Base entity for dumb dryer entities."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return integration device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=self.coordinator.config_entry.title,
            manufacturer="Home Assistant Custom",
            model="Power-based Dryer Monitor",
        )
