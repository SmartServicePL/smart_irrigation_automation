# Smart irrigation setup

[![Open your Home Assistant instance and import this blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml)

`blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml` adds intelligent Home Assistant irrigation for 1 to 8 garden sections.

Translated UI guides are available in [docs/i18n](i18n/README.md) for English,
German, Spanish, French, Italian, Dutch and Portuguese.

## How it works

The automation starts watering from a fixed time, sunrise or sunset with configurable offset. Before watering it checks season, current weather, rain forecast, physical rain sensor, temperature, wind and optional soil moisture. If the weather entity or forecast is `unknown`/`unavailable`, watering is skipped with a clear reason instead of running without reliable weather data.

It can also run condition-only checks, by default at 12:00, 18:00, 00:00 and 03:00. These checks fetch weather and recalculate watering need, update the next-watering helper, then stop before any section can start. They do not create Home Assistant notifications.

For every active section it calculates a water dose and runtime from:

- plant type: grass, flowers, vegetables or shrubs,
- soil type, selected with simplified garden names,
- sprinkler profile: detailed Rain Bird profiles, Hunter profiles or custom mm/h,
- recent/forecast rain,
- daily reference evapotranspiration (ETo), or a fallback estimate from temperature, sunlight/UV and wind,
- optional soil moisture,
- irrigation efficiency and per-section runtime correction.

## Water-Balance Model

The blueprint uses a simplified checkbook water-balance model. Daily plant water use is estimated as `ETc = ETo * Kc`. Rain reduces the modeled deficit. Soil type defines available water capacity, plant type defines root depth and allowed depletion, and watering starts when the modeled deficit reaches that section threshold. This is intentionally simpler than full FAO Penman-Monteith, but follows the same scheduling idea and works with normal Home Assistant weather data.

If you already have a reliable daily ETo/evapotranspiration sensor in millimeters, select it in **Dzienne ET0 / ewapotranspiracja**. Without that sensor, the blueprint estimates ETo from garden temperature, UV/sunlight and wind.

Available soil choices are intentionally written for normal garden use:

- **Piaszczysta / bardzo lekka** - water drains quickly; irrigation may be needed sooner.
- **Lekka ogrodowa** - fairly permeable garden soil.
- **Zwykla ziemia ogrodowa** - default choice for most gardens.
- **Humusowa / prochniczna** - fertile topsoil or compost-rich purchased garden soil.
- **Czarnoziem / czarna ziemia** - dark fertile soil that usually stores water well.
- **Gliniasta / ciezka** - heavier soil that keeps water longer.
- **Bardzo ciezka / zbita glina** - very compact clay; water enters slowly and runoff risk is higher.

Model references:

- [FAO-56 Crop evapotranspiration](https://www.fao.org/4/x0490e/x0490e00.htm)
- [University of Minnesota Extension: ET-based water balance method](https://extension.umn.edu/irrigation/evapotranspiration-based-irrigation-scheduling-or-water-balance-method)
- [Colorado State University Extension: water balance approach](https://extension.colostate.edu/resource/irrigation-scheduling-the-water-balance-approach/)
- [Oregon State University Extension: irrigation water scheduling](https://extension.oregonstate.edu/catalog/em-9717-irrigation-water-scheduling)
- [UC ANR: plant factor and crop coefficient](https://ucanr.edu/site/center-landscape-urban-horticulture/plant-factor-or-crop-coefficient-whats-difference)

Rain Bird profiles include 5000/3500 rotors, 1800 sprays, R-VAN rotary nozzles and XF dripline, plus generic Rain Bird rotors, sprays and dripline for mixed or unknown installations.

Enable **Uzywaj czasu sekcji w sterowniku Rain Bird** when sections are native Rain Bird RC2/ESP `switch` entities. The blueprint detects native Rain Bird entities and calls `rainbird.start_irrigation` with the calculated runtime in minutes. Other switch integrations always use standard `switch.turn_on`.

After sending a start command, the blueprint waits for an `on/open` state confirmation. If the controller does not confirm the start or closes the section too early, the run is stopped and the Logbook/persistent notification clearly reports that watering did not occur as planned.

If rain starts while a section is running, the weather changes to a blocking condition, or weather data becomes unavailable, the automation closes the valve, reports the interruption reason and stops the remaining sections.

## Logs and notifications

At the bottom of the blueprint you can enable **Wlacz logbook.log**. When enabled, Home Assistant Logbook receives entries for:

- global watering skip reasons,
- start of the watering check,
- section start with calculated runtime and water dose,
- section end,
- skipped section with reason,
- interruption by rain or bad weather.

You can also enable **Tworz powiadomienie persistent_notification**. Notifications are created only for user-visible events: watering start, watering end with per-section times, skipped watering with a clear reason, or interrupted watering with a short reason.

## Next watering helper

Optionally create an `input_datetime` helper with date and time, then select it in **Helper - nastepne podlewanie**. The automation updates it after each check. If watering is blocked by season or weather, it stores the next scheduled check. If watering is not needed yet, it stores the first scheduled cycle after the calculated water need reaches the start threshold.

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
