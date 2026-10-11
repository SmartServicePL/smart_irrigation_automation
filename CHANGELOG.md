# Changelog

## 1.7.0

Water balance:

- With the **Helper - trwały bilans wody** selected, one measured rain source is required: **Opad zmierzony** or MeteoFusion HA. Without it watering stops with a clear reason (in 1.6.0 this was only a warning), because rain would never reduce the balance.
- After a break in balance updates (Home Assistant down or the automation disabled) evapotranspiration is added for at most 7 days (previously 3). A longer gap is written to the Logbook.
- Outside the season the balance is kept at zero. A new season starts from zero on the first day of the season start month, so the first spring watering is not driven by a deficit accumulated over the winter. The season start is written to the Logbook.
- The **korekta czasu** description explains that the balance subtracts the water actually applied: a shorter run means more frequent watering, a longer run less frequent watering.

Units:

- Temperatures reported in °F (weather entity `temperature_unit` or sensor `unit_of_measurement`) are converted to °C. Previously 30 °F was treated as 30 °C, so the frost block never stopped watering on imperial installations and hot-weather and evapotranspiration estimates were inflated.
- Forecast and current weather precipitation in inches is converted to millimetres, so the forecast rain block works with imperial weather entities (rain amount sensors in inches were already converted).

Texts:

- All Polish names, descriptions, option labels, notifications, Logbook entries and step names now use Polish characters, and several sentences were corrected grammatically. Option values, input keys and identifiers are unchanged, so existing automations need no reconfiguration.
- The Polish label column of the 7 translated UI guides matches the new labels.

Behavior change for existing automations: an automation with the balance helper but without a rain amount sensor and without MeteoFusion HA stops watering until a rain source is selected.

## 1.6.0

Valve safety:

- A section whose opening is not confirmed within 60 seconds (previously 20) is now always sent a close command before the cycle stops. The `opening` state is accepted as a started valve, so slow motorized ball valves are no longer left open after a "failed" start.
- Every section close is confirmed: the close command is repeated up to 3 times, 30 seconds apart, until the entity reports `off`/`closed`. A section that still does not confirm creates a separate alarm notification (`smart_irrigation_valve_alarm`, always shown, independent of the notification option) and stops the cycle.
- All open/close commands use `continue_on_error`, so a failed command no longer aborts the run before the valve is closed.
- After a Home Assistant start the automation waits up to 3 minutes for its `switch`/`valve` sections to become available and closes any that are on/open (and sends OFF to sections in the `unknown` state). After this automation itself is saved or reloaded, the same check runs. Rain Bird RC2 and Rain Bird sections are skipped because the controller times the run itself.
- New input **Nadzor czasu pracy sekcji** (enabled by default): a `switch`/`valve` section that stays on longer than the maximum section runtime + 5 minutes is closed, whoever turned it on.
- The automation mode changed from `single` to `queued` (max 10), so a schedule trigger arriving during the restart check is no longer dropped.

Water balance and decisions:

- Fixed the persistent water balance never being read back: Home Assistant converts the stored JSON into a dictionary, which the 1.5.0 template rejected, so every check reset all sections to zero and the decision step could fail.
- Balance values are rounded to 0.1 mm and the stored payload is at most 99 characters, so the default 100-character Text helper is enough. A helper that is missing or too short now stops watering with a clear reason instead of silently ignoring the write.
- Without the balance helper, installations with ordinary `switch`/`valve` sections are now blocked with a clear reason. Their compatibility calculation always returned a zero deficit, so they never watered.
- An unavailable rain amount sensor no longer overwrites the stored rain total with another source; the same rain is no longer credited twice when the sensor returns.
- Notifications and the Logbook warn when no measured rain source is configured, because rain then does not reduce the balance.
- An unavailable temperature sensor falls back to the current weather temperature instead of the forecast daily maximum; without any current temperature watering is stopped. An unavailable wind sensor falls back to the weather entity's wind and blocks when none is available.
- An unavailable rain sensor now reports its own reason instead of a MeteoFusion rain message.
- A brief (under 5 minutes) loss of the weather entity no longer interrupts a running section.
- Weather without a daily forecast stops the run with a reason instead of an unexplained error.
- Minimum dose larger than maximum dose is reported as a configuration error.
- Rain sensor and MeteoFusion rain are checked live before every section.
- Next-watering times for fixed-time schedules stay correct across daylight saving time changes.
- A gap of more than 3 days in balance updates is written to the Logbook.

Reports:

- The final report is built from sections confirmed in this cycle, so `switch`/`valve` sections are reported as watered (previously only Rain Bird RC2 sections were).
- A section that fails to start ends the cycle with the normal final report and a note instead of a lone "skipped" message.

Other:

- Requires Home Assistant 2025.4.0 or newer (variables updated inside the section loop).
- The release workflow only publishes `## x.y.z` headings, tags them as `v<version>` and never moves an existing tag.
- Removed the byte order mark from the blueprint file and synchronized the translated UI guides with the current labels.

Behavior changes for existing automations: watering stops with a reason when the balance helper is missing or too short, or when ordinary relays are used without the helper; open `switch`/`valve` sections are closed after a Home Assistant restart or a save of this automation; sections left on longer than the maximum runtime + 5 minutes are closed unless the new watchdog input is disabled.

## 1.5.0

- Added one optional `input_text` helper for a persistent per-section soil-water balance across Home Assistant restarts.
- Changed the model to accumulate elapsed `ETo * Kc` and subtract only newly measured effective rain on every scheduled or condition-only check.
- Fixed rolling 24-hour rain handling so rain leaving the sensor window does not reappear as a false water deficit.
- Changed forecast rain to a start-delay safety signal only; forecast millimeters are no longer counted as water received.
- Capped effective-rain credit at 100% so the model cannot receive more water than was measured.
- Subtracts estimated net water after every confirmed completed section and partial water after an interrupted section.
- Removed target waterings per week from the blueprint and all irrigation-decision and next-run calculations.
- Separated root-zone depletion threshold from the maximum dose of one watering cycle.
- Recalculates the next-watering helper from persisted post-cycle deficits instead of a fixed weekly interval.
- Preserved a non-persistent compatibility calculation for existing automations that have not selected the new helper yet.
- Expanded regression coverage for rolling rain, one-time rain credit, per-section irrigation credit and forecast isolation.

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
