# Validation Plan — What Are Energy Systems?

## Scope

The computational companion treats an energy system as a directed, bounded network of resources, conversion assets, networks, storage, end-use technologies, and useful services. It is an educational systems model, not an operational power-flow model.

## Assertions

1. Node and link identifiers are unique.
2. Every link references declared nodes.
3. Efficiencies, availability values, and criticality weights remain in the interval `[0, 1]`.
4. Negative energy, cost, emissions, and capacity inputs are rejected.
5. The teaching graph is acyclic and has a deterministic topological order.
6. Scenario outputs preserve valid efficiency, renewable-share, and critical-service ranges.
7. Monte Carlo outputs are reproducible under a fixed seed.
8. CSV, JSON, SVG, SQL, and optional compiled outputs are nonempty and machine-readable.

## Limitations

The model does not solve alternating-current power flow, unit commitment, market clearing, dynamic stability, lifecycle assessment, or engineering design. Links are declared accounting pathways. Data are synthetic and must not be used for operational, investment, safety-critical, or regulatory decisions.
