# Changelog

## Unreleased

## 1.4.0

- Fixed condition-only checks so weather blocks at `12:00`, `18:00`, `00:00` and `03:00` cannot create misleading skipped-watering notifications.
- Limited the execution path to one daily decision; the legacy backup time is now only a missed-primary recovery when the next-watering helper proves the main start was missed.
- Moved the start notification after the first valve/switch confirms `on` or `open`, preventing a planned cycle from being reported as real watering.
- Kept notifications to three user-facing outcomes: confirmed start, final completion (including early safety completion), or one skipped result.
- Changed soil moisture from a demand multiplier to a direct, configurable irrigation override, matching professional soil-moisture controller behavior.
- Recommended rolling 24-hour or rain-event totals for measured precipitation so midnight-reset daily sensors do not hide recent rain.
- Normalized wind inputs from m/s, mph and knots to km/h before applying the configured safety threshold.
- Carried forward the unfilled part of the root-zone target when a controller's confirmed runtime was too short to deliver the requested depth.
- Added estimated net applied depth to section diagnostics and final notifications.
- Corrected forecast-rain threshold equality so the configured blocking amount behaves as described.

## 1.3.0

- Added explicit **Korzystaj z danych MeteoFusion HA** mode with validation of the stable `smart_service.weather.v1` contract.
- Moved manual weather entities and sensors into a separate collapsed optional-overrides section for a cleaner MeteoFusion setup.
- Automatically uses MeteoFusion rolling 24-hour rain, daily FAO-56 ETo, local rain rate/total, current station conditions and forecast-quality data.
- Added a configurable minimum MeteoFusion confidence threshold and stale-station safety check.
- Preserved manually selected weather sensors as higher-priority overrides.
- Changed ordinary forecast rain to use configured amount/probability thresholds instead of blocking solely on the `rainy` condition; heavy rain, lightning, hail and snow remain unconditional forecast blocks.
- Added live MeteoFusion rain/lightning interruption checks while a section is running.
- Added MeteoFusion source, confidence, status and ETo details to irrigation notifications.
- Aligned forecast-rain threshold comparisons with the displayed 0.1 mm precision so invisible hundredths do not cause confusing skips.
- Expanded the blueprint from 8 to 12 irrigation sections.
- Added complete inputs, water-balance calculations, runtime execution, diagnostics and final reporting for sections 9-12.
- Documented mixed-controller installations, such as Rain Bird RC2 sections combined with Sonoff, Shelly or ESPHome relays for additional drip lines.
- Clarified that Rain Bird RC2 uses `rainbird_rc2.start_zone`, ordinary switches use timed ON/OFF control and ordinary valves use timed open/close control.
- Reformatted Home Assistant persistent notifications as Markdown-style blocks instead of one long sentence.
- Added structured notification sections for status, reason, weather, next watering time and final section summary.
- Changed the final cycle notification to use a compact section table with watered/skipped results.

## 1.2.0

- Simplified per-section soil choices with garden-friendly names so users do not need to know technical soil classifications.
- Added **Humusowa / prochniczna** and **Czarnoziem / czarna ziemia** soil options for common purchased garden soils.
- Mapped the new soil options into the water-balance model:
  - humus-rich soil stores more water than standard garden soil,
  - black soil/chernozem stores the most water from the simplified garden-soil list,
  - existing technical soil values remain compatible with older automations.
- Added translated UI guides for English, German, Spanish, French, Italian, Dutch and Portuguese.
- Added README and setup-documentation links to the translation glossary.

## 1.1.0

- Reworked irrigation need calculation to a simplified ET water-balance model:
  - estimates daily crop water use as `ETc = ETo * Kc`,
  - supports an optional daily ETo/evapotranspiration sensor in millimeters,
  - falls back to an ETo estimate from temperature, UV/sunlight and wind when no ETo sensor is configured,
  - uses plant type for crop coefficient, rooting depth and allowed depletion,
  - uses soil type for available water capacity instead of multiplying water demand by soil type,
  - starts watering when modeled root-zone depletion reaches the section threshold.
- Added the optional **Helper - nastepne podlewanie** `input_datetime` input.
- Added automatic next-watering helper updates after every scheduled or condition-only check.
- Added condition-only checks at `12:00`, `18:00`, `00:00` and `03:00`.
- Condition-only checks recalculate weather and watering need, update the helper and optional Logbook entries, but never start irrigation sections and never create Home Assistant notifications.
- Cleaned Home Assistant persistent notifications:
  - start notification only when watering begins,
  - final notification with watered/skipped section count and per-section times,
  - skip notification only when watering is skipped with a user-readable reason,
  - interruption notification only when watering is stopped early or blocked during a section.
- Removed noisy per-section persistent notifications for section start, section end and section skip.
- Improved skip wording so low water need is explained as a normal user-facing reason instead of raw debug values.
- Updated README and setup documentation with the ET/Kc water-balance model, notification behavior and references.

## 1.0.0

- Initial release.
- Added intelligent irrigation blueprint for 1 to 8 sections.
- Added shared weather and sensor inputs.
- Added per-section soil, plant and Rain Bird/Hunter sprinkler settings.
- Added fixed time, sunrise and sunset schedule modes.
- Added optional Logbook and persistent notification logging for watering, skipped sections and skip reasons.
- Translated weather condition names in Logbook and persistent notifications.
- Added detailed final persistent notification with watered/skipped section summary.
- Added detailed Rain Bird sprinkler profiles and safer interruption handling.
- Added weather-data safety check for unknown/unavailable weather states.
- Added per-run duration control through `rainbird.start_irrigation` for native Rain Bird RC2/ESP switch entities.
- Added start-state confirmation and early-stop detection so notifications never report an unconfirmed watering cycle as completed.
- Added My Home Assistant import button.
- Added setup documentation and donate button.
