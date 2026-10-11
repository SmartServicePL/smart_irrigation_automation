"""Render selected blueprint templates with a small Home Assistant-like Jinja environment.

These tests exercise the real template text from the blueprint (not Python copies of
the formulas). They need ``jinja2`` and ``PyYAML``; without them the module is skipped.
"""

from __future__ import annotations

import json
import math
import re
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import jinja2
    import yaml
except ImportError:  # pragma: no cover - optional test dependencies
    jinja2 = None
    yaml = None


BLUEPRINT = (
    Path(__file__).parents[1]
    / "blueprints"
    / "automation"
    / "smart_irrigation_automation"
    / "smart_irrigation.yaml"
)
NOW = time.time()


def _load_blueprint() -> dict:
    class Loader(yaml.SafeLoader):
        pass

    Loader.add_constructor("!input", lambda loader, node: "INPUT:" + loader.construct_scalar(node))
    return yaml.load(BLUEPRINT.read_text(encoding="utf-8"), Loader=Loader)


def _float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _is_number(value) -> bool:
    if value is None or isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _bool(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "on")
    return bool(value)


def _from_json(value, default=None):
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def _as_timestamp(value, default=None):
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).timestamp()
        except ValueError:
            pass
    return _float(value, default)


def _timestamp_custom(value, fmt, local=True):
    zone = None if local else timezone.utc
    return datetime.fromtimestamp(float(value), zone).strftime(fmt)


def _round(value, precision=0, method="common"):
    value = float(value)
    if method == "ceil":
        factor = 10**precision
        return math.ceil(value * factor) / factor
    return round(value, precision)


class _States:
    """``states('x')`` returns the state string, ``states['x']`` the state object or None."""

    def __init__(self, hass: "FakeHass") -> None:
        self._hass = hass

    def __call__(self, entity_id):
        return self._hass.state(entity_id)

    def __getitem__(self, entity_id):
        if entity_id not in self._hass.states:
            return None
        return {"entity_id": entity_id, "state": self._hass.states[entity_id]}


class FakeHass:
    """Entity states and attributes used by the rendered templates."""

    def __init__(self, states: dict[str, str] | None = None, attributes: dict | None = None):
        self.states = states or {}
        self.attributes = attributes or {}

    def env(self) -> "jinja2.Environment":
        env = jinja2.Environment()
        env.filters.update(
            float=_float,
            int=_int,
            bool=_bool,
            from_json=_from_json,
            to_json=lambda v: json.dumps(v, separators=(",", ":")),
            is_number=_is_number,
            round=_round,
            timestamp_custom=_timestamp_custom,
        )
        env.tests.update(
            is_number=_is_number,
            list=lambda v: isinstance(v, list),
            match=lambda v, pattern: re.match(pattern, str(v)) is not None,
            is_state=self.is_state,
        )
        env.globals.update(
            states=_States(self),
            state_attr=self.state_attr,
            is_state=self.is_state,
            integration_entities=lambda domain: [],
            as_timestamp=_as_timestamp,
            now=lambda: datetime.fromtimestamp(NOW),
            timedelta=timedelta,
            none=None,
        )
        return env

    def state(self, entity_id):
        return self.states.get(entity_id, "unknown")

    def state_attr(self, entity_id, attribute):
        return self.attributes.get(entity_id, {}).get(attribute)

    def is_state(self, entity_id, value):
        values = value if isinstance(value, list) else [value]
        return self.state(entity_id) in values


def _render(hass: FakeHass, template: str, context: dict) -> str:
    template = template.replace("as_timestamp(now())", str(NOW))
    return hass.env().from_string(template).render(**context).strip()


def _action_variables(doc: dict, alias: str) -> dict:
    return next(action for action in doc["actions"] if action.get("alias") == alias)["variables"]


