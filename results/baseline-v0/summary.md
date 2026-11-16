# Results

N = 64 nodes, dt = 0.05, T = 200, 10 seeds, reference dt/16, tolerance 0.1 rad RMS. Runtime 249 s.

## Primary test: torus vs shuffled, mean valid time

Valid time = first time the run's error against the reference exceeds the tolerance. Higher is better. Verdict uses a 2-standard-error threshold on the difference. Censored = seeds that stayed under the tolerance for the whole run (torus/shuffled); if many are censored, run longer before reading the verdict.

| Integrator | Projection | Torus | Shuffled | Diff ± SE | Verdict | Censored | Reference trusted |
|---|---|---|---|---|---|---|---|
| leapfrog | off | 8.6 | 9.9 | -1.3 ± 0.571 | **shuffled better** | 0/0 | yes |
| leapfrog | on | 8.3 | 9.4 | -1.1 ± 0.522 | **shuffled better** | 0/0 | yes |
| rk4 | off | 19.8 | 20 | -0.2 ± 1.18 | **null** | 0/0 | yes |
| rk4 | on | 21 | 20.1 | 0.9 ± 1.11 | **null** | 0/0 | yes |

## Confound check: how chaotic is each graph?

If one graph is simply less chaotic, every method stays accurate longer on it, whatever the integrator. A valid-time gap that tracks the Lyapunov gap is about the dynamics, not about the numerics.

| Topology | Lyapunov exponent (mean ± sd) | Reference horizon (mean) |
|---|---|---|
| torus | 0.644 ± 0.0305 | 33.8 |
| shuffled | 0.639 ± 0.033 | 34.5 |

## Secondary metrics at final time

Energy drift is per node and is not scored for projection-on runs, which enforce it. Charge drift should be round-off in every arm.

| Topology | Integrator | Projection | Median error | Median energy drift | Max charge drift | Projection failures |
|---|---|---|---|---|---|---|
| torus | leapfrog | off | 2.61 | 0.000283 | 7.11e-14 | 0 |
| torus | leapfrog | on | 2.49 | enforced | 9.95e-14 | 0 |
| torus | rk4 | off | 2.54 | 4.06e-05 | 5.68e-14 | 0 |
| torus | rk4 | on | 2.55 | enforced | 7.11e-14 | 0 |
| shuffled | leapfrog | off | 2.49 | 0.00042 | 1.14e-13 | 0 |
| shuffled | leapfrog | on | 2.54 | enforced | 9.95e-14 | 0 |
| shuffled | rk4 | off | 2.56 | 3.83e-05 | 7.11e-14 | 0 |
| shuffled | rk4 | on | 2.5 | enforced | 7.11e-14 | 0 |
