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
        confirmation = self.text.index("Zapamietaj czas faktycznego startu")
        notification = self.text.index(
            "Powiadom po potwierdzeniu pierwszej uruchomionej sekcji"
        )
        self.assertLess(confirmation, notification)


if __name__ == "__main__":
    unittest.main()