def _zone_context() -> dict:
    context = {}
    for zone in range(1, 13):
        context[f"zone_{zone}_soil_type"] = "loam"
        context[f"zone_{zone}_plant_type"] = "shrubs"
        context[f"zone_{zone}_valve"] = ""
    return context


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class WaterBalancePayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.balance = _action_variables(cls.doc, "Zaktualizuj trwały bilans wody")

    def _payload(self, saved: dict, rain_total: float) -> str:
        hass = FakeHass()
        context = _zone_context()
        context.update(
            water_balance_saved=saved,
            water_balance_saved_valid=True,
            season_ok=True,
            water_balance_new_season=False,
            water_balance_elapsed_days=0.5,
            reference_et_mm=7.5,
            effective_rain_increment_mm=0,
            water_balance_rain_total_mm=rain_total,
        )
        deficits = _render(hass, self.balance["water_balance_deficits_json"], context)
        context["water_balance_deficits_json"] = deficits
        return _render(hass, self.balance["water_balance_payload"], context)

    def test_worst_case_payload_fits_default_text_helper(self) -> None:
        # Every section at its largest possible capacity and a 4-digit rain total.
        saved = {"v": 1, "t": NOW - 3600, "r": 9999.9, "z": [999.99] * 12}
        payload = self._payload(saved, 9999.94)
        self.assertLessEqual(len(payload), 100, payload)
        decoded = json.loads(payload)
        self.assertEqual(decoded["v"], 1)
        self.assertEqual(len(decoded["z"]), 12)
        self.assertTrue(all(len(str(v).split(".")[-1]) <= 1 for v in decoded["z"]))

    def test_saved_balance_is_read_when_home_assistant_returns_a_dict(self) -> None:
        # Home Assistant turns a rendered JSON variable into a native dict, so the
        # saved balance must be accepted both as a dict and as a JSON string.
        saved = {"v": 1, "t": NOW - 3600, "r": 0, "z": [30] * 12}
        for value in (saved, json.dumps(saved)):
            context = dict(water_balance_enabled=True, water_balance_saved=value)
            self.assertEqual(_render(FakeHass(), self.balance["water_balance_saved_valid"], context), "True")
        deficits = [1.5] * 12
        for value in (deficits, json.dumps(deficits)):
            rendered = _render(FakeHass(), self.balance["water_balance_deficits"], {"water_balance_deficits_json": value})
            self.assertEqual(rendered, str(deficits))

    def test_helper_limit_is_checked_against_real_payload_length(self) -> None:
        text = self.balance["water_balance_helper_ok"]
        hass = FakeHass({"input_text.balance": "{}"})
        common = dict(water_balance_enabled=True, water_balance_helper="input_text.balance")
        self.assertEqual(
            _render(hass, text, dict(common, water_balance_payload_length=99, water_balance_helper_max=100)),
            "True",
        )
        self.assertEqual(
            _render(hass, text, dict(common, water_balance_payload_length=99, water_balance_helper_max=50)),
            "False",
        )
        missing = FakeHass({})
        self.assertEqual(
            _render(missing, text, dict(common, water_balance_payload_length=60, water_balance_helper_max=255)),
            "False",
        )

    def test_unavailable_rain_source_keeps_previous_total_and_adds_no_rain(self) -> None:
        hass = FakeHass({"sensor.rain_24h": "unavailable"})
        context = dict(
            rain_amount_sensor="sensor.rain_24h",
            forecast_weather_entity="weather.home",
            water_balance_saved={"v": 1, "t": NOW, "r": 12.0, "z": [0] * 12},
            water_balance_saved_valid=True,
            current_rain_mm=0,
        )
        source_ok = _render(hass, self.balance["water_balance_rain_source_ok"], context)
        self.assertEqual(source_ok, "False")
        context["water_balance_rain_source_ok"] = source_ok
        total = _render(hass, self.balance["water_balance_rain_total_mm"], context)
        self.assertEqual(float(total), 12.0)
        context["water_balance_rain_total_mm"] = total
        increment = _render(hass, self.balance["water_balance_rain_increment_mm"], context)
        self.assertEqual(float(increment), 0)

    def test_returning_rain_source_is_not_credited_twice(self) -> None:
        hass = FakeHass({"sensor.rain_24h": "11"})
        context = dict(
            rain_amount_sensor="sensor.rain_24h",
            forecast_weather_entity="weather.home",
            water_balance_saved={"v": 1, "t": NOW, "r": 12.0, "z": [0] * 12},
            water_balance_saved_valid=True,
            current_rain_mm=11,
        )
        context["water_balance_rain_source_ok"] = _render(hass, self.balance["water_balance_rain_source_ok"], context)
        context["water_balance_rain_total_mm"] = _render(hass, self.balance["water_balance_rain_total_mm"], context)
        increment = _render(hass, self.balance["water_balance_rain_increment_mm"], context)
        self.assertEqual(float(increment), 0)


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class ForecastRainEstimateTests(unittest.TestCase):
    """Without a station rain sensor the daily forecast is booked once per day as an estimate."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.balance = _action_variables(_load_blueprint(), "Zaktualizuj trwały bilans wody")

    def _render(self, name: str, context: dict, hass: FakeHass | None = None) -> str:
        return _render(hass or FakeHass(), self.balance[name], context)

    def _context(self, saved: dict, forecast: list) -> dict:
        context = dict(
            water_balance_enabled=True,
            rain_amount_sensor="",
            forecast_weather_entity="weather.home",
            water_balance_saved=saved,
            water_balance_saved_valid=True,
            daily_forecast={"weather.home": {"forecast": forecast}},
            current_rain_mm=0,
        )
        context["water_balance_rain_from_forecast"] = self._render("water_balance_rain_from_forecast", context)
        context["water_balance_day"] = self._render("water_balance_day", context)
        context["water_balance_saved_day"] = self._render("water_balance_saved_day", context)
        return context

    @staticmethod
    def _iso(offset: int = 0) -> str:
        return (datetime.fromtimestamp(NOW) + timedelta(days=offset)).replace(hour=12).isoformat()

    def test_forecast_mode_only_without_station_sensor(self) -> None:
        context = dict(water_balance_enabled=True, rain_amount_sensor="sensor.rain")
        self.assertEqual(self._render("water_balance_rain_from_forecast", context), "False")
        context["rain_amount_sensor"] = ""
        self.assertEqual(self._render("water_balance_rain_from_forecast", context), "True")

    def test_today_forecast_is_stored_and_not_credited_the_same_day(self) -> None:
        saved = {"v": 1, "t": NOW, "z": [10] * 12, "p": 3.0}
        context = self._context(saved, [{"datetime": self._iso(), "precipitation": 6.4}])
        self.assertEqual(float(self._render("water_balance_forecast_today_mm", context)), 6.4)
        context["water_balance_forecast_today_mm"] = 6.4
        context["water_balance_rain_source_ok"] = self._render("water_balance_rain_source_ok", context)
        context["water_balance_rain_total_mm"] = self._render("water_balance_rain_total_mm", context)
        self.assertEqual(float(self._render("water_balance_rain_increment_mm", context)), 0)

    def test_yesterday_forecast_is_credited_once_on_a_new_day(self) -> None:
        saved = {"v": 1, "t": NOW - 86400, "z": [10] * 12, "p": 5.5}
        context = self._context(saved, [{"datetime": self._iso(), "precipitation": 0.0}])
        context["water_balance_rain_source_ok"] = self._render("water_balance_rain_source_ok", context)
        context["water_balance_rain_total_mm"] = self._render("water_balance_rain_total_mm", context)
        self.assertEqual(float(self._render("water_balance_rain_increment_mm", context)), 5.5)

    def test_payload_keeps_forecast_and_day_and_fits_default_helper(self) -> None:
        context = dict(
            water_balance_rain_total_mm=0.0,
            water_balance_deficits_json=json.dumps([90.0] * 12, separators=(",", ":")),
            water_balance_rain_from_forecast=True,
            water_balance_forecast_today_mm=99.9,
        )
        payload = self._render("water_balance_payload", context)
        decoded = json.loads(payload)
        self.assertEqual(decoded["p"], 99.9)
        self.assertNotIn("r", decoded)
        self.assertLessEqual(len(payload), 100, payload)

    def test_inches_in_forecast_are_converted(self) -> None:
        hass = FakeHass({}, {"weather.home": {"precipitation_unit": "in"}})
        saved = {"v": 1, "t": NOW, "r": 0, "z": [0] * 12}
        context = self._context(saved, [{"datetime": self._iso(), "precipitation": 0.5}])
        self.assertEqual(float(self._render("water_balance_forecast_today_mm", context, hass)), 12.7)


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class SeasonBalanceTests(unittest.TestCase):
    """Evapotranspiration is added for at most 7 days and a new season starts from zero."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.balance = _action_variables(_load_blueprint(), "Zaktualizuj trwały bilans wody")

    def _render(self, name: str, context: dict) -> str:
        return _render(FakeHass(), self.balance[name], context)

    def _deficits(self, context: dict) -> list:
        context = dict(_zone_context(), reference_et_mm=7.5, effective_rain_increment_mm=0, **context)
        return json.loads(self._render("water_balance_deficits_json", context))

    def test_season_start_timestamp(self) -> None:
        now = datetime.fromtimestamp(NOW)
        first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        same = dict(season_start_month=now.month, season_end_month=now.month)
        self.assertEqual(int(self._render("water_balance_season_start_ts", same)), int(first.timestamp()))
        # Season crossing the new year that started in the previous calendar year.
        later = now.month % 12 + 1
        wrap = dict(season_start_month=later, season_end_month=now.month)
        expected = first.replace(year=now.year - 1 if later > now.month else now.year, month=later)
        self.assertEqual(int(self._render("water_balance_season_start_ts", wrap)), int(expected.timestamp()))

    def test_long_gap_inside_season_adds_at_most_seven_days(self) -> None:
        saved = {"v": 1, "t": NOW - 20 * 86400, "r": 0, "z": [10] * 12}
        common = dict(
            water_balance_saved=saved,
            water_balance_saved_valid=True,
            season_ok=True,
            water_balance_season_start_ts=NOW - 100 * 86400,
            water_balance_raw_elapsed_days=20,
        )
        self.assertEqual(self._render("water_balance_new_season", common), "False")
        elapsed = self._render("water_balance_elapsed_days", common)
        self.assertEqual(float(elapsed), 7.0)
        deficits = self._deficits(dict(common, water_balance_elapsed_days=elapsed, water_balance_new_season=False))
        self.assertEqual(deficits[0], round(10 + 7.5 * 0.55 * 7, 1))

    def test_new_season_starts_from_zero(self) -> None:
        saved = {"v": 1, "t": NOW - 200 * 86400, "r": 0, "z": [40] * 12}
        common = dict(
            water_balance_saved=saved,
            water_balance_saved_valid=True,
            season_ok=True,
            water_balance_season_start_ts=NOW - 2 * 86400,
            water_balance_raw_elapsed_days=200,
        )
        new_season = self._render("water_balance_new_season", common)
        self.assertEqual(new_season, "True")
        elapsed = self._render("water_balance_elapsed_days", dict(common, water_balance_new_season=True))
        self.assertAlmostEqual(float(elapsed), 2.0, places=3)
        deficits = self._deficits(dict(common, water_balance_elapsed_days=elapsed, water_balance_new_season=True))
        self.assertEqual(deficits[0], round(7.5 * 0.55 * float(elapsed), 1))

    def test_off_season_keeps_balance_at_zero(self) -> None:
        saved = {"v": 1, "t": NOW - 86400, "r": 0, "z": [40] * 12}
        common = dict(
            water_balance_saved=saved,
            water_balance_saved_valid=True,
            season_ok=False,
            water_balance_season_start_ts=NOW + 60 * 86400,
            water_balance_raw_elapsed_days=1,
        )
        self.assertEqual(self._render("water_balance_new_season", common), "False")
        elapsed = self._render("water_balance_elapsed_days", common)
        self.assertEqual(float(elapsed), 0.0)
        deficits = self._deficits(dict(common, water_balance_elapsed_days=elapsed, water_balance_new_season=False))
        self.assertEqual(deficits, [0] * 12)


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class SkipReasonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.reason = _action_variables(cls.doc, "Wylicz powód pominięcia podlewania")

    def _context(self, **overrides) -> dict:
        context = _zone_context()
        context.update(
            season_ok=True,
            min_dose_mm=3,
            max_dose_mm=10,
            water_balance_enabled=True,
            water_balance_helper="input_text.balance",
            water_balance_helper_ok=True,
            water_balance_helper_max=255,
            water_balance_payload_length=61,
            zone_count=1,
            zone_1_valve="switch.relay",
            daily_forecast_available=True,
            weather_data_ok=True,
            weather_ok=True,
            rain_binary_sensor="",
            rain_sensor_ok=True,
            soil_moisture_ok=True,
            forecast_rain_ok=True,
            temp_available=True,
            temp_ok=True,
            wind_available=True,
            wind_ok=True,
            forecast_weather_entity="weather.home",
            current_weather_entity="weather.home",
            temperature_source_entity="",
            wind_source_entity="",
        )
        context.update(overrides)
        return context

    def _reason(self, hass: FakeHass, **overrides) -> str:
        context = self._context(**overrides)
        context["zones_non_rc2"] = _render(hass, self.reason["zones_non_rc2"], context)
        context["zones_non_rc2"] = eval(context["zones_non_rc2"])  # noqa: S307 - rendered list literal
        context["rain_sensor_unavailable"] = _render(hass, self.reason["rain_sensor_unavailable"], context) == "True"
        return _render(hass, self.reason["irrigation_skip_reason"], context)

    def test_ready_configuration_has_no_skip_reason(self) -> None:
        hass = FakeHass({"input_text.balance": "{}"})
        self.assertEqual(self._reason(hass), "")

    def test_plain_switch_without_balance_helper_is_blocked_with_reason(self) -> None:
        hass = FakeHass({})
        reason = self._reason(hass, water_balance_enabled=False, water_balance_helper="")
        self.assertIn("Helper - trwały bilans wody", reason)
        self.assertIn("switch.relay", reason)

    def test_helper_too_short_is_reported(self) -> None:
        hass = FakeHass({"input_text.balance": "{}"})
        reason = self._reason(hass, water_balance_helper_ok=False, water_balance_helper_max=50, water_balance_payload_length=61)
        self.assertIn("limit 50", reason)
        self.assertIn("255", reason)

    def test_minimum_dose_above_maximum_is_reported(self) -> None:
        hass = FakeHass({"input_text.balance": "{}"})
        reason = self._reason(hass, min_dose_mm=12, max_dose_mm=10)
        self.assertIn("Minimalna dawka", reason)

    def test_unavailable_rain_sensor_has_its_own_reason(self) -> None:
        hass = FakeHass({"input_text.balance": "{}", "binary_sensor.rain": "unavailable"})
        reason = self._reason(hass, rain_binary_sensor="binary_sensor.rain", rain_sensor_ok=False)
        self.assertIn("niedostępny", reason)
        self.assertNotIn("aktywny", reason)

    def test_balance_helper_without_rain_sensor_is_not_blocked(self) -> None:
        # Without a station the rain is estimated from the forecast, so there is no block.
        hass = FakeHass({"input_text.balance": "{}"})
        self.assertEqual(self._reason(hass, rain_amount_sensor=""), "")

    def test_missing_daily_forecast_is_reported(self) -> None:
        hass = FakeHass({"input_text.balance": "{}"})
        reason = self._reason(hass, daily_forecast_available=False)
        self.assertIn("prognozy dziennej", reason)

    def test_missing_temperature_blocks(self) -> None:
        hass = FakeHass({"input_text.balance": "{}"})
        reason = self._reason(hass, temp_available=False, temp_ok=False)
        self.assertIn("Brak aktualnej temperatury", reason)


