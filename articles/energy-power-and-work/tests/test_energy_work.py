from __future__ import annotations
import math, sys, unittest
from datetime import datetime, timedelta
from pathlib import Path
PYTHON_DIR = Path(__file__).resolve().parents[1] / "python"; sys.path.insert(0, str(PYTHON_DIR))
from energy_work.core import (ConversionStage, PowerObservation, elastic_potential_energy_j,
    gravitational_potential_energy_j, integrate_power_wh, kinetic_energy_j, load_statistics,
    mechanical_work_j, run_conversion_chain, run_scenario)
from energy_work.uncertainty import propagate_efficiency_uncertainty
from energy_work.units import convert_energy, convert_power

class PhysicsTests(unittest.TestCase):
    def test_work(self): self.assertAlmostEqual(mechanical_work_j(10, 3), 30)
    def test_perpendicular_work(self): self.assertAlmostEqual(mechanical_work_j(10, 3, 90), 0, places=10)
    def test_kinetic(self): self.assertAlmostEqual(kinetic_energy_j(2, 4), 16)
    def test_gravity(self): self.assertAlmostEqual(gravitational_potential_energy_j(1, 1), 9.80665)
    def test_elastic(self): self.assertAlmostEqual(elastic_potential_energy_j(100, .2), 2)

class ConversionTests(unittest.TestCase):
    def test_units(self):
        self.assertEqual(convert_energy(1, "kWh", "J"), 3600000)
        self.assertEqual(convert_power(2.5, "MW", "kW"), 2500)
        self.assertAlmostEqual(convert_energy(convert_energy(12.5, "MWh", "GJ"), "GJ", "MWh"), 12.5)
    def test_chain_conservation(self):
        result = run_conversion_chain(100, [ConversionStage("a", .9), ConversionStage("b", .8)])
        self.assertAlmostEqual(result.useful_output_kwh, 72); self.assertAlmostEqual(result.losses_kwh, 28)
        self.assertAlmostEqual(result.input_kwh, result.useful_output_kwh + result.losses_kwh)
    def test_invalid_efficiency(self):
        with self.assertRaises(ValueError): ConversionStage("bad", 1.1)

class TimeSeriesTests(unittest.TestCase):
    def setUp(self):
        start = datetime(2026, 1, 1)
        self.rows = [PowerObservation(start, 100), PowerObservation(start + timedelta(hours=1), 200),
                     PowerObservation(start + timedelta(hours=2), 100)]
    def test_integration(self): self.assertAlmostEqual(integrate_power_wh(self.rows), 300000)
    def test_stats(self):
        stats = load_statistics(self.rows)
        self.assertAlmostEqual(stats["energy_kwh"], 300); self.assertAlmostEqual(stats["load_factor"], .75)
    def test_scenario_residual(self):
        result = run_scenario("test", self.rows, 1, [ConversionStage("load", .9)])
        self.assertTrue(math.isclose(result.conservation_residual_kwh, 0, abs_tol=1e-12))

class UncertaintyTests(unittest.TestCase):
    def test_repeatable(self):
        first = propagate_efficiency_uncertainty(1000, [.95, .90], [.01, .02], 1000, 42)
        second = propagate_efficiency_uncertainty(1000, [.95, .90], [.01, .02], 1000, 42)
        self.assertEqual(first, second); self.assertLess(first.p05_useful_energy_kwh, first.p50_useful_energy_kwh)
        self.assertLess(first.p50_useful_energy_kwh, first.p95_useful_energy_kwh)

if __name__ == "__main__": unittest.main()
