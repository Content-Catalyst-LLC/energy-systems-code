#!/usr/bin/env python3
"""Small article example: one transparent energy chain."""

from energy_accounting import AccountingChain, chain_accounting

chain = AccountingChain(
    name="gas_to_useful_heat",
    primary_energy_mwh=100.0,
    conversion_efficiency=0.96,
    delivery_efficiency=0.98,
    end_use_efficiency=0.88,
    service_factor=0.92,
    energy_sector_own_use_fraction=0.02,
)
result = chain_accounting(chain)
print(f"final_energy_mwh={result.final_energy_mwh:.3f}")
print(f"useful_energy_mwh={result.useful_energy_mwh:.3f}")
print(f"service_equivalent_mwh={result.service_energy_equivalent_mwh:.3f}")
