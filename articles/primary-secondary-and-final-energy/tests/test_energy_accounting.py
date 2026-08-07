from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from energy_accounting.core import (  # noqa: E402
    AccountingChain,
    aggregate_results,
    chain_accounting,
    direct_equivalent_primary,
    energy_balance,
    final_to_useful,
    multistage_efficiency,
    site_to_source,
    substitution_primary,
)
from energy_accounting.uncertainty import monte_carlo_chain  # noqa: E402


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.chain = AccountingChain(
            name="test",
            primary_energy_mwh=100.0,
            conversion_efficiency=0.50,
            delivery_efficiency=0.90,
            end_use_efficiency=0.80,
            service_factor=0.75,
            energy_sector_own_use_fraction=0.05,
            non_energy_use_fraction=0.05,
        )

    def test_chain_values(self):
        result = chain_accounting(self.chain)
        self.assertAlmostEqual(result.transformation_input_mwh, 90.0)
        self.assertAlmostEqual(result.secondary_energy_mwh, 45.0)
        self.assertAlmostEqual(result.final_energy_mwh, 40.5)
        self.assertAlmostEqual(result.useful_energy_mwh, 32.4)
        self.assertAlmostEqual(result.service_energy_equivalent_mwh, 24.3)

    def test_conservation(self):
        self.assertAlmostEqual(chain_accounting(self.chain).residual_mwh, 0.0, places=12)

    def test_invalid_efficiency(self):
        with self.assertRaises(ValueError):
            chain_accounting(AccountingChain("bad", 10, 1.2, 1, 1))

    def test_own_use_and_non_energy_limit(self):
        with self.assertRaises(ValueError):
            chain_accounting(AccountingChain("bad", 10, 1, 1, 1, energy_sector_own_use_fraction=0.7, non_energy_use_fraction=0.5))

    def test_final_to_useful(self):
        self.assertAlmostEqual(final_to_useful(80, 0.75), 60)


class MethodTests(unittest.TestCase):
    def test_direct_equivalent(self):
        self.assertEqual(direct_equivalent_primary(1000), 1000)

    def test_substitution(self):
        self.assertAlmostEqual(substitution_primary(1000, 0.4), 2500)

    def test_site_source(self):
        self.assertAlmostEqual(site_to_source(100, 2.5), 250)

    def test_multistage(self):
        self.assertAlmostEqual(multistage_efficiency([0.9, 0.8, 0.75]), 0.54)

    def test_balance(self):
        balance = energy_balance(100, 20, 5, 10, 65)
        self.assertAlmostEqual(balance.residual_mwh, 0.0)


class AggregateAndUncertaintyTests(unittest.TestCase):
    def test_aggregate(self):
        first = chain_accounting(AccountingChain("a", 100, 0.5, 1, 1))
        second = chain_accounting(AccountingChain("b", 100, 1, 1, 1))
        aggregate = aggregate_results([first, second])
        self.assertAlmostEqual(aggregate["primary_energy_mwh"], 200)
        self.assertAlmostEqual(aggregate["useful_energy_mwh"], 150)

    def test_uncertainty_repeatable(self):
        chain = AccountingChain("u", 100, 0.5, 0.9, 0.8)
        first = monte_carlo_chain(chain, samples=100, seed=7)
        second = monte_carlo_chain(chain, samples=100, seed=7)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
