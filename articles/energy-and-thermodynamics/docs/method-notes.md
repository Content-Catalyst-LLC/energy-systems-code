# Method notes

## Sign convention

The first-law helper uses `ΔU = Q - W`, where heat entering the system is positive and work performed by the system is positive. Other disciplines may use different sign conventions; comparisons must align conventions first.

## Heat engines

The reversible temperature limit is represented by the Carnot efficiency. Actual efficiency is modeled as a specified fraction of that limit. This separates the temperature-bound opportunity from practical irreversibility without claiming to reproduce a specific turbine, working fluid, or cycle configuration.

## Entropy and irreversibility

Entropy generation is calculated from reservoir heat transfers. Negative entropy generation is rejected because it would violate the second law under the stated model boundary.

## Exergy

Heat exergy is referenced to an ambient temperature. Changing the reference environment changes the calculated exergy and must be documented.

## Heat pumps and storage

Heat-pump COP is represented as a fraction of the reversible heating COP. Thermal storage separates charge loss, standby loss, and discharge loss so that round-trip efficiency remains auditable.

## Scope limits

The package uses constant reservoir temperatures and does not calculate real-fluid properties, phase equilibria, pressure drops, equipment geometry, transient control, or safety margins. Those require specialized property libraries and engineering models.
