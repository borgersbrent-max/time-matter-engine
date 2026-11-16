# Pre-registration: v1, calm phase-locked regime

Committed and pushed before any v1 run. The push time on GitHub is the seal.
The only things run before the seal were the unit tests and a 3-seed, 16-node,
T = 10 smoke test of the pipeline. Their numbers are not v1 results and are
not used.

## Why v1

v0 ran in a chaotic regime (Lyapunov exponent about 0.64 on both graphs).
There, error grows like e^(λt) and erases any difference between methods or
graphs by t ≈ 30, so v0 tested chaos, not structure. v1 starts near the
synchronised state, where the dynamics are close to linear and error builds up
from the integrator alone.

## Setup (preset `v1` in `tme/experiment.py`)

- Same model, same 8 arms as v0: {leapfrog, RK4} × {projection off, on} × {8 × 8 torus, degree-preserving single shuffle}
- Initial phases: normal, std 0.1, mean removed. Initial momenta: normal, std 0.1, mean removed.
- dt = 0.05, 10,000 steps (T = 500), **30 seeds**. Seed s uses the same initial conditions on both graphs; each seed gets its own shuffle.
- Reference: RK4 at dt/8, checked against RK4 at dt/16.

Run with `python run_grid.py --preset v1 --name v1`.

## Gate: the regime must actually be calm

For both topologies, the mean Lyapunov exponent must be below 0.05 (v0 was
0.64), and no edge's phase difference may reach π/2 at any checkpoint of the
reference run (no phase slips). **If the gate fails, the run is invalid, not a
null**, and v1 is redesigned under a new label.

## Primary test

Cell: **leapfrog, projection off**. Metric: RMS trajectory error against the
reference at T = 500, the same error as in v0.

Statistic: the per-seed log of (torus error ÷ shuffled error), paired by seed.
We report its geometric-mean ratio with a 95% t-interval.

- CI entirely below 1: **torus better**
- CI entirely above 1: **shuffled better**
- otherwise: **null**

A cell's verdict only counts if the reference is accurate enough: its own
final error must be below 1% of the smallest final error it scores in that
cell.

## Secondary tests

The other three cells, with the same statistic and Bonferroni-corrected
98.33% intervals. Also, for projection-off cells, the same paired ratio on
final energy drift, reported but not used for a verdict.

## Predictions, sealed

Each prediction is scored on the primary cell's 95% interval:

- **confirmed** if the interval lies inside the band
- **consistent** if it overlaps the band
- **ruled out** if it misses the band

**Prediction A (user): the torus is 15–25% more accurate.** Band: ratio 0.75–0.85, and the interval must exclude 1.
The argument: on the torus, collective modes propagate coherently thanks to
translational invariance and uniform coordination. On the shuffled graph,
local clustering anomalies and dead ends scatter and trap phase gradients,
which concentrates stress and speeds up error growth.

**Prediction B (Claude, linear mode theory): no difference.** Band: 0.95–1.05.
Near sync, the system is a network of harmonic oscillators with frequencies
ω_k = √(K λ_k), where λ_k are the eigenvalues of the graph Laplacian.
Leapfrog's phase error in each mode grows like ω_k³ dt² t, so the total error
depends only on the graph's spectrum and on how strongly each mode starts out
excited. The spectra were computed from the 30 v1 graphs before the seal,
without running any dynamics:

- Torus: λ_max = 8 exactly, spectral gap 0.586.
- Shuffled: λ_max = 7.35 ± 0.06, gap 0.73 ± 0.07.

The torus's higher top frequency is offset by the shuffled graph having more
modes near the top of its range. With the initial excitation above, this
predicts a ratio of 1.00 for leapfrog and 1.02 for RK4.

A ratio well away from 1 would mean something beyond linear mode theory is
happening, such as nonlinear coupling between modes or the localisation and
trapping effects that Prediction A describes.

## Planned follow-up (v1b, not run as part of v1)

Prediction A adds that any torus advantage disappears above a critical energy
density, where topological defects unbind. v1b will sweep the initial phase
spread, from 0.1 up to fully random phases (the v0 setting), on the primary
cell, and pre-register its own thresholds before it runs.
