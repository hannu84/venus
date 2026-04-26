# Marstek Venus A Local

Home Assistant custom integration for the Marstek Venus A using the local UDP JSON-RPC API on port `30000`.

## Features

- Local polling, no cloud required
- Config Flow in Home Assistant UI
- Sensors for:
  - Battery SOC
  - Battery temperature
  - PV1 to PV4 power
  - PV total power
  - Grid power
  - Offgrid power
  - Meter total power
  - Total grid input/output energy
  - Operating mode
  - WiFi RSSI

## Notes

- `PV1` is scaled by `0.1` by default because this channel appears to use a different multiplier on the tested device.
- Polling is intentionally conservative because the Marstek local API can become unstable if queried too aggressively.

## Installation with HACS

1. Push this repository to GitHub.
2. In HACS, add it as a custom repository.
3. Choose category `Integration`.
4. Install `Marstek Venus A Local`.
5. Restart Home Assistant.
6. Add the integration from `Settings -> Devices & Services`.
