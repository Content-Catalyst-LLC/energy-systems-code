from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from grid_reliability import (
    OutageEvent,
    annualized_risk,
    caidi,
    expected_unserved_energy_mwh,
    frequency_deviation_hz,
    monte_carlo_resource_adequacy,
    reserve_margin,
    restoration_auc,
    saidi,
    saifi,
)


class ReliabilityMetricTests(unittest.TestCase):
    def setUp(self):
        self.events = [
            OutageEvent(10000, 2.0),
            OutageEvent(5000, 4.0),
            OutageEvent(20000, 1.0),
        ]

    def test_saidi_article_example(self):
        self.assertAlmostEqual(saidi(self.events, 100000), 0.6)

    def test_saifi_article_example(self):
        self.assertAlmostEqual(saifi(self.events, 100000), 0.35)

    def test_caidi_article_example(self):
        self.assertAlmostEqual(caidi(self.events, 100000), 0.6 / 0.35)

    def test_reserve_margin(self):
        self.assertAlmostEqual(reserve_margin(42000, 36000), 1 / 6)

    def test_frequency_response(self):
        self.assertAlmostEqual(frequency_deviation_hz(600, 10000), -0.06)

    def test_eue(self):
        events = [
            OutageEvent(1, 2.0, unserved_mw=10, probability=0.5),
            OutageEvent(1, 1.0, unserved_mw=20, probability=0.25),
        ]
        self.assertAlmostEqual(expected_unserved_energy_mwh(events), 15.0)

    def test_invalid_customers(self):
        with self.assertRaises(ValueError):
            saidi(self.events, 0)


class ResilienceTests(unittest.TestCase):
    def test_annualized_risk_article_example(self):
        self.assertAlmostEqual(annualized_risk(0.02, 80.0), 1.6)

    def test_restoration_auc(self):
        result = restoration_auc([0, 1, 2], [0.5, 0.75, 1.0])
        self.assertAlmostEqual(result, 1.5)

    def test_invalid_restoration_curve(self):
        with self.assertRaises(ValueError):
            restoration_auc([0, 2, 1], [0.5, 0.7, 1.0])


class UncertaintyTests(unittest.TestCase):
    def test_repeatable(self):
        a = monte_carlo_resource_adequacy(
            dependable_capacity_mw=42000,
            peak_load_mw=36000,
            draws=100,
            seed=7,
        )
        b = monte_carlo_resource_adequacy(
            dependable_capacity_mw=42000,
            peak_load_mw=36000,
            draws=100,
            seed=7,
        )
        self.assertEqual(a, b)

    def test_probability_bounds(self):
        r = monte_carlo_resource_adequacy(
            dependable_capacity_mw=42000,
            peak_load_mw=36000,
            draws=200,
            seed=8,
        )
        self.assertGreaterEqual(r["shortfall_probability"], 0)
        self.assertLessEqual(r["shortfall_probability"], 1)

    def test_quantile_order(self):
        r = monte_carlo_resource_adequacy(
            dependable_capacity_mw=42000,
            peak_load_mw=36000,
            draws=200,
            seed=8,
        )
        self.assertLessEqual(r["p05_margin_mw"], r["p50_margin_mw"])
        self.assertLessEqual(r["p50_margin_mw"], r["p95_margin_mw"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
