"""Rain source priority, reason helper, quiet night and lawn mower cooperation (1.12.0).

The tests render the real templates from the blueprint, like test_blueprint_templates.py.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from test_blueprint_templates import (  # noqa: E402
    BLUEPRINT,
    NOW,
    FakeHass,
    _action_variables,
    _load_blueprint,
    _zone_context,
    jinja2,
    yaml,
)

# Input names that existed before 1.12.0. They must never be renamed or removed.
OLD_INPUTS = (
    "forecast_weather_entity current_weather_entity rain_binary_sensor rain_amount_sensor "
    "temperature_source_entity wind_source_entity sunlight_source_entity reference_et_sensor "
    "solar_radiation_mean_sensor soil_moisture_sensor zone_count send_runtime_to_switch "
    "valve_runtime_watchdog schedule_mode sun_event_offset_minutes primary_start_time "
    "backup_start_time enable_backup_time enable_condition_checks condition_check_time_1 "
    "condition_check_time_2 condition_check_time_3 condition_check_time_4 season_start_month "
    "season_end_month min_dose_mm max_dose_mm min_runtime_minutes max_runtime_minutes "
    "zone_pause_seconds max_forecast_rain_mm max_rain_probability_percent rain_credit_percent "
    "min_temperature_c hot_temperature_c max_wind min_battery_percent soil_moisture_block_percent "
    "irrigation_efficiency_percent enable_irrigation_logs create_persistent_notification "
    "next_watering_datetime water_balance_helper"
).split()
ZONE_INPUTS = (
    "valve name soil_type plant_type sprinkler_profile custom_rate_mm_h "
    "runtime_adjustment_percent online_sensor battery_sensor"
).split()
NEW_INPUTS = ("pogoda_opad_24h_wstecz", "cisza_nocna", "pomocnik_powod", "kosiarka")


def _inputs(doc: dict) -> dict:
    result = {}
    for section in doc["blueprint"]["input"].values():
        result.update(section.get("input", {}))
    return result


def _render_at(hass: FakeHass, template: str, context: dict, when: datetime | None = None) -> str:
    env = hass.env()
    if when is not None:
        env.globals["now"] = lambda: when
    return env.from_string(template).render(**context).strip()


def _render_chain(hass: FakeHass, variables: dict, names: list[str], context: dict, when=None) -> dict:
    """Render variables one after another, like a Home Assistant ``variables`` action."""
    context = dict(context)
    for name in names:
        context[name] = _render_at(hass, variables[name], context, when)
    return context


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class InputStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.inputs = _inputs(cls.doc)

    def test_no_existing_input_was_removed_or_renamed(self) -> None:
        for name in OLD_INPUTS:
            self.assertIn(name, self.inputs, name)
        for zone in range(1, 13):
            for suffix in ZONE_INPUTS:
                self.assertIn(f"zone_{zone}_{suffix}", self.inputs)

    def test_new_inputs_exist_and_are_optional_with_empty_default(self) -> None:
        for name in NEW_INPUTS:
            self.assertIn(name, self.inputs, name)
            self.assertEqual(self.inputs[name]["default"], "", name)

    def test_new_input_selectors(self) -> None:
        def domains(name: str) -> list[str]:
            return [item["domain"] for item in self.inputs[name]["selector"]["entity"]["filter"]]

        self.assertEqual(domains("pogoda_opad_24h_wstecz"), ["sensor"])
        self.assertEqual(domains("cisza_nocna"), ["input_boolean"])
        self.assertEqual(domains("pomocnik_powod"), ["input_text"])
        self.assertEqual(domains("kosiarka"), ["lawn_mower"])

    def test_existing_rain_input_keeps_its_selector_and_default(self) -> None:
        self.assertEqual(self.inputs["rain_amount_sensor"]["default"], "")
        self.assertEqual(
            self.inputs["rain_amount_sensor"]["selector"]["entity"]["filter"], [{"domain": "sensor"}]
        )

    def test_every_new_input_is_read_into_a_variable(self) -> None:
        variables = self.doc["variables"]
        for name in NEW_INPUTS:
            self.assertEqual(variables[name], f"INPUT:{name}")
        self.assertEqual(variables["rain_amount_sensor_fallback"], "INPUT:rain_amount_sensor")

    def test_version_is_1_12_1_in_all_files(self) -> None:
        for suffix in ("", "_en", "_de"):
            text = BLUEPRINT.with_name(f"smart_irrigation{suffix}.yaml").read_text(encoding="utf-8")
            self.assertRegex(text, r"(Wersja|Version) 1\.12\.1\.")


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class RainSourcePriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.variables = cls.doc["variables"]

    def _source(self, states: dict, main: str = "sensor.main", own: str = "sensor.own") -> tuple[str, str]:
        hass = FakeHass(states)
        context = dict(pogoda_opad_24h_wstecz=main, rain_amount_sensor_fallback=own)
        context = _render_chain(hass, self.variables, ["rain_source_mode", "rain_amount_sensor"], context)
        return context["rain_source_mode"], context["rain_amount_sensor"]

    def test_main_source_has_priority_over_the_own_sensor(self) -> None:
        self.assertEqual(self._source({"sensor.main": "2.5", "sensor.own": "9"}), ("glowne", "sensor.main"))

    def test_zero_from_the_main_source_is_a_valid_reading(self) -> None:
        self.assertEqual(self._source({"sensor.main": "0", "sensor.own": "9"}), ("glowne", "sensor.main"))

    def test_unavailable_main_source_falls_back_to_the_own_sensor(self) -> None:
        for bad in ("unavailable", "unknown", "", "abc"):
            self.assertEqual(
                self._source({"sensor.main": bad, "sensor.own": "3"}), ("rezerwa", "sensor.own"), bad
            )

    def test_missing_main_entity_falls_back_too(self) -> None:
        self.assertEqual(self._source({"sensor.own": "3"}), ("rezerwa", "sensor.own"))

    def test_both_unavailable_means_unknown(self) -> None:
        mode, entity = self._source({"sensor.main": "unavailable", "sensor.own": "unavailable"})
        self.assertEqual(mode, "nieznane")
        self.assertEqual(entity, "sensor.main")

    def test_main_unavailable_and_no_own_sensor_means_unknown(self) -> None:
        self.assertEqual(self._source({"sensor.main": "unavailable"}, own="")[0], "nieznane")

    def test_without_main_input_the_own_sensor_works_exactly_as_before(self) -> None:
        self.assertEqual(self._source({"sensor.own": "3"}, main=""), ("wlasny", "sensor.own"))
        # Unavailable own sensor: still the own sensor (warning, balance keeps the old total).
        self.assertEqual(self._source({"sensor.own": "unavailable"}, main=""), ("wlasny", "sensor.own"))

    def test_without_any_rain_sensor_the_forecast_estimate_is_used(self) -> None:
        self.assertEqual(self._source({}, main="", own=""), ("prognoza", ""))


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class SourceSwitchBalanceTests(unittest.TestCase):
    """Switching between sources must not be booked as new rain."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.balance = _action_variables(cls.doc, "Zaktualizuj trwały bilans wody")

    def _increment(self, saved: dict, mode: str, current: float) -> float:
        hass = FakeHass()
        context = dict(
            rain_source_mode=mode,
            water_balance_saved=saved,
            water_balance_saved_valid=True,
            water_balance_rain_from_forecast=False,
            water_balance_rain_source_ok=True,
            water_balance_rain_total_mm=current,
        )
        context = _render_chain(hass, self.balance, ["water_balance_source_tag"], context)
        return float(_render_at(hass, self.balance["water_balance_rain_increment_mm"], context))

    def test_same_main_source_counts_new_rain(self) -> None:
        saved = {"v": 1, "t": NOW, "r": 2.0, "s": 1, "z": [0] * 12}
        self.assertEqual(self._increment(saved, "glowne", 5.0), 3.0)

    def test_legacy_payload_without_tag_is_the_own_sensor(self) -> None:
        saved = {"v": 1, "t": NOW, "r": 2.0, "z": [0] * 12}
        self.assertEqual(self._increment(saved, "wlasny", 5.0), 3.0)
        self.assertEqual(self._increment(saved, "rezerwa", 5.0), 3.0)

    def test_switch_from_own_to_main_books_no_rain(self) -> None:
        saved = {"v": 1, "t": NOW, "r": 2.0, "z": [0] * 12}
        self.assertEqual(self._increment(saved, "glowne", 9.0), 0)

    def test_switch_from_main_to_fallback_books_no_rain(self) -> None:
        saved = {"v": 1, "t": NOW, "r": 9.0, "s": 1, "z": [0] * 12}
        self.assertEqual(self._increment(saved, "rezerwa", 11.0), 0)

    def test_unknown_rain_keeps_the_stored_tag(self) -> None:
        for tag in (0, 1):
            saved = {"v": 1, "t": NOW, "r": 9.0, "z": [0] * 12}
            if tag:
                saved["s"] = 1
            context = dict(
                rain_source_mode="nieznane", water_balance_saved=saved, water_balance_saved_valid=True
            )
            rendered = _render_at(FakeHass(), self.balance["water_balance_source_tag"], context)
            self.assertEqual(rendered, str(tag))

    def test_payload_carries_the_tag_only_for_the_main_source_and_fits_the_helper(self) -> None:
        hass = FakeHass()
        context = _zone_context()
        context.update(
            water_balance_rain_from_forecast=False,
            water_balance_rain_total_mm=9999.9,
            water_balance_deficits_json=json.dumps([999.9] * 12),
        )
        main = _render_at(hass, self.balance["water_balance_payload"], dict(context, water_balance_source_tag="1"))
        own = _render_at(hass, self.balance["water_balance_payload"], dict(context, water_balance_source_tag="0"))
        self.assertEqual(json.loads(main)["s"], 1)
        self.assertNotIn("s", json.loads(own))
        self.assertLessEqual(len(main), 255)


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class ReasonHelperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.step = _action_variables(cls.doc, "Wylicz tekst powodu decyzji")
        cls.names = ["decision_when_ts", "decision_when", "decision_source_note", "decision_base", "decision_text"]

    def _text(self, **overrides) -> str:
        context = dict(
            irrigation_skip_reason="",
            irrigation_cycle_needed=True,
            irrigation_start_trigger_ok=False,
            irrigation_cycle_depth_mm=6.04,
            next_watering_estimated_timestamp=int(NOW) + 86400,
            next_watering_blocked_timestamp=int(NOW) + 86400,
            rain_source_mode="glowne",
        )
        context.update(overrides)
        return _render_chain(FakeHass(), self.step, self.names, context)["decision_text"]

    def test_planned_watering_names_the_day_and_time(self) -> None:
        text = self._text()
        self.assertRegex(text, r"^Podlewam jutro o \d{1,2}:\d{2} - gleba potrzebuje wody \(dawka do 6\.0 mm\)$")

    def test_running_cycle(self) -> None:
        self.assertEqual(
            self._text(irrigation_start_trigger_ok=True),
            "Podlewam teraz - gleba potrzebuje wody (dawka do 6.0 mm)",
        )

    def test_no_need(self) -> None:
        self.assertRegex(
            self._text(irrigation_cycle_needed=False),
            r"^Nie podlewam - trawnik nie wymaga jeszcze podlewania, następny termin jutro o \d{1,2}:\d{2}$",
        )

    def test_skip_reason_is_shortened_to_its_first_sentence(self) -> None:
        text = self._text(irrigation_skip_reason="Wiatr jest za mocny: 40, limit to 35. Dalsze zdanie.")
        self.assertTrue(text.startswith("Nie podlewam - Wiatr jest za mocny: 40, limit to 35, następny termin"), text)
        self.assertNotIn("Dalsze", text)

    def test_fallback_and_unknown_are_always_marked(self) -> None:
        self.assertTrue(self._text(rain_source_mode="rezerwa").endswith("(pogoda zapasowa: opad z rezerwowego czujnika)"))
        self.assertTrue(self._text(rain_source_mode="nieznane").endswith("(pogoda nieznana: brak odczytu opadu)"))
        for mode in ("glowne", "wlasny", "prognoza"):
            self.assertNotIn("pogoda", self._text(rain_source_mode=mode))

    def test_text_never_exceeds_the_helper_limit_and_keeps_the_note(self) -> None:
        long_reason = "Bardzo długi powód " + "x" * 600
        for mode, note in (("rezerwa", "rezerwowego czujnika)"), ("nieznane", "odczytu opadu)")):
            text = self._text(irrigation_skip_reason=long_reason, rain_source_mode=mode)
            self.assertLessEqual(len(text), 255)
            self.assertTrue(text.endswith(note), text)

    def test_blueprint_writes_only_when_the_text_changed_and_the_helper_exists(self) -> None:
        action = next(a for a in self.doc["actions"] if a.get("alias") == "Zapisz powód decyzji w pomocniku")
        condition = action["choose"][0]["conditions"][0]["value_template"]
        self.assertIn("states[pomocnik_powod] is not none", condition)
        self.assertIn("states(pomocnik_powod) != decision_text", condition)
        step = action["choose"][0]["sequence"][0]
        self.assertEqual(step["action"], "input_text.set_value")
        self.assertTrue(step["continue_on_error"])

    def test_reason_step_runs_before_every_early_stop_of_the_decision(self) -> None:
        aliases = [a.get("alias") for a in self.doc["actions"]]
        compute = aliases.index("Wylicz tekst powodu decyzji")
        reason = aliases.index("Zapisz powód decyzji w pomocniku")
        self.assertEqual(reason, compute + 1)
        self.assertLess(reason, aliases.index("Zapisz termin kolejnego sprawdzenia przy blokadzie"))
        self.assertLess(reason, aliases.index("Zatrzymaj gdy podlewanie pominięte"))
        self.assertLess(reason, aliases.index("Zatrzymaj gdy cykl podlewania nie jest potrzebny"))
        self.assertLess(aliases.index("Wylicz powód pominięcia podlewania"), reason)


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class QuietNightAndMowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.reason = _action_variables(cls.doc, "Wylicz powód pominięcia podlewania")

    def _blocks(self, name: str, states: dict, hour: int, **context) -> bool:
        when = datetime(2026, 7, 1, hour, 30)
        base = dict(irrigation_start_trigger_ok=True, cisza_nocna="", kosiarka="")
        base.update(context)
        return _render_at(FakeHass(states), self.reason[name], base, when) == "True"

    def test_start_before_sunrise_does_not_wait_for_the_end_of_quiet_night(self) -> None:
        states = {"input_boolean.cisza": "on", "sun.sun": "below_horizon"}
        self.assertFalse(self._blocks("quiet_night_blocks", states, 4, cisza_nocna="input_boolean.cisza"))

    def test_other_starts_wait_while_quiet_night_is_on(self) -> None:
        states = {"input_boolean.cisza": "on", "sun.sun": "below_horizon"}
        self.assertTrue(self._blocks("quiet_night_blocks", states, 22, cisza_nocna="input_boolean.cisza"))
        states["sun.sun"] = "above_horizon"
        self.assertTrue(self._blocks("quiet_night_blocks", states, 7, cisza_nocna="input_boolean.cisza"))

    def test_quiet_night_off_or_missing_never_blocks(self) -> None:
        states = {"input_boolean.cisza": "off", "sun.sun": "above_horizon"}
        self.assertFalse(self._blocks("quiet_night_blocks", states, 22, cisza_nocna="input_boolean.cisza"))
        self.assertFalse(self._blocks("quiet_night_blocks", {"sun.sun": "above_horizon"}, 22))

    def test_condition_checks_are_not_blocked_by_quiet_night_or_mower(self) -> None:
        states = {"input_boolean.cisza": "on", "lawn_mower.m": "mowing", "sun.sun": "above_horizon"}
        for name in ("quiet_night_blocks", "mower_blocks"):
            self.assertFalse(
                self._blocks(name, states, 22, irrigation_start_trigger_ok=False,
                             cisza_nocna="input_boolean.cisza", kosiarka="lawn_mower.m"),
                name,
            )

    def test_mower_blocks_only_while_mowing(self) -> None:
        for state, expected in (("mowing", True), ("docked", False), ("paused", False), ("error", False)):
            self.assertEqual(
                self._blocks("mower_blocks", {"lawn_mower.m": state}, 5, kosiarka="lawn_mower.m"), expected, state
            )
        self.assertFalse(self._blocks("mower_blocks", {"lawn_mower.m": "mowing"}, 5))

    def test_blocks_appear_as_skip_reasons_last_in_the_weather_chain(self) -> None:
        text = self.reason["irrigation_weather_block_reason"]
        self.assertLess(text.index("wind_ok"), text.index("quiet_night_blocks"))
        self.assertLess(text.index("quiet_night_blocks"), text.index("mower_blocks"))

    def test_sections_wait_while_the_mower_mows(self) -> None:
        text = BLUEPRINT.read_text(encoding="utf-8")
        ready = text.index("section_ready: >-")
        block = text[ready : ready + 900]
        self.assertIn("is_state(kosiarka, 'mowing')", block)
        self.assertIn("section_skip_reason", text[ready:])


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class ActionStructureTests(unittest.TestCase):
    def test_a_variables_action_has_no_other_action_type(self) -> None:
        # Home Assistant rejects a step that mixes "variables" with another action type.
        doc = _load_blueprint()

        def walk(node):
            if isinstance(node, dict):
                if "variables" in node and "alias" in node:
                    extra = set(node) - {"alias", "variables", "enabled", "continue_on_error"}
                    self.assertFalse(extra, f"{node['alias']}: {sorted(extra)}")
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(doc["actions"])


