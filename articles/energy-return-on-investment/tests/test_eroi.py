from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from eroi import (
    EnergyInvestment,
    EnergyProject,
    delivered_eroi,
    energy_payback_years,
    monte_carlo_eroi,
    net_energy_fraction,
)


class CoreTests(unittest.TestCase):
    def test_basic_eroi(self):
        p = EnergyProject("x", 1000, EnergyInvestment(construction_mwh=100))
        self.assertAlmostEqual(p.eroi(), 10)

    def test_net_energy(self):
        p = EnergyProject("x", 1000, EnergyInvestment(construction_mwh=100))
        self.assertAlmostEqual(p.net_energy_mwh(), 900)

    def test_net_fraction(self):
        self.assertAlmostEqual(net_energy_fraction(10), 0.9)

    def test_invalid_negative_investment(self):
        p = EnergyProject("x", 1000, EnergyInvestment(construction_mwh=-1))
        with self.assertRaises(ValueError):
            p.eroi()

    def test_zero_investment_rejected(self):
        p = EnergyProject("x", 1000, EnergyInvestment())
        with self.assertRaises(ValueError):
            p.eroi()

    def test_empty_name_rejected(self):
        p = EnergyProject("", 1000, EnergyInvestment(construction_mwh=100))
        with self.assertRaises(ValueError):
            p.eroi()

    def test_energy_payback(self):
        self.assertAlmostEqual(energy_payback_years(1500, 600, 30), 1500 / 570)

    def test_payback_rejects_nonpositive_net(self):
        with self.assertRaises(ValueError):
            energy_payback_years(100, 50, 50)

    def test_delivered_eroi(self):
        value = delivered_eroi(700, 300, 0.85, 70, 15, 5)
        self.assertAlmostEqual(value, 955 / 90)

    def test_storage_efficiency_range(self):
        with self.assertRaises(ValueError):
            delivered_eroi(700, 300, 1.2, 70, 15)


class UncertaintyTests(unittest.TestCase):
    def setUp(self):
        self.project = EnergyProject(
            "x",
            1000,
            EnergyInvestment(construction_mwh=100),
        )

    def test_repeatable(self):
        a = monte_carlo_eroi(self.project, draws=100, seed=7)
        b = monte_carlo_eroi(self.project, draws=100, seed=7)
        self.assertEqual(a, b)

    def test_quantiles_ordered(self):
        result = monte_carlo_eroi(self.project, draws=200, seed=8)
        self.assertLessEqual(result["p05_eroi"], result["p50_eroi"])
        self.assertLessEqual(result["p50_eroi"], result["p95_eroi"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
