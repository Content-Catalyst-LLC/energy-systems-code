from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from smart_grids import (
    DERResource,
    aggregate_der_capacity,
    annual_energy_reduction_mwh,
    charging_power_mw,
    communications_availability,
    demand_response_net_load,
    dispatch_available_der,
    flisr_customer_hours_avoided,
    load_factor,
    monte_carlo_flexible_peak,
    restoration_fraction,
)


class FlexibilityTests(unittest.TestCase):
    def test_ev_article_examples(self):
        self.assertAlmostEqual(charging_power_mw(10000, 14, 2), 70.0)
        self.assertAlmostEqual(charging_power_mw(10000, 14, 7), 20.0)

    def test_demand_response_article_example(self):
        self.assertAlmostEqual(demand_response_net_load(85, 12), 73.0)

    def test_volt_var_article_example(self):
        self.assertAlmostEqual(
            annual_energy_reduction_mwh(10, 0.012, 4000),
            480.0,
        )

    def test_load_factor_article_example(self):
        self.assertAlmostEqual(load_factor(0.72, 720, 0.005), 0.2)

    def test_invalid_charging_hours(self):
        with self.assertRaises(ValueError):
            charging_power_mw(10, 14, 0)


class AutomationTests(unittest.TestCase):
    def test_flisr_article_example(self):
        self.assertAlmostEqual(
            flisr_customer_hours_avoided(9800, 90, 2),
            9800 * 88 / 60,
        )

    def test_parallel_communications_improves_availability(self):
        value = communications_availability(0.99, 0.95)
        self.assertGreater(value, 0.99)
        self.assertLessEqual(value, 1.0)

    def test_restoration_fraction(self):
        self.assertAlmostEqual(restoration_fraction(12000, 9800), 9800 / 12000)


class DERTests(unittest.TestCase):
    def setUp(self):
        self.resources = [
            DERResource("Battery", 10, 0.9, 0.8),
            DERResource("DR", 5, 0.8, 0.5),
        ]

    def test_nameplate(self):
        self.assertAlmostEqual(aggregate_der_capacity(self.resources), 15.0)

    def test_dispatchable_below_nameplate(self):
        self.assertLess(
            dispatch_available_der(self.resources),
            aggregate_der_capacity(self.resources),
        )


class UncertaintyTests(unittest.TestCase):
    def test_repeatable(self):
        a = monte_carlo_flexible_peak(
            baseline_peak_mw=88,
            flexible_capacity_mw=20,
            draws=100,
            seed=7,
        )
        b = monte_carlo_flexible_peak(
            baseline_peak_mw=88,
            flexible_capacity_mw=20,
            draws=100,
            seed=7,
        )
        self.assertEqual(a, b)

    def test_quantiles_ordered(self):
        r = monte_carlo_flexible_peak(
            baseline_peak_mw=88,
            flexible_capacity_mw=20,
            draws=200,
            seed=8,
        )
        self.assertLessEqual(r["p05_net_peak_mw"], r["p50_net_peak_mw"])
        self.assertLessEqual(r["p50_net_peak_mw"], r["p95_net_peak_mw"])

    def test_nonnegative_peak(self):
        r = monte_carlo_flexible_peak(
            baseline_peak_mw=10,
            flexible_capacity_mw=100,
            draws=50,
            seed=9,
        )
        self.assertGreaterEqual(r["p05_net_peak_mw"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
