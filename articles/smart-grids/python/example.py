#!/usr/bin/env python3
from smart_grids import (
    annual_energy_reduction_mwh,
    charging_power_mw,
    demand_response_net_load,
    flisr_customer_hours_avoided,
)

print("Unmanaged EV:", charging_power_mw(10000, 14, 2), "MW")
print("Managed EV:", charging_power_mw(10000, 14, 7), "MW")
print("Demand-response net:", demand_response_net_load(85, 12), "MW")
print("Volt/VAR savings:", annual_energy_reduction_mwh(10, 0.012, 4000), "MWh")
print("FLISR benefit:", flisr_customer_hours_avoided(9800, 90, 2), "customer-hours")
