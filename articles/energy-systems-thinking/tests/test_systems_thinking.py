import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from systems_thinking import Scenario, learning_cost, simulate, rebound, loop_type, monte_carlo

class Tests(unittest.TestCase):
    def scenario(self):
        return Scenario(name="baseline", years=5)
    def test_history_length(self): self.assertEqual(len(simulate(self.scenario())), 6)
    def test_capacity_nonnegative(self): self.assertTrue(all(x[1] >= 0 for x in simulate(self.scenario())))
    def test_learning_double(self): self.assertAlmostEqual(learning_cost(160, 80, 100, .20), 80.0)
    def test_reinforcing(self): self.assertEqual(loop_type([1,-1,-1]), "reinforcing")
    def test_balancing(self): self.assertEqual(loop_type([1,-1,1]), "balancing")
    def test_bad_loop(self):
        with self.assertRaises(ValueError): loop_type([1,0,-1])
    def test_rebound(self): self.assertAlmostEqual(rebound(20,14,15.5)["fraction"], .25)
    def test_constraint(self):
        s = Scenario(name="x", years=1, transmission_limit_gw=2.0)
        h = simulate(s)
        self.assertLessEqual(h[1][4], 2.0)
    def test_retirement_positive(self): self.assertGreater(simulate(self.scenario())[1][5], 0)
    def test_invalid_years(self):
        with self.assertRaises(ValueError): simulate(Scenario(name="x", years=0))
    def test_mc_repeatable(self):
        a = monte_carlo(self.scenario(), draws=50, seed=7)
        b = monte_carlo(self.scenario(), draws=50, seed=7)
        self.assertEqual(a,b)
    def test_mc_ordered(self):
        x = monte_carlo(self.scenario(), draws=100, seed=8)
        self.assertLessEqual(x["p05"], x["p50"])
        self.assertLessEqual(x["p50"], x["p95"])

if __name__ == "__main__": unittest.main(verbosity=2)
