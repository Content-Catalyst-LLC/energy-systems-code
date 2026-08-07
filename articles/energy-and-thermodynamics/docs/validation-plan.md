# Validation plan

1. Confirm absolute-temperature checks and hot-reservoir ordering.
2. Confirm first-law residuals remain at numerical zero.
3. Confirm actual efficiency never exceeds the Carnot limit.
4. Confirm entropy generation is nonnegative.
5. Confirm heat-pump COP responds correctly to temperature lift.
6. Confirm multistage efficiency equals the product of stage efficiencies.
7. Confirm storage input equals useful output plus loss.
8. Confirm Monte Carlo output is deterministic for a fixed seed.
9. Cross-check baseline calculations in Python, R, Julia, and C when available.
10. Validate CSV, JSON, and SVG outputs before commit.
