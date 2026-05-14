# ha-dumb-dryer

A Home Assistant custom integration that monitors a dryer power sensor and infers dryer state.

## Features

- Creates a dedicated dryer device in Home Assistant
- Uses a `DataUpdateCoordinator` and async patterns
- Detects:
  - `OFF`
  - `RUNNING`
  - `COOLING`
  - `FINISHED`
- Detects completed cycles with debounce and hold timers to avoid false positives
- Exposes:
  - Sensors: dryer state, current power
  - Binary sensors: running, cooling, finished, cycle active
- Full UI configuration for:
  - Source power sensor entity
  - Off/cooling/running thresholds
  - Debounce and update timing values

## Install

1. Copy `custom_components/dumb_dryer` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**.
4. Search for **Dumb Dryer**.
5. Choose your power sensor and configure thresholds.

You can later adjust thresholds and the source power sensor from the integration **Configure** options in the UI.
