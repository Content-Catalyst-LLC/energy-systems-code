# Method notes

## Grid balance

At every instant, generation and imports must balance load, exports, storage charging, and system losses closely enough to maintain frequency.

## DC power flow

The companion uses the standard linearized relationship between bus-angle difference and active-power flow. Voltage magnitude and reactive-power effects are outside this approximation.

## Frequency

A simplified frequency-response relationship converts a power imbalance into an indicative steady frequency deviation. It is not a transient dynamic model.

## Storage

Storage dispatch respects power, energy, state-of-charge, and round-trip-efficiency constraints.

## Reliability

Reserve margin is included as a simple capacity indicator. It is not a probabilistic resource-adequacy metric.

## Scope

All numerical data are synthetic and educational.