@unittest.skipIf(jinja2 is None or yaml is None, "jinja2 and PyYAML are required")
class WeatherFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = _load_blueprint()
        cls.weather = _action_variables(cls.doc, "Wylicz pogodę i wspólne warunki")

    def test_unavailable_temperature_sensor_uses_current_weather_not_forecast_maximum(self) -> None:
        hass = FakeHass(
            {"sensor.garden_temperature": "unavailable"},
            {"weather.home": {"temperature": -1.0}},
        )
        context = dict(
            temperature_source_entity="sensor.garden_temperature",
            forecast_weather_entity="weather.home",
            current_weather_entity="weather.home",
            forecast_temperature=14,
        )
        self.assertEqual(float(_render(hass, self.weather["temp_c"], context)), -1.0)

    def test_fahrenheit_weather_and_sensor_are_converted_to_celsius(self) -> None:
        context = dict(
            temperature_source_entity="",
            forecast_weather_entity="weather.home",
            current_weather_entity="weather.home",
        )
        weather = FakeHass({}, {"weather.home": {"temperature": 30, "temperature_unit": "°F"}})
        self.assertAlmostEqual(float(_render(weather, self.weather["temp_c"], context)), -1.1, places=1)
        sensor = FakeHass(
            {"sensor.garden_temperature": "50"},
            {"sensor.garden_temperature": {"unit_of_measurement": "°F"}, "weather.home": {"temperature": 99}},
        )
        context["temperature_source_entity"] = "sensor.garden_temperature"
        self.assertEqual(float(_render(sensor, self.weather["temp_c"], context)), 10.0)

    def test_forecast_rain_in_inches_is_converted_to_mm(self) -> None:
        hass = FakeHass({}, {"weather.home": {"precipitation_unit": "in"}})
        context = dict(
            forecast_weather_entity="weather.home",
            daily_forecast={"weather.home": {"forecast": [{"precipitation": 0.5}]}},
        )
        self.assertEqual(float(_render(hass, self.weather["forecast_precipitation"], context)), 12.7)

    def test_temperature_without_any_source_is_marked_missing(self) -> None:
        hass = FakeHass({"sensor.garden_temperature": "unavailable"}, {})
        context = dict(
            temperature_source_entity="sensor.garden_temperature",
            forecast_weather_entity="weather.home",
            current_weather_entity="weather.home",
        )
        temp = _render(hass, self.weather["temp_c"], context)
        self.assertEqual(_render(hass, self.weather["temp_available"], {"temp_c": temp}), "False")

    def test_unavailable_wind_sensor_falls_back_to_weather_or_blocks(self) -> None:
        context = dict(
            wind_source_entity="sensor.garden_wind",
            forecast_weather_entity="weather.home",
            current_weather_entity="weather.home",
        )
        with_weather = FakeHass(
            {"sensor.garden_wind": "unavailable"},
            {"weather.home": {"wind_speed": 5, "wind_speed_unit": "m/s"}},
        )
        self.assertEqual(float(_render(with_weather, self.weather["wind_value"], context)), 18.0)
        without_weather = FakeHass({"sensor.garden_wind": "unavailable"}, {})
        wind = _render(without_weather, self.weather["wind_value"], context)
        self.assertEqual(_render(without_weather, self.weather["wind_available"], {"wind_value": wind}), "False")

    def test_no_wind_source_and_no_weather_wind_keeps_previous_behaviour(self) -> None:
        context = dict(
            wind_source_entity="",
            forecast_weather_entity="weather.home",
            current_weather_entity="weather.home",
        )
        hass = FakeHass({}, {"weather.home": {}})
        self.assertEqual(float(_render(hass, self.weather["wind_value"], context)), 0.0)


