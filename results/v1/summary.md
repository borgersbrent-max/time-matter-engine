# v1 results: calm, phase-locked regime

N = 64 nodes, dt = 0.05, T = 500, 30 seeds, initial phase spread 0.1, momentum spread 0.1, reference dt/8. Runtime 752 s.

## Gate: is the regime actually calm?

Both topologies must have Lyapunov exponent < 0.05 and every edge's phase difference must stay below π/2 for the whole reference run. If this fails, the run is invalid, not a null.

| Topology | Lyapunov (mean) | Max edge phase difference | Passed |
|---|---|---|---|
| torus | 0.00661 | 0.593 rad | yes |
| shuffled | 0.0066 | 0.572 rad | yes |

**Gate passed.**

## Primary test: leapfrog, projection off

Ratio = geometric mean over seeds of (torus error ÷ shuffled error) at the final time, paired by seed. Below 1 means the torus is more accurate.

**Ratio 1.056, 95% CI [0.986, 1.130]: null.**

| Prediction | Band | Result |
|---|---|---|
| Torus 15–25% more accurate | 0.75–0.85 | ruled out |
| Linear mode theory: no difference | 0.95–1.05 | consistent |

## All four cells

Secondary cells use Bonferroni-corrected 98.33% intervals.

| Integrator | Projection | Error ratio | CI | Verdict | Energy drift ratio | Reference accurate enough |
|---|---|---|---|---|---|---|
| leapfrog (primary) | off | 1.056 | [0.986, 1.130] | **null** | 0.997 [0.835, 1.190] | yes |
| leapfrog | on | 1.101 | [0.997, 1.216] | **null** | enforced | yes |
| rk4 | off | 1.076 | [0.979, 1.181] | **null** | 1.079 [0.957, 1.217] | yes |
| rk4 | on | 1.078 | [0.977, 1.190] | **null** | enforced | yes |

## Graph spectra

| Topology | Largest Laplacian eigenvalue | Spectral gap |
|---|---|---|
| torus | 8 | 0.586 |
| shuffled | 7.35 | 0.725 |

## Median final error per arm

| Topology | Integrator | Projection | Median error | Median energy drift | Max charge drift |
|---|---|---|---|---|---|
| torus | leapfrog | off | 0.112 | 2.34e-05 | 1.71e-13 |
| torus | leapfrog | on | 0.125 | enforced | 1.56e-13 |
| torus | rk4 | off | 0.000258 | 8.8e-06 | 1.14e-13 |
| torus | rk4 | on | 0.000338 | enforced | 1.42e-13 |
| shuffled | leapfrog | off | 0.102 | 2.37e-05 | 2.7e-12 |
| shuffled | leapfrog | on | 0.11 | enforced | 2.79e-12 |
| shuffled | rk4 | off | 0.000255 | 7.88e-06 | 1.48e-12 |
| shuffled | rk4 | on | 0.000324 | enforced | 1.48e-12 |
