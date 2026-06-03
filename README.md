# Smart Irrigation Automation

Home Assistant automation blueprint for intelligent garden irrigation from 1 to 8 sections.

Prepared by **Smart Service**.

## Import Blueprint

[![Open your Home Assistant instance and import this blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml)

Manual import URL:

```text
https://github.com/SmartServicePL/smart_irrigation_automation/blob/main/blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

## Donate

[![Donate via Revolut](https://img.shields.io/badge/Donate-Revolut-0666EB?style=for-the-badge)](https://revolut.me/smartserwis)

## Smart Irrigation

The blueprint calculates irrigation time for each section from shared weather/sensor data and per-section garden settings. Common inputs include weather forecast, local weather, rain sensor, rain amount, temperature, wind, sunlight/UV and optional soil moisture. Each section has its own valve, name, soil type, plant type, sprinkler profile, custom precipitation rate, runtime correction, online sensor and battery sensor.

Supported section count is configurable from 1 to 8. Sections above the selected count stay in the blueprint configuration but are ignored by the automation.

Documentation:

- [Smart irrigation setup](docs/smart-irrigation.md)

Blueprint path:

```text
blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

## Requirements

- Home Assistant 2025.1.0 or newer.
- One `valve` or `switch` entity per irrigation section.
- A `weather` entity that supports daily forecast.
- Optional local weather entity, rain sensor, rain amount sensor, temperature sensor, wind source, UV/sunlight source and soil moisture sensor.

## Privacy

Do not publish Home Assistant storage files, access tokens, exact home address, raw API responses or screenshots showing private garden details.
