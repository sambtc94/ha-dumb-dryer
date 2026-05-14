"""Data coordinator for dumb dryer state detection."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_COOLING_THRESHOLD,
    CONF_FINISHED_HOLD,
    CONF_OFF_THRESHOLD,
    CONF_POWER_SENSOR,
    CONF_RUNNING_THRESHOLD,
    CONF_START_DEBOUNCE,
    CONF_STOP_DEBOUNCE,
    CONF_UPDATE_INTERVAL,
    COORDINATOR_NAME,
    DEFAULT_COOLING_THRESHOLD,
    DEFAULT_FINISHED_HOLD,
    DEFAULT_OFF_THRESHOLD,
    DEFAULT_RUNNING_THRESHOLD,
    DEFAULT_START_DEBOUNCE,
    DEFAULT_STOP_DEBOUNCE,
    DEFAULT_UPDATE_INTERVAL,
    STATE_COOLING,
    STATE_FINISHED,
    STATE_OFF,
    STATE_RUNNING,
)

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class DryerData:
    """Runtime data for the dryer."""

    power_w: float
    state: str
    cycle_active: bool
    source_entity: str
    updated_at: datetime


class DryerCoordinator(DataUpdateCoordinator[DryerData]):
    """Coordinate dryer power updates and state detection."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.config_entry = config_entry
        self._state = STATE_OFF
        self._cycle_active = False
        self._candidate_state: str | None = None
        self._candidate_since: datetime | None = None
        self._finished_until: datetime | None = None

        super().__init__(
            hass,
            logger=LOGGER,
            name=COORDINATOR_NAME,
            update_interval=timedelta(seconds=self._setting(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)),
        )

    def _setting(self, key: str, default: Any) -> Any:
        """Return option if set, else config data, else default."""
        return self.config_entry.options.get(key, self.config_entry.data.get(key, default))

    async def _async_update_data(self) -> DryerData:
        """Fetch power sensor value and update dryer state."""
        now = dt_util.utcnow()
        power_sensor = self._setting(CONF_POWER_SENSOR, None)
        if not power_sensor:
            raise UpdateFailed("Power sensor is not configured")

        sensor_state = self.hass.states.get(power_sensor)
        if sensor_state is None:
            raise UpdateFailed(f"Sensor '{power_sensor}' not found")
        if sensor_state.state in ("unknown", "unavailable"):
            raise UpdateFailed(f"Sensor '{power_sensor}' is {sensor_state.state}")

        try:
            power_w = float(sensor_state.state)
        except (TypeError, ValueError) as err:
            raise UpdateFailed(f"Sensor '{power_sensor}' is not numeric") from err

        self.update_interval = timedelta(
            seconds=self._setting(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        self._transition_state(power_w, now)

        return DryerData(
            power_w=power_w,
            state=self._state,
            cycle_active=self._cycle_active,
            source_entity=power_sensor,
            updated_at=now,
        )

    def _transition_state(self, power_w: float, now: datetime) -> None:
        """Apply threshold and debounce logic for dryer state."""
        off_threshold = float(self._setting(CONF_OFF_THRESHOLD, DEFAULT_OFF_THRESHOLD))
        cooling_threshold = float(
            self._setting(CONF_COOLING_THRESHOLD, DEFAULT_COOLING_THRESHOLD)
        )
        running_threshold = float(
            self._setting(CONF_RUNNING_THRESHOLD, DEFAULT_RUNNING_THRESHOLD)
        )
        start_debounce = timedelta(
            seconds=int(self._setting(CONF_START_DEBOUNCE, DEFAULT_START_DEBOUNCE))
        )
        stop_debounce = timedelta(
            seconds=int(self._setting(CONF_STOP_DEBOUNCE, DEFAULT_STOP_DEBOUNCE))
        )
        finished_hold = timedelta(
            seconds=int(self._setting(CONF_FINISHED_HOLD, DEFAULT_FINISHED_HOLD))
        )

        if power_w >= running_threshold:
            target_state = STATE_RUNNING
        elif power_w >= cooling_threshold:
            target_state = STATE_COOLING
        elif power_w <= off_threshold:
            target_state = STATE_OFF
        else:
            # Keep a deadband between OFF and COOLING thresholds to avoid
            # flapping from short low-power spikes between tumble segments.
            target_state = None

        if self._state == STATE_FINISHED:
            if target_state == STATE_RUNNING:
                self._finished_until = None
            elif self._finished_until and now < self._finished_until:
                return
            else:
                self._state = STATE_OFF
                self._finished_until = None

        if target_state is None or target_state == self._state:
            self._candidate_state = None
            self._candidate_since = None
            return

        if target_state != self._candidate_state:
            self._candidate_state = target_state
            self._candidate_since = now
            return

        if self._candidate_since is None:
            self._candidate_since = now
            return

        debounce = start_debounce if target_state in (STATE_RUNNING, STATE_COOLING) else stop_debounce
        if now - self._candidate_since < debounce:
            return

        previous_state = self._state
        self._state = target_state
        self._candidate_state = None
        self._candidate_since = None

        if self._state == STATE_RUNNING:
            self._cycle_active = True
            self._finished_until = None
            return

        if self._state == STATE_OFF and self._cycle_active and previous_state in (STATE_RUNNING, STATE_COOLING):
            self._state = STATE_FINISHED
            self._cycle_active = False
            self._finished_until = now + finished_hold
