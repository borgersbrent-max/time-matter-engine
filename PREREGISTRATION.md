# Pre-registration: v0 control grid

The design, metric and success test were agreed before the first full run and
implemented in code before it. This file was written up right after that run,
without changing any of them. From now on, changing anything below after
seeing results means starting a new, separately labelled version.

## Hypothesis

Explicit structure, here a 2D torus lattice, keeps long-horizon rollouts closer
to the true trajectory than a random graph with the same degree sequence, when
the integrator and projection are the same.

## System

Coupled phase oscillators with a passive conserved charge on a 4-regular graph,
N = 64 (8 x 8). See `tme/dynamics.py`.

## Grid (8 arms)

- Integrator: leapfrog (symplectic) or RK4
- Projection: off, or rescale momenta to the initial energy after every step
- Topology: 8 x 8 torus, or the torus shuffled once by degree-preserving double-edge swaps (a new shuffle per seed)

Each seed uses the same initial conditions for both topologies.

## Primary metric

**Valid time**: the first time a run's error against the reference goes above
0.1 rad RMS (phases wrapped, momenta included). The reference is RK4 at dt/16
on the same graph from the same start. It counts as trusted only while it
agrees with an RK4 run at dt/32 to within 0.01.

## Success test

Within each integrator x projection cell, the torus's mean valid time must be
higher than the shuffled graph's by more than 2 standard errors of the
difference, over 10 seeds. Anything else is a null result, and we report it as
one.

## Secondary metrics, not tests

- Energy drift per node, only for projection-off arms
- Total charge drift; this is a sanity check and should be round-off
- Largest Lyapunov exponent of each topology. If one graph is simply less
  chaotic, every method stays accurate longer on it, which would explain a
  valid-time gap without the numerics playing any part.

## Exploratory, not part of the test

Re-shuffling the graph every step. Not implemented in v0.
