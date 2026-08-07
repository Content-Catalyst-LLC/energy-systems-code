#!/usr/bin/env python3
from electricity_grids import dc_line_flow_mw, frequency_deviation_hz, reserve_margin

print("Line flow:", dc_line_flow_mw(0.04, 0.01, 0.10, 100.0), "MW")
print("Reserve margin:", reserve_margin(3350, 3000))
print("Frequency deviation:", frequency_deviation_hz(450, 7500), "Hz")
