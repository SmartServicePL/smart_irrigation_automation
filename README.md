# Smart Irrigation Automation

Home Assistant automation blueprint for intelligent garden irrigation from 1 to 12 sections.

Prepared by **Smart Service**.

Current version: **1.5.0**

## Import Blueprint

[![Open your Home Assistant instance and import this blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml)

Manual import URL:

```text
https://github.com/SmartServicePL/smart_irrigation_automation/blob/main/blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml
```

## Donate

[![Donate via Revolut](https://img.shields.io/badge/Donate-Revolut-0666EB?style=for-the-badge)](https://revolut.me/smartserwis)

## New in 1.5.0: persistent per-section water balance

Version 1.5.0 adds a checkbook-style water balance that survives Home Assistant
restarts. One compact `input_text` helper stores the current soil-water deficit
for all 12 sections, the last update time and the last observed measured-rain
total. Each check adds elapsed `ETo * Kc`, subtracts only newly measured
effective rain, and every confirmed section run subtracts the water it applied.
A falling rolling-24-hour rain value no longer makes old rain disappear from the
model.

Forecast rain is now a start delay only. It is never booked as water received
until a gauge or MeteoFusion reports it. The weekly-cycle setting has been
removed from the decision model; watering is triggered exclusively by section
depletion, weather and safety conditions. Existing automations without the new
helper keep a compatibility calculation so an imported update does not disable
them, but persistent operation is strongly recommended.

Create one Home Assistant **Text** helper with a maximum length of `255`, then
select it as **Helper - trwaly bilans wody**. The first run initializes a safe
zero balance and later checks build the real deficit automatically.

## New in 1.4.0: quiet daily decisions and corrected water balance

Version 1.4.0 separates four optional condition checks from the single daily
execution decision. Condition checks update the next-watering helper and may
write diagnostic Logbook entries, but they cannot create a skipped-watering
notification. On a watering day, the persistent notification is first written
only after a valve confirms that it is open, then replaced by the final result.
On a non-watering day there is one readable skipped-watering result.

The water-balance model now treats a configured soil-moisture sensor as a direct
irrigation override at a configurable threshold, normalizes wind speed to km/h,
and carries forward water that a section could not deliver because of its
maximum runtime. Final section results show confirmed runtime and estimated net
water applied. For measured rain, select a rolling 24-hour or cumulative
rain-event sensor when available. The persistent model stores only new
increments and retains their effect when the rolling value later falls.

## New in 1.3.0: MeteoFusion HA

Version 1.3.0 adds native weather intelligence from
[MeteoFusion HA](https://github.com/SmartServicePL/meteofusion-ha). Setup is
intentionally short:

1. Select the MeteoFusion `weather` entity as **Encja pogody do prognozy**.
2. Enable **Korzystaj z danych MeteoFusion HA**.
3. Leave **Opcjonalne sensory lokalne i nadpisania** collapsed and empty unless
   a dedicated garden sensor should override one measurement.

The blueprint then receives a rolling next-24-hour rain forecast, daily FAO-56 ETo, current
local-station conditions and forecast-quality diagnostics. It refuses unsafe
decisions when the MeteoFusion contract is missing, confidence is too low or
station data is stale. Existing non-MeteoFusion weather setups remain
compatible by leaving the new option disabled.

## Smart Irrigation

The blueprint calculates one irrigation decision for the whole enabled cycle.
It accumulates a modeled water need from plant demand, soil, temperature,
sunlight, rain and optional soil moisture. When watering is needed, every
enabled and ready section is run; each section still gets its own calculated
runtime from its sprinkler profile, soil, plants and manual adjustment.

There are no fixed watering weekdays or target runs per week. A persistent
water balance decides when the first section reaches its soil/root-zone
threshold. The planned cycle then waters every enabled and ready section, with
an individually calculated runtime and applied-depth correction.

Supported section count is configurable from 1 to 12. Sections above the selected count stay in the blueprint configuration but are ignored by the automation.

Controllers may be mixed in one automation. For example, sections 1-8 can use
native Rain Bird RC2 entities while sections 9-12 use Sonoff, Shelly or ESPHome
relays for drip lines. The automation runs them sequentially and applies the
same weather checks, water-balance decision and per-section runtime calculation
to every enabled section.

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
switch integrations use standard `switch.turn_on`, wait for confirmation, keep
the section active for the calculated time and then call `switch.turn_off`.
Normal `valve` entities are handled with `valve.open_valve` and
`valve.close_valve`.

## MeteoFusion HA

Enable **Korzystaj z danych MeteoFusion HA** after selecting a MeteoFusion
weather entity. The blueprint validates its `smart_service.weather.v1`
contract and then uses:

- the rolling next-24-hour precipitation sum and maximum rain probability,
- daily FAO-56 ETo without requiring a separate sensor selection,
- local-station rain rate, rain total, temperature and wind,
- forecast confidence, source count and station freshness.

Explicitly selected rain, temperature, wind, UV or ETo sensors keep priority, so
MeteoFusion can be combined with dedicated garden sensors. Low-confidence or
stale MeteoFusion data safely skips irrigation with a readable explanation.
The optional local sensors are grouped in a collapsed section and may all stay
empty for a MeteoFusion-only setup. Ordinary `weather` entities remain fully
supported with the MeteoFusion option disabled.

The blueprint waits for the valve or switch to confirm `on/open` before reporting that watering started. A missing start confirmation or an early controller stop is reported as an irrigation failure instead of a completed section.

Optional logging writes the deficit, start threshold, watering decision and
confirmed duration to Home Assistant Logbook. Persistent notifications are kept
to one daily lifecycle: start after the first section confirms opening and a
final completed result, or one skipped result when no watering begins. A safety
interruption replaces the final result with a completed-before-time explanation.
All use one notification ID, so the HA panel shows the current outcome instead
of accumulating a stack of messages.

Optional condition checks can run during the day and night, by default at
12:00, 18:00, 00:00 and 03:00. These checks fetch current weather and recalculate
watering need and update the next-watering helper, but they do not open
irrigation sections or create Home Assistant notifications.

Optionally, select an `input_datetime` helper in the blueprint to store the
estimated next watering time. The automation updates it after each check: when
weather blocks watering it stores the next scheduled check, and when watering
is not yet needed it stores the first scheduled cycle after the modeled water
need reaches the start threshold.

For the calculation itself, create one `input_text` helper with maximum length
`255` and select **Helper - trwaly bilans wody**. Do not edit its compact JSON
value manually. One helper stores all section balances.

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
- Optional MeteoFusion HA `0.7.0` or newer for native 24-hour rain, ETo and forecast-quality data.
- Optional local weather entity, rain sensor, rain amount sensor, temperature sensor, wind source, UV/sunlight source and soil moisture sensor.
- One recommended `input_text` helper with maximum length `255` for persistent water balance.
- Optional Logbook diagnostics and persistent notifications for user-visible irrigation events.

## Privacy

Do not publish Home Assistant storage files, access tokens, exact home address, raw API responses or screenshots showing private garden details.
