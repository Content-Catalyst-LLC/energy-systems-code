#!/usr/bin/env python3
"""Minimal example used in the article."""

from energy_flows import Flow, FlowNetwork

network = FlowNetwork([
    Flow("Fuel", "Power plant", 100.0),
    Flow("Power plant", "Electricity", 42.0),
    Flow("Power plant", "Generation losses", 58.0, "loss"),
])
network.assert_balanced()
print(network.balance("Power plant"))
