from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from thermodynamics import (  # noqa: E402
    carnot_efficiency,
    celsius_to_kelvin,
    entropy_generation_heat_engine,
    exergy_of_heat,
    first_law_delta_u,
    heat_engine,
    heat_pump_cop_heating,
    ideal_gas_temperature,
    monte_carlo_heat_engine,
    multistage_efficiency,
    thermal_storage_cycle,
)


class ThermodynamicFoundationTests(unittest.TestCase):
    def test_temperature_conversion(self) -> None:
        self.assertAlmostEqual(celsius_to_kelvin(0.0), 273.15)
        with self.assertRaises(ValueError):
            celsius_to_kelvin(-274.0)

    def test_first_law_sign_convention(self) -> None:
        self.assertAlmostEqual(first_law_delta_u(120.0, 45.0), 75.0)

    def test_ideal_gas_temperature(self) -> None:
        temperature = ideal_gas_temperature(101325.0, 0.024465, 1.0)
        self.assertAlmostEqual(temperature, 298.15, places=1)

    def test_carnot_bounds(self) -> None:
        efficiency = carnot_efficiency(800.0, 300.0)
        self.assertAlmostEqual(efficiency, 0.625)
        with self.assertRaises(ValueError):
            carnot_efficiency(300.0, 300.0)

    def test_heat_engine_conservation_and_limit(self) -> None:
        result = heat_engine(1000.0, 800.0, 300.0, 0.60)
        self.assertAlmostEqual(result.first_law_residual, 0.0)
        self.assertLessEqual(result.actual_efficiency, result.carnot_efficiency)
        self.assertGreaterEqual(result.entropy_generation, 0.0)

    def test_entropy_generation_reversible_limit(self) -> None:
        q_hot = 1000.0
        eta = carnot_efficiency(800.0, 300.0)
        q_cold = q_hot * (1.0 - eta)
        self.assertAlmostEqual(entropy_generation_heat_engine(q_hot, q_cold, 800.0, 300.0), 0.0)

    def test_heat_pump_cop(self) -> None:
        ideal = heat_pump_cop_heating(320.0, 280.0)
        actual = heat_pump_cop_heating(320.0, 280.0, 0.5)
        self.assertAlmostEqual(ideal, 8.0)
        self.assertAlmostEqual(actual, 4.0)

    def test_exergy_of_heat(self) -> None:
        self.assertAlmostEqual(exergy_of_heat(100.0, 600.0, 300.0), 50.0)

    def test_multistage_efficiency(self) -> None:
        self.assertAlmostEqual(multistage_efficiency((0.9, 0.8, 0.95)), 0.684)

    def test_storage_conservation(self) -> None:
        result = thermal_storage_cycle(100.0, 0.95, 0.90, 0.98)
        self.assertAlmostEqual(result.conservation_residual, 0.0)
        self.assertAlmostEqual(result.round_trip_efficiency, 0.8379)

    def test_uncertainty_repeatable(self) -> None:
        kwargs = dict(
            heat_input=1000.0,
            hot_temperature_k=823.15,
            cold_temperature_k=303.15,
            second_law_fraction=0.58,
            samples=500,
            seed=42,
        )
        first = monte_carlo_heat_engine(**kwargs)
        second = monte_carlo_heat_engine(**kwargs)
        self.assertEqual(first, second)
        self.assertTrue(math.isfinite(float(first["efficiency_mean"])))


if __name__ == "__main__":
    unittest.main(verbosity=2)
