# Changelog

## Unreleased

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
