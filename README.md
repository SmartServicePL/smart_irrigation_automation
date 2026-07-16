# Smart Irrigation Automation

Home Assistant automation blueprint for intelligent garden irrigation from 1 to 8 sections.

Prepared by **Smart Service**.

Current version: **1.2.0**

## Import Blueprint

[![Open your Home Assistant instance and import this blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml)

Manual import URL:

```text
https://github.com/SmartServicePL/smart_irrigation_automation/blob/main/blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

## Donate

[![Donate via Revolut](https://img.shields.io/badge/Donate-Revolut-0666EB?style=for-the-badge)](https://revolut.me/smartserwis)

## Smart Irrigation

The blueprint calculates one irrigation decision for the whole enabled cycle.
It accumulates a modeled water need from plant demand, soil, temperature,
sunlight, rain and optional soil moisture. When watering is needed, every
enabled and ready section is run; each section still gets its own calculated
runtime from its sprinkler profile, soil, plants and manual adjustment.

The target cycles-per-week setting is used only as a startup/fallback assumption
when a section has no watering history, and to estimate the next cycle after a
fresh watering. It does not assign weekdays and never forces watering merely
because a scheduled day arrived. With Rain Bird RC2, confirmed section
completion times are persisted by the integration and used by the next cycle
decision.

Supported section count is configurable from 1 to 8. Sections above the selected count stay in the blueprint configuration but are ignored by the automation.

Rain Bird is the primary target, with detailed profiles for 5000/3500 rotors, 1800 sprays, R-VAN rotary nozzles and XF dripline. Generic Rain Bird, Hunter and custom mm/h profiles are still available.

Watering need is calculated with a simplified water-balance model inspired by
FAO-56 and extension irrigation scheduling guides. The blueprint estimates daily
crop water use as `ETc = ETo * Kc`, subtracts useful rain, then starts watering
when the modeled depletion reaches the allowed root-zone depletion for the
selected soil and plant type. If you have a daily ETo sensor, select it; otherwise
the blueprint estimates ETo from temperature, UV/sun and wind.

Soil selection uses garden-friendly names instead of geological labels:
piaszczysta / bardzo lekka, lekka ogrodowa, zwykla ziemia ogrodowa,
humusowa / prochniczna, czarnoziem / czarna ziemia, gliniasta / ciezka and
bardzo ciezka / zbita glina. Existing configurations using the older technical
values remain compatible.

For native Rain Bird RC2 switch entities, the blueprint automatically uses
`rainbird_rc2.start_zone` and passes the calculated runtime in minutes. Other
switch integrations continue to use standard `switch.turn_on`.

The blueprint waits for the valve or switch to confirm `on/open` before reporting that watering started. A missing start confirmation or an early controller stop is reported as an irrigation failure instead of a completed section.

Optional logging writes the deficit, start threshold, watering decision and
confirmed duration to Home Assistant Logbook. Persistent notifications are kept
for user-visible events: watering start, watering end, skipped watering and
interrupted watering.

Optional condition checks can run during the day and night, by default at
12:00, 18:00, 00:00 and 03:00. These checks fetch current weather and recalculate
watering need and update the next-watering helper, but they do not open
irrigation sections or create Home Assistant notifications.

Optionally, select an `input_datetime` helper in the blueprint to store the
estimated next watering time. The automation updates it after each check: when
weather blocks watering it stores the next scheduled check, and when watering
is not yet needed it stores the first scheduled cycle after the modeled water
need reaches the start threshold.

Documentation:

- [Smart irrigation setup](docs/smart-irrigation.md)
- [Translations and UI glossary](docs/i18n/README.md): English, German, Spanish,
  French, Italian, Dutch and Portuguese.

Blueprint path:

```text
blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

## Requirements

- Home Assistant 2025.1.0 or newer.
- One `valve` or `switch` entity per irrigation section.
- A `weather` entity that supports daily forecast.
- Optional local weather entity, rain sensor, rain amount sensor, temperature sensor, wind source, UV/sunlight source and soil moisture sensor.
- Optional Logbook diagnostics and persistent notifications for user-visible irrigation events.

## Privacy

Do not publish Home Assistant storage files, access tokens, exact home address, raw API responses or screenshots showing private garden details.
