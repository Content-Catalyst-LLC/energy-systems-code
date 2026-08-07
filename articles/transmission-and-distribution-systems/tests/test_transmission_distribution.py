from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from transmission_distribution import (
    ExpansionOption,
    HostingCase,
    congestion_cost,
    evaluate_hosting_case,
    feeder_utilization,
    hosting_headroom_mw,
    rank_expansion_options,
    three_phase_current_a,
    three_phase_loss_kw,
    transformer_loading,
    voltage_drop_percent,
)


class CoreTests(unittest.TestCase):
    def test_high_voltage_reduces_current(self):
        i115 = three_phase_current_a(500, 115)
        i345 = three_phase_current_a(500, 345)
        self.assertLess(i345, i115)
        self.assertAlmostEqual(i115 / i345, 3.0)

    def test_article_loss_example(self):
        self.assertAlmostEqual(three_phase_loss_kw(800, 0.08), 153.6)

    def test_feeder_utilization(self):
        self.assertAlmostEqual(feeder_utilization(9.6, 12.0), 0.8)

    def test_transformer_loading(self):
        self.assertAlmostEqual(transformer_loading(510, 500), 1.02)

    def test_article_congestion_cost(self):
        self.assertAlmostEqual(congestion_cost(200, 85, 30), 11000.0)

    def test_voltage_drop_positive(self):
        self.assertGreater(
            voltage_drop_percent(300, 0.15, 0.10, 13800, 0.95),
            0.0,
        )

    def test_invalid_power_factor(self):
        with self.assertRaises(ValueError):
            three_phase_current_a(10, 13.8, 0.0)


class HostingTests(unittest.TestCase):
    def test_headroom(self):
        self.assertAlmostEqual(hosting_headroom_mw(12, 9.6, 1.0), 2.4)

    def test_violation_detection(self):
        result = evaluate_hosting_case(
            HostingCase(
                "test",
                feeder_rating_mva=10,
                base_peak_mva=8,
                added_load_mw=3,
                added_generation_mw=0,
                power_factor=1.0,
            )
        )
        self.assertTrue(result["thermal_violation"])

    def test_generation_can_reduce_net_peak(self):
        result = evaluate_hosting_case(
            HostingCase(
                "test",
                feeder_rating_mva=10,
                base_peak_mva=8,
                added_load_mw=0,
                added_generation_mw=2,
                power_factor=1.0,
            )
        )
        self.assertAlmostEqual(result["net_peak_mw"], 6.0)


class PlanningTests(unittest.TestCase):
    def test_rank_returns_all_options(self):
        options = [
            ExpansionOption("A", 10, 5, 100, 1.0, 2),
            ExpansionOption("B", 5, 4, 200, 0.5, 1),
        ]
        self.assertEqual(len(rank_expansion_options(options)), 2)

    def test_rank_sorted_descending(self):
        options = [
            ExpansionOption("A", 10, 5, 100, 1.0, 2),
            ExpansionOption("B", 5, 4, 200, 0.5, 1),
        ]
        ranked = rank_expansion_options(options)
        self.assertGreaterEqual(ranked[0]["score"], ranked[1]["score"])

    def test_invalid_option(self):
        with self.assertRaises(ValueError):
            rank_expansion_options([
                ExpansionOption("bad", -1, 5, 0, 0, 1),
            ])


if __name__ == "__main__":
    unittest.main(verbosity=2)
