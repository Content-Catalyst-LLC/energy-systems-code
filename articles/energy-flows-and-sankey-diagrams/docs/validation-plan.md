# Validation plan

1. Reject negative or non-finite link values.
2. Reject self-links.
3. Confirm selected transformation, storage, and end-use nodes conserve energy.
4. Confirm width scaling remains proportional to link magnitude.
5. Confirm duplicate-link aggregation preserves total energy.
6. Confirm balance reconciliation preserves composition and equalizes side totals.
7. Confirm deterministic uncertainty results repeat for a fixed seed.
8. Confirm CSV and JSON outputs parse successfully.
9. Confirm the generated SVG is valid text beginning with an SVG root element.
10. Run optional R, Julia, C, and SQLite cross-checks when available.