class ValveSafetyStructureTests(unittest.TestCase):
    """Static checks of the valve safety sequence (no template engine needed)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = BLUEPRINT.read_text(encoding="utf-8")

    def test_file_has_no_byte_order_mark(self) -> None:
        self.assertFalse(BLUEPRINT.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_minimum_home_assistant_supports_outer_scope_variables(self) -> None:
        self.assertIn("min_version: 2025.4.0", self.text)

    def test_restart_reload_and_runtime_watchdog_triggers_exist(self) -> None:
        self.assertIn("trigger: homeassistant\n    id: ha_start\n    event: start", self.text)
        self.assertIn("event_type: automation_reloaded", self.text)
        self.assertIn("id: valve_watchdog", self.text)
        self.assertIn("mode: queued", self.text)

    def test_start_waits_sixty_seconds_and_accepts_opening(self) -> None:
        wait = self.text.index("alias: Poczekaj na potwierdzenie otwarcia sekcji")
        self.assertIn('timeout: "00:01:00"', self.text[wait : wait + 300])
        self.assertIn("- opening", self.text)

    def test_close_is_always_sent_confirmed_and_retried(self) -> None:
        start = self.text.index("alias: Zapamiętaj wynik otwarcia sekcji")
        close = self.text.index("alias: Zamknij sekcję i potwierdź zamknięcie", start)
        alarm = self.text.index("alias: Alarm gdy sekcja nie potwierdziła zamknięcia", close)
        failed_start = self.text.index("alias: Obsłuż brak potwierdzenia otwarcia", alarm)
        self.assertLess(start, close)
        block = self.text[close:alarm]
        self.assertIn("repeat.index >= 3", block)
        self.assertIn('timeout: "00:00:30"', block)
        self.assertIn("valve_closed_states", block)
        self.assertIn("smart_irrigation_valve_alarm", self.text[alarm:failed_start])
        # The close block is not nested under the "started" branch, so a start
        # that was not confirmed still sends the close command.
        def indent(index: int) -> int:
            line_start = self.text.rfind(chr(10), 0, index) + 1
            return index - line_start

        self.assertEqual(indent(close), indent(start))

    def test_every_valve_command_continues_on_error(self) -> None:
        for action in (
            "rainbird_rc2.start_zone",
            "rainbird_rc2.stop_zone",
            "rainbird.start_irrigation",
            "switch.turn_on",
            "switch.turn_off",
            "valve.open_valve",
            "valve.close_valve",
        ):
            for match in re.finditer(rf"action: {re.escape(action)}\n", self.text):
                following = self.text[match.end() : match.end() + 80]
                self.assertIn("continue_on_error: true", following, action)

    def test_report_uses_cycle_record_instead_of_rc2_attributes(self) -> None:
        summary = self.text.index("irrigation_cycle_summary: |-")
        self.assertIn("watered_sections", self.text[summary:])
        self.assertNotIn("last_ts >= as_timestamp(irrigation_cycle_started_at", self.text)


if __name__ == "__main__":
    unittest.main()
