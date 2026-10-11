# Smart irrigation setup

[![Open your Home Assistant instance and import this blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSmartServicePL%2Fsmart_irrigation_automation%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fsmart_irrigation_automation%2Fsmart_irrigation.yaml)

`blueprints/automation/smart_irrigation_automation/smart_irrigation.yaml` adds intelligent Home Assistant irrigation for 1 to 12 garden sections.

Translated UI guides are available in [docs/i18n](i18n/README.md) for English,
German, Spanish, French, Italian, Dutch and Portuguese.

## How it works

The automation starts watering from a fixed time, sunrise or sunset with configurable offset. Before watering it checks season, current weather, rain forecast, physical rain sensor, temperature, wind and optional soil moisture. If the weather entity or forecast is `unknown`/`unavailable`, watering is skipped with a clear reason instead of running without reliable weather data.

It can also run condition-only checks, by default at 12:00, 18:00, 00:00 and 03:00. These checks fetch weather and recalculate watering need, update the next-watering helper, then stop before any section can start. Weather blocks and low demand discovered by these checks remain silent in Home Assistant notifications.

For every active section it calculates a water dose and runtime from:

- plant type: grass, flowers, vegetables or shrubs,
- soil type, selected with simplified garden names,
- sprinkler profile: detailed Rain Bird profiles, Hunter profiles or custom mm/h,
- newly measured rain (forecast rain only delays the start and is never counted as water received),
- daily reference evapotranspiration (ETo), or a fallback estimate from temperature, sunlight/UV and wind,
- optional soil moisture,
- irrigation efficiency and per-section runtime correction.

## Persistent Water-Balance Model

The blueprint uses a checkbook water-balance model. Daily plant water use is estimated as `ETc = ETo * Kc`. Newly measured effective rain and confirmed irrigation reduce the stored deficit. Soil type defines available water capacity, plant type defines root depth and allowed depletion, and watering starts when the modeled deficit reaches that section threshold. This is intentionally simpler than full FAO Penman-Monteith, but follows the same scheduling idea and works with normal Home Assistant weather data.

Create one Home Assistant `input_text` helper, set its maximum length to `255`
and select it as **Helper - trwały bilans wody**. It stores compact JSON for all
sections. Do not edit its state manually. The first automation run initializes
the balances at zero; later checks add elapsed ETo and subtract only new rain.
This makes a rolling rain value safe: when an old storm leaves the 24-hour
window, the saved soil-water credit remains in the balance.

Forecast precipitation only delays a start. It is not subtracted from the
balance until measured locally or reported as measured rain by MeteoFusion.
Existing automations without the helper keep a compatibility calculation, but
they cannot remember rain beyond the sensor's own history window.

If you already have a reliable daily ETo/evapotranspiration sensor in millimeters, select it in **Dzienne ET0 / ewapotranspiracja**. Without that sensor, the blueprint first uses MeteoFusion ETo when available; for other weather entities it estimates ETo from garden temperature, UV/sunlight and wind. A measured-rain override should preferably be a rolling 24-hour or current rain-event total. A sensor that resets at midnight represents only part of the water received since the previous irrigation.

## MeteoFusion HA

Select the MeteoFusion weather entity in **Encja pogody do prognozy**, then
enable **Korzystaj z danych MeteoFusion HA**. The blueprint validates the stable
`smart_service.weather.v1` contract and uses the rolling 24-hour rain forecast,
local rain rate and rain total, current station conditions, daily FAO-56 ETo and
forecast-quality diagnostics.

Manual sensor selections remain overrides. For example, a dedicated garden
rain gauge can supply the measured rain amount while MeteoFusion supplies ETo
and the next-24-hour forecast. If no ETo sensor is selected, MeteoFusion ETo is
used before the blueprint's fallback estimate. All manual weather sensors are
placed in the collapsed **Opcjonalne sensory lokalne i nadpisania** section, so
a MeteoFusion-only user can leave the whole section untouched.

**MeteoFusion - minimalna pewność prognozy** defines the minimum accepted
forecast confidence. Irrigation is also skipped when the MeteoFusion station
data is stale, no forecast source is available or the weather contract is
unavailable. The notification shows the source, confidence, status and ETo used
for the decision.

Rain in a daily forecast no longer blocks irrigation by its condition name
alone. Normal rain is evaluated with the configured precipitation amount and
probability limits. Forecast heavy rain, lightning, hail and snow remain unconditional
safety blocks, and current rain from MeteoFusion interrupts an active section.

Available soil choices are intentionally written for normal garden use:

- **Piaszczysta / bardzo lekka** - water drains quickly; irrigation may be needed sooner.
- **Lekka ogrodowa** - fairly permeable garden soil.
- **Zwykła ziemia ogrodowa** - default choice for most gardens.
- **Humusowa / próchniczna** - fertile topsoil or compost-rich purchased garden soil.
- **Czarnoziem / czarna ziemia** - dark fertile soil that usually stores water well.
- **Gliniasta / ciężka** - heavier soil that keeps water longer.
- **Bardzo ciężka / zbita glina** - very compact clay; water enters slowly and runoff risk is higher.

Model references:

- [FAO-56 Crop evapotranspiration](https://www.fao.org/4/x0490e/x0490e00.htm)
- [FAO-56 root-zone soil-water balance and irrigation timing](https://www.fao.org/4/X0490E/x0490e0e.htm)
- [University of Minnesota Extension: ET-based water balance method](https://extension.umn.edu/irrigation/evapotranspiration-based-irrigation-scheduling-or-water-balance-method)
- [US EPA WaterSense: soil-moisture-based irrigation controllers](https://www.epa.gov/watersense/soil-moisture-based-irrigation-controllers)
- [Rain Bird: Cycle+Soak for RC2 and other connected controllers](https://wifi.rainbird.com/articles/understanding-cycle-and-soak-and-your-rain-bird-smart-wifi-controller/)
- [Colorado State University Extension: water balance approach](https://extension.colostate.edu/resource/irrigation-scheduling-the-water-balance-approach/)
- [Oregon State University Extension: irrigation water scheduling](https://extension.oregonstate.edu/catalog/em-9717-irrigation-water-scheduling)
- [UC ANR: plant factor and crop coefficient](https://ucanr.edu/site/center-landscape-urban-horticulture/plant-factor-or-crop-coefficient-whats-difference)

Rain Bird profiles include 5000/3500 rotors, 1800 sprays, R-VAN rotary nozzles and XF dripline, plus generic Rain Bird rotors, sprays and dripline for mixed or unknown installations.

For native Rain Bird RC2 entities, the blueprint automatically calls `rainbird_rc2.start_zone` with the calculated runtime in minutes. The **Przekazuj wyliczony czas do sterownika Rain Bird** option is retained for older Rain Bird entities that support `rainbird.start_irrigation`. It does not affect ordinary switch or valve entities.

One automation may combine different controllers. A typical mixed installation can use Rain Bird RC2 for sections 1-8 and Sonoff, Shelly or ESPHome relays for drip lines in sections 9-12. Ordinary `switch` entities are turned on, monitored for start confirmation, kept active for the calculated runtime and turned off. Ordinary `valve` entities are opened and closed in the same controlled sequence. Sections always run one at a time.

After sending a start command, the blueprint waits up to 60 seconds for an `on/open` (or `opening`) state confirmation. The start notification is not created until that confirmation arrives. If the controller does not confirm the start, a close command is sent anyway and the cycle ends with a final report that names the section. If the controller closes the section too early, the run is stopped and the final Logbook/persistent notification clearly reports what actually happened.

Every close command is confirmed: the blueprint waits for `off/closed`, repeats the command up to 3 times every 30 seconds and, if the section still reports open, creates a separate alarm notification (`smart_irrigation_valve_alarm`) and stops the cycle.

## Valve safety

- After a Home Assistant start the blueprint waits up to 3 minutes for its `switch`/`valve` sections to become available and closes every section that is on or open. The same check runs after this automation is saved or reloaded.
- **Nadzór czasu pracy sekcji** (on by default) closes a `switch`/`valve` section that stays on longer than the maximum section runtime plus 5 minutes, regardless of who turned it on. Disable it only if you deliberately water manually for longer than that limit.
- Rain Bird RC2 and Rain Bird sections are excluded from both checks, because the controller receives the runtime and stops the station itself.
- Home Assistant can only close a valve while it runs. For relays such as Sonoff, Shelly or ESPHome also set a hardware limit in the device: Shelly **Auto OFF**, Sonoff **Inching**, or an ESPHome `on_turn_on` action with a `delay` followed by `switch.turn_off`.

If rain starts while a section is running, the weather changes to a blocking condition, or weather data stays unavailable for more than 5 minutes, the automation closes the valve, reports the interruption reason and stops the remaining sections.

## Logs and notifications

At the bottom of the blueprint you can enable **Włącz logbook.log**. When enabled, Home Assistant Logbook receives entries for:

- global watering skip reasons,
- start of the watering check,
- section start with calculated runtime and water dose,
- section end,
- skipped section with reason,
- interruption by rain or bad weather.

You can also enable **Twórz powiadomienie persistent_notification**. There is one daily execution decision. If watering starts, the notification appears only after the first section confirms opening and is then replaced by the final result with per-section time and estimated applied depth. If watering does not start, one skipped result explains why. Condition-only checks never create notifications. A safety interruption becomes the final completed-before-time result instead of an extra intermediate message.

## Helpers

Optionally create an `input_datetime` helper with date and time, then select it in **Helper - następne podlewanie**. The automation updates it after each check. If watering is blocked by season or weather, it stores the next scheduled check. If watering is not needed yet, it stores the first scheduled cycle after the calculated water need reaches the start threshold.

For the persistent calculation, create a Text helper with maximum length `255`
and select it in **Helper - trwały bilans wody**. Only one helper is required for
all configured sections. The helper is required when any section is an ordinary
`switch`/`valve`. If the helper is missing or its maximum length is too short for
the stored balance, watering stops with a reason that names the helper.

Without a rain amount sensor and without MeteoFusion HA, measured rain does not
reduce the balance; notifications show a warning in that case. When the selected
rain sensor is temporarily unavailable, the balance keeps the last stored rain
total and does not credit any new rain until the sensor returns.

## Recommended setup

Use one automation instance for one hydraulic system or watering area. It may contain more than one controller type. Set **Liczba sekcji** to the real number of sections, up to 12. Fill only those sections; later sections may stay with defaults.

For MeteoFusion HA, select its weather entity, enable **Korzystaj z danych
MeteoFusion HA** and normally leave the complete optional sensor section empty.
Select separate garden sensors only when they should override MeteoFusion for
that measurement.

Good starting values:

- Start mode: sunrise.
- Sun offset: `-30` minutes.
- Season: `4-10`.
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
