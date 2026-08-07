from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from electricity_grids import (
    Branch,
    BusInjection,
    GridNetwork,
    dc_line_flow_mw,
    frequency_deviation_hz,
    monte_carlo_peak_balance,
    reserve_margin,
    storage_dispatch,
    transmission_loss_mw,
)


class GridCoreTests(unittest.TestCase):
    def test_dc_line_flow(self):
        self.assertAlmostEqual(dc_line_flow_mw(0.04, 0.01, 0.10, 100.0), 30.0)

    def test_reserve_margin(self):
        self.assertAlmostEqual(reserve_margin(3350, 3000), 350 / 3000)

    def test_frequency_response(self):
        self.assertAlmostEqual(frequency_deviation_hz(450, 7500), -0.06)

    def test_transmission_loss_nonnegative(self):
        self.assertGreaterEqual(transmission_loss_mw(500, 0.01, 1.0, 100.0), 0)

    def test_invalid_branch(self):
        with self.assertRaises(ValueError):
            Branch("x", "A", "A", 0.1, 100).validate()

    def test_storage_discharge(self):
        result = storage_dispatch(900, 250, 1, 300, 1200, 0.90)
        self.assertLess(result["grid_mw"], 0)
        self.assertLess(result["new_soc_mwh"], 900)

    def test_storage_charge(self):
        result = storage_dispatch(300, -200, 1, 300, 1200, 0.90)
        self.assertGreater(result["grid_mw"], 0)
        self.assertGreater(result["new_soc_mwh"], 300)


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.network = GridNetwork([
            Branch("AB", "A", "B", 0.1, 100),
            Branch("BC", "B", "C", 0.2, 80),
        ])

    def test_bus_count(self):
        self.assertEqual(self.network.buses, ("A", "B", "C"))

    def test_flows(self):
        flows = self.network.flows_from_angles({"A": 0.03, "B": 0.01, "C": 0.0})
        self.assertAlmostEqual(flows["AB"], 20.0)
        self.assertAlmostEqual(flows["BC"], 5.0)

    def test_overload_detection(self):
        overloaded = self.network.overloaded({"AB": 120.0, "BC": 40.0})
        self.assertEqual(overloaded, ("AB",))

    def test_system_balance(self):
        injections = [
            BusInjection("A", 100, 20),
            BusInjection("B", 20, 100),
        ]
        self.assertAlmostEqual(self.network.system_balance(injections), 0.0)


class UncertaintyTests(unittest.TestCase):
    def test_repeatable(self):
        a = monte_carlo_peak_balance(available_capacity_mw=3350, peak_load_mw=3000, draws=100, seed=7)
        b = monte_carlo_peak_balance(available_capacity_mw=3350, peak_load_mw=3000, draws=100, seed=7)
        self.assertEqual(a, b)

    def test_probability_bounds(self):
        result = monte_carlo_peak_balance(available_capacity_mw=3350, peak_load_mw=3000, draws=200, seed=8)
        self.assertGreaterEqual(result["shortfall_probability"], 0)
        self.assertLessEqual(result["shortfall_probability"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
