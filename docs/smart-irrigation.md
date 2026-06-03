# Smart irrigation setup

[![Open your Home Assistant instance and import this blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml)

`blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml` adds intelligent Home Assistant irrigation for 1 to 8 garden sections.

## How it works

The automation starts from a fixed time, sunrise or sunset with configurable offset. Before watering it checks season, current weather, rain forecast, physical rain sensor, temperature, wind and optional soil moisture.

For every active section it calculates a water dose and runtime from:

- plant type: grass, flowers, vegetables or shrubs,
- soil type: sand, sandy loam, loam, clay loam or clay,
- sprinkler profile: Rain Bird or Hunter rotors, sprays, drip lines, Hunter MP Rotator or custom mm/h,
- recent/forecast rain,
- temperature, sunlight/UV and optional soil moisture,
- irrigation efficiency and per-section runtime correction.

If rain starts while a section is running, the automation closes the valve and stops the remaining sections.

## Recommended setup

Use one automation instance per garden controller or area. Set **Liczba sekcji** to the real number of sections. Fill only those sections; later sections may stay with defaults.

Good starting values:

- Start mode: sunrise.
- Sun offset: `-30` minutes.
- Season: `4-10`.
- Waterings per week: `3`.
- Minimum dose: `3 mm`.
- Maximum dose: `10 mm`.
- Minimum runtime: `8 min`.
- Maximum runtime: `45 min`.
- Irrigation efficiency: `75%`.

## Section settings

Each section has its own:

- valve or switch entity,
- display name,
- soil type,
- plant type,
- sprinkler profile,
- optional custom precipitation rate in `mm/h`,
- runtime correction,
- optional online sensor,
- optional battery sensor.

The runtime correction is useful when one section is drier, has lower pressure or gets more sun. `100%` means no correction, `120%` makes the section run longer, `80%` makes it shorter.

## Installation

Click the **Import Blueprint** button above, or import this URL manually in Home Assistant:

```text
https://github.com/SmartServicePL/smart_irrigation_automation/blob/main/blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

Manual file installation:

Copy the blueprint file to:

```text
/config/blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

Reload automations or restart Home Assistant, then create a new automation from the blueprint.
