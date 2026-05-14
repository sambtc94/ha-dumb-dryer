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

### HACS

1. Add this repository to HACS as a custom repository with the **Integration** category.
2. Install **Dumb Dryer** from HACS.
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration**.
5. Search for **Dumb Dryer**.
6. Choose your power sensor and configure thresholds.

For stable HACS installs, publish GitHub releases that match the integration version in `custom_components/dumb_dryer/manifest.json`.

### Manual

1. Copy `custom_components/dumb_dryer` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration**.
4. Search for **Dumb Dryer**.
5. Choose your power sensor and configure thresholds.

You can later adjust thresholds and the source power sensor from the integration **Configure** options in the UI.