class ValveSafetyRequirementTests(unittest.TestCase):
    """Requirement 6.3 ("Bezpieczne zawory") is covered by the existing safety sequence."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = BLUEPRINT.read_text(encoding="utf-8")

    def test_ha_start_and_periodic_watchdog_close_open_valves_with_a_notification(self) -> None:
        self.assertIn("id: ha_start", self.text)
        self.assertIn("id: valve_watchdog", self.text)
        # The watchdog limit (maximum section runtime + 5 minutes) is stricter than "+ 10 minutes".
        self.assertIn("(trigger_max_runtime_minutes | int(45)) + 5) * 60", self.text)
        alarm = self.text.index("alias: Powiadom o zamknięciu sekcji")
        self.assertIn("persistent_notification.create", self.text[alarm : alarm + 400])
        self.assertTrue(re.search(r"valve_runtime_watchdog:\n(?:.*\n)*?\s+default: true", self.text))

    def test_emergency_close_is_written_to_the_reason_helper(self) -> None:
        alarm = self.text.index("alias: Powiadom o zamknięciu sekcji")
        end = self.text.index("alias: Zaloguj kontrolę zaworów")
        self.assertIn("input_text.set_value", self.text[alarm:end])
        self.assertIn("pomocnik_powod", self.text[alarm:end])


if __name__ == "__main__":
    unittest.main()
