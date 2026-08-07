from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from energy_systems_foundation.model import (
    EnergyLink,
    EnergyNode,
    NodeKind,
    build_system,
    run_scenario,
)
from energy_systems_foundation.scenarios import transform_system
from energy_systems_foundation.uncertainty import monte_carlo_system_efficiency


class ModelTests(unittest.TestCase):
    def setUp(self):
        nodes = [
            EnergyNode("resource", "Resource", NodeKind.RESOURCE, "fuel"),
            EnergyNode("converter", "Converter", NodeKind.CONVERSION, "electricity"),
            EnergyNode("service", "Service", NodeKind.SERVICE, "service", criticality=1.0),
        ]
        links = [
            EnergyLink("a", "resource", "converter", 100.0, 0.5, 100.0, 10.0, 1.0),
            EnergyLink("b", "converter", "service", 50.0, 0.8, 0.0, 2.0, 1.0),
        ]
        self.system = build_system(nodes, links)

    def test_topological_order(self):
        self.assertEqual(self.system.topological_order(), ("resource", "converter", "service"))

    def test_link_accounting(self):
        link = self.system.links[0]
        self.assertAlmostEqual(link.output_mwh, 50.0)
        self.assertAlmostEqual(link.loss_mwh, 50.0)
        self.assertAlmostEqual(link.emissions_kg_co2e, 10000.0)

    def test_scenario_efficiency_and_conservation(self):
        result = run_scenario("test", self.system, set())
        self.assertAlmostEqual(result.primary_input_mwh, 100.0)
        self.assertAlmostEqual(result.useful_service_mwh_equivalent, 40.0)
        self.assertAlmostEqual(result.overall_primary_to_service_efficiency, 0.4)
        self.assertAlmostEqual(result.conservation_residual_mwh, 0.0)

    def test_upstream_shortage_propagates(self):
        stressed = transform_system(self.system, availability_overrides={"a": 0.5})
        result = run_scenario("stress", stressed, set())
        self.assertAlmostEqual(result.primary_input_mwh, 50.0)
        self.assertAlmostEqual(result.useful_service_mwh_equivalent, 20.0)
        self.assertAlmostEqual(result.unavailable_energy_mwh, 50.0)
        self.assertGreater(result.unserved_service_mwh_equivalent, 0.0)

    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):
            build_system(
                self.system.nodes,
                list(self.system.links) + [EnergyLink("c", "service", "resource", 1.0, 1.0)],
            )

    def test_invalid_efficiency(self):
        with self.assertRaises(ValueError):
            EnergyLink("bad", "resource", "service", 1.0, 1.1)


class ScenarioTests(unittest.TestCase):
    def setUp(self):
        nodes = [
            EnergyNode("sun", "Sun", NodeKind.RESOURCE, "solar"),
            EnergyNode("plant", "Plant", NodeKind.CONVERSION, "electricity"),
            EnergyNode("service", "Service", NodeKind.SERVICE, "service", criticality=0.8),
        ]
        links = [
            EnergyLink("resource", "sun", "plant", 100.0, 0.25),
            EnergyLink("service", "plant", "service", 25.0, 0.8),
        ]
        self.system = build_system(nodes, links)

    def test_efficiency_improvement(self):
        base = run_scenario("base", self.system, {"sun"})
        improved = run_scenario(
            "improved",
            transform_system(self.system, efficiency_multiplier=1.1),
            {"sun"},
        )
        self.assertGreater(improved.useful_service_mwh_equivalent, base.useful_service_mwh_equivalent)

    def test_renewable_share(self):
        result = run_scenario("base", self.system, {"sun"})
        self.assertAlmostEqual(result.renewable_input_share, 1.0)

    def test_uncertainty_repeatable(self):
        first = monte_carlo_system_efficiency(self.system, {"sun"}, iterations=200, seed=7)
        second = monte_carlo_system_efficiency(self.system, {"sun"}, iterations=200, seed=7)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
