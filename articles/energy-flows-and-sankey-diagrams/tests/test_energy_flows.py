from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from energy_flows import (
    Flow,
    FlowNetwork,
    aggregate_links,
    monte_carlo_network,
    normalize_widths,
    reconcile_balanced_node,
)


class FlowTests(unittest.TestCase):
    def test_invalid_negative_flow(self):
        with self.assertRaises(ValueError):
            Flow("A", "B", -1).validated()

    def test_self_link_rejected(self):
        with self.assertRaises(ValueError):
            Flow("A", "A", 1).validated()

    def test_node_balance(self):
        net = FlowNetwork([
            Flow("A", "B", 10),
            Flow("B", "C", 7),
            Flow("B", "Loss", 3),
        ])
        self.assertAlmostEqual(net.balance("B").residual_mwh, 0)

    def test_assert_balanced_rejects_error(self):
        net = FlowNetwork([Flow("A", "B", 10), Flow("B", "C", 9)])
        with self.assertRaises(ValueError):
            net.assert_balanced()

    def test_boundary_residual_balanced(self):
        net = FlowNetwork([
            Flow("A", "B", 10),
            Flow("B", "C", 7),
            Flow("B", "Loss", 3),
        ])
        self.assertAlmostEqual(net.boundary_residual(), 0)


class UtilityTests(unittest.TestCase):
    def test_aggregate_links(self):
        flows = aggregate_links([
            Flow("A", "B", 2, "x"),
            Flow("A", "B", 3, "x"),
            Flow("A", "B", 4, "y"),
        ])
        values = sorted(f.value_mwh for f in flows)
        self.assertEqual(values, [4.0, 5.0])

    def test_normalize_widths(self):
        widths = normalize_widths([Flow("A", "B", 10), Flow("C", "D", 5)], max_width=20)
        self.assertAlmostEqual(widths[("A", "B")], 20)
        self.assertAlmostEqual(widths[("C", "D")], 10)

    def test_zero_width(self):
        widths = normalize_widths([Flow("A", "B", 0), Flow("C", "D", 5)])
        self.assertEqual(widths[("A", "B")], 0)

    def test_reconciliation_conserves_target(self):
        ins, outs = reconcile_balanced_node({"a": 100, "b": 20}, {"x": 110})
        self.assertAlmostEqual(sum(ins.values()), sum(outs.values()))

    def test_reconciliation_preserves_ratios(self):
        ins, _ = reconcile_balanced_node({"a": 100, "b": 20}, {"x": 110})
        self.assertAlmostEqual(ins["a"] / ins["b"], 5)


class UncertaintyTests(unittest.TestCase):
    def test_repeatable(self):
        flows = [Flow("A", "B", 10), Flow("B", "C", 10)]
        a = monte_carlo_network(flows, draws=50, seed=7)
        b = monte_carlo_network(flows, draws=50, seed=7)
        self.assertEqual(a, b)

    def test_draw_count(self):
        result = monte_carlo_network([Flow("A", "B", 10)], draws=25)
        self.assertEqual(result["draws"], 25.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
