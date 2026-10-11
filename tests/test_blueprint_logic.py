from __future__ import annotations

import unittest
from pathlib import Path


BLUEPRINT = (
    Path(__file__).parents[1]
    / "blueprints"
    / "automation"
    / "smart_irrigation_automation"
    / "smart_irrigation.yaml"
)


def reconstructed_deficit(
    *,
    target_mm: float,
    last_runtime_minutes: float,
    precipitation_rate_mm_h: float,
    efficiency: float,
    et0_mm_day: float,
    crop_coefficient: float,
    elapsed_days: float,
    effective_rain_mm: float,
) -> tuple[float, float, float]:
    effective_rate = precipitation_rate_mm_h * efficiency
    delivered = last_runtime_minutes * effective_rate / 60
    carryover = max(target_mm - delivered, 0)
    deficit = max(
        carryover + et0_mm_day * crop_coefficient * elapsed_days - effective_rain_mm,
        0,
    )
    return delivered, carryover, deficit


def update_persistent_deficit(
    *,
    previous_deficit_mm: float,
    et0_mm_day: float,
    crop_coefficient: float,
    elapsed_days: float,
    previous_rain_total_mm: float,
    current_rain_total_mm: float,
    rain_credit: float,
    capacity_mm: float,
) -> float:
    rain_increment = max(current_rain_total_mm - previous_rain_total_mm, 0)
    raw = (
        previous_deficit_mm
        + et0_mm_day * crop_coefficient * elapsed_days
        - rain_increment * rain_credit
    )
    return min(max(raw, 0), capacity_mm)


class WaterBalanceTests(unittest.TestCase):
    def test_runtime_cap_carries_unfilled_depth_forward(self) -> None:
        delivered, carryover, deficit = reconstructed_deficit(
            target_mm=10,
            last_runtime_minutes=45,
            precipitation_rate_mm_h=12,
            efficiency=0.75,
            et0_mm_day=3.9,
            crop_coefficient=0.75,
            elapsed_days=2.3,
            effective_rain_mm=0,
        )

        self.assertAlmostEqual(delivered, 6.75)
        self.assertAlmostEqual(carryover, 3.25)
        self.assertAlmostEqual(deficit, 9.9775)

    def test_recent_effective_rain_clears_current_deficit(self) -> None:
        _, _, deficit = reconstructed_deficit(
            target_mm=10,
            last_runtime_minutes=45,
            precipitation_rate_mm_h=12,
            efficiency=0.75,
            et0_mm_day=3.9,
            crop_coefficient=0.75,
            elapsed_days=2.3,
            effective_rain_mm=13.8 * 0.8,
        )

        self.assertEqual(deficit, 0)

    def test_rolling_rain_drop_does_not_restore_old_deficit(self) -> None:
        after_rain = update_persistent_deficit(
            previous_deficit_mm=8,
            et0_mm_day=0,
            crop_coefficient=0.75,
            elapsed_days=0,
            previous_rain_total_mm=0,
            current_rain_total_mm=11.1,
            rain_credit=0.8,
            capacity_mm=30,
        )
        after_sensor_window_moves = update_persistent_deficit(
            previous_deficit_mm=after_rain,
            et0_mm_day=0,
            crop_coefficient=0.75,
            elapsed_days=0,
            previous_rain_total_mm=11.1,
            current_rain_total_mm=3,
            rain_credit=0.8,
            capacity_mm=30,
        )

        self.assertEqual(after_rain, 0)
        self.assertEqual(after_sensor_window_moves, 0)

    def test_same_measured_rain_is_credited_only_once(self) -> None:
        first = update_persistent_deficit(
            previous_deficit_mm=12,
            et0_mm_day=0,
            crop_coefficient=0.75,
            elapsed_days=0,
            previous_rain_total_mm=2,
            current_rain_total_mm=7,
            rain_credit=0.8,
            capacity_mm=30,
        )
        second = update_persistent_deficit(
            previous_deficit_mm=first,
            et0_mm_day=0,
            crop_coefficient=0.75,
            elapsed_days=0,
            previous_rain_total_mm=7,
            current_rain_total_mm=7,
            rain_credit=0.8,
            capacity_mm=30,
        )

        self.assertEqual(first, 8)
        self.assertEqual(second, 8)

    def test_completed_irrigation_reduces_only_its_section(self) -> None:
        deficits = [9.0, 7.0, 2.0]
        section_index = 1
        delivered = 5.5
        updated = [
            max(value - delivered, 0) if index == section_index else value
            for index, value in enumerate(deficits)
        ]

        self.assertEqual(updated, [9.0, 1.5, 2.0])


class NotificationFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = BLUEPRINT.read_text(encoding="utf-8")

    def test_global_skip_notification_excludes_condition_checks(self) -> None:
        self.assertIn(
            "irrigation_skip_reason | trim | length > 0 and not "
            "(trigger_is_condition_check | bool) and "
            "(create_persistent_notification | bool)",
            self.text,
        )

    def test_start_notification_follows_controller_confirmation(self) -> None:
        confirmation = self.text.index("Zapamiętaj wynik otwarcia sekcji")
        notification = self.text.index(
            "Powiadom po potwierdzeniu pierwszej uruchomionej sekcji"
        )
        self.assertLess(confirmation, notification)


class BlueprintModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = BLUEPRINT.read_text(encoding="utf-8")

    def test_weekly_cycle_setting_is_not_part_of_blueprint(self) -> None:
        self.assertNotIn("waterings_per_week", self.text)

    def test_forecast_is_not_credited_as_measured_rain(self) -> None:
        rain_credit = self.text.index("rain_credit_mm:")
        balance_update = self.text.index("Zaktualizuj trwały bilans wody")
        self.assertNotIn(
            "forecast_precipitation",
            self.text[rain_credit:balance_update],
        )

    def test_persistent_balance_is_written_and_reduced_after_a_run(self) -> None:
        self.assertIn("Helper - trwały bilans wody", self.text)
        self.assertIn("Odejmij wykonane podlewanie od bilansu sekcji", self.text)
        self.assertIn("effective_rain_increment_mm", self.text)


if __name__ == "__main__":
    unittest.main()
