# Method notes

## Flow representation

Each link is represented as a directed transfer with a source, target, energy value, category, and note. Visual widths are proportional to a common scale factor.

## Conservation

For internal accounting nodes, inflow should equal outflow within a stated numerical tolerance. External sources and sinks represent the system boundary and do not individually require zero residual.

## Storage

Storage is modeled explicitly as a charging flow, a return flow, and a loss flow. Feedback links make the network cyclic, which is valid for accounting but requires care in graph algorithms.

## Reconciliation

The included reconciliation utility rescales inflow and outflow totals toward their average while preserving within-side composition. It is a teaching method, not a replacement for statistical-agency balancing procedures.

## Scope limits

The package is a reproducible educational companion. It does not replace official energy balances, production-grade Sankey layout engines, power-system dispatch models, lifecycle assessment, or input-output analysis.
