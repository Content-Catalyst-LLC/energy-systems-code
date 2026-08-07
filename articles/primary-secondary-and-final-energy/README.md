# Primary, Secondary, and Final Energy

Status: computational companion implemented

This package provides transparent energy-accounting workflows for tracing resource inputs through conversion, delivery, end use, and service-equivalent output. It keeps physical stages and accounting conventions explicit so that totals from different datasets or institutions are not compared without checking their boundaries and methods.

## Included analysis

- Primary, secondary, final, useful, and service-equivalent energy chains
- Energy-sector own use and non-energy use
- Transformation, delivery, and end-use losses
- Primary-to-final, primary-to-useful, and primary-to-service efficiencies
- Site-energy and source-energy conversion
- Direct-equivalent and substitution primary-energy methods
- Aggregate balance and residual checks
- Deterministic uncertainty analysis
- Cross-language Python, R, Julia, C, and SQL examples
- Machine-readable CSV and JSON outputs plus an SVG figure

## Run

```bash
./run_all.sh
```

The core Python workflow requires Python 3.10 or later and uses only the standard library. R, Julia, C, and SQLite workflows run automatically when those tools are installed and otherwise skip cleanly.

## Interpretation requirement

Energy totals are meaningful only when the system boundary, carrier definitions, treatment of non-combustible electricity, own use, non-energy use, losses, and statistical conventions are documented. The direct-equivalent and substitution methods are both included to demonstrate how methodology can change reported primary-energy totals without changing physical electricity generation.
