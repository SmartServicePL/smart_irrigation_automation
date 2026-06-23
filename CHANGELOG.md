# Changelog

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
