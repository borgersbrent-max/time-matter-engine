# Structure without advantage: three controlled nulls

**A negative-results note from time-matter-engine.** Draft, 16 November 2026.

## Summary

We tested three times whether built-in geometric structure gives a simulated
system an advantage over a matched control:

1. A 2D torus lattice against a degree-matched random graph, in a chaotic regime (v0).
2. The same comparison in a calm, phase-locked regime (v1).
3. Feedback through the E8 → H4 projection, from a bulk with full E8 lattice symmetry, against random and PCA projections of the same rank (v2).

All three results are null. In every case the outcome is accounted for by an
ordinary statistic of the system: chaos in v0, the graph's frequency spectrum
in v1, and the feedback torque's correlation time in v2. None of the
structures had an effect beyond that statistic. v1 and v2 were pre-registered,
with the design, metrics, success tests and predictions committed and pushed
to GitHub before the runs.

## Background

The E8-Engine repository asked a related question informally: is E8-lattice
quantised attention better than a random codebook of the same size? It was not
pre-registered, and its results are not in the repository. Its author reports
they were not useful, so it is mentioned here only as motivation. The present
work was set up to ask the question under controls fixed in advance.

## Shared method

- **Matched controls.** Every structured arm was compared with a control that
  matches it on the obvious statistics:
  - v0, v1: the same degree for every node, and the same number of edges.
  - v2: the same rank of projection, and torque normalised to the same mean and spread.
- **Paired seeds.** Within a seed, the arms share initial conditions (v0, v1),
  and the bulk trajectory and noise (v2). Comparisons are made seed by seed.
- **Gates.** Each run had validity checks set in advance. A failed check would
  have made the run invalid, rather than a null.
- **Predictions with bands.** For v1 and v2, the user and Claude each sealed a
  predicted ratio band. A prediction counts as:
  - **confirmed** if the 95% interval lies inside its band
  - **consistent** if the interval overlaps its band
  - **ruled out** if the interval misses its band
- **Seals.** A seal is a pre-registration commit pushed to GitHub before the
  run. Its push time is the timestamp that counts.

Code, data and every pre-registration are in this repository. Each result
reruns with one command (listed at the end).

## v0: torus vs shuffled graph, chaotic regime

**System.** Coupled phase oscillators (H = Σp²/2 − K Σ cos(θᵢ − θⱼ)), carrying a
passive conserved charge, on a 64-node 4-regular graph. 8 arms:
- integrator: leapfrog or RK4
- energy projection: on or off
- topology: torus or degree-preserving shuffle

**Score.** Valid time: how long each run stays within 0.1 rad RMS of an RK4
reference at dt/16. 10 seeds, T = 200.

**Result.** No cell showed a torus advantage. In the two leapfrog cells, the
shuffled graph was ahead by 2.1–2.3 SE. That's borderline with 10 shared
seeds, and we don't claim it. Both graphs had Lyapunov exponent ≈ 0.64, so
every arm lost the true trajectory by t ≈ 30, whatever its integrator or graph.

**Reading.** In a chaotic regime, structure cannot show up in trajectory
accuracy. This is a design lesson more than a finding, and it motivated v1.

## v1: torus vs shuffled graph, calm regime

**Change.** Initial states near synchronisation (phase and momentum spread
0.1), 30 seeds, T = 500.

**Gate.** Passed. The Lyapunov exponent was 0.0066 on both graphs (100× lower
than v0), and the largest edge phase difference was 0.59 rad (limit: π/2).

**Primary result (leapfrog, no projection).** Torus ÷ shuffled final error
was 1.056, 95% CI [0.986, 1.130]: **null**. The three secondary cells are also
null. Their point estimates are 1.08–1.10, so the torus is, if anything,
slightly worse.

**Predictions.**
- **User:** torus 15–25% more accurate, band 0.75–0.85. **Ruled out.**
- **Claude:** linear mode theory, no difference, band 0.95–1.05. **Consistent.**

**Reading.** Near sync the system is a network of harmonic oscillators, and
integration error depends on the graph Laplacian's spectrum. The torus's
higher top eigenvalue (8 vs 7.35) is offset by the random graph having more
modes near the top of its spectrum. The lattice's structure adds nothing
beyond its spectrum.

## v2: E8 projection feedback

**System.** Same 8 × 8 torus.
- Each node carries a bulk vector **u** ∈ ℝ⁸ in a potential with full E8
  lattice symmetry: V = −(V₀/120) Σ cos(2π **r**·**u**) over the root pairs,
  plus a Weyl-invariant trap.
- The bulk drives the node's phase through a torque proportional to |P**u**|².
- P is one of four choices:
  - the exact H4 projection, verified to send the 240 roots onto two 600-cells with radius ratio φ
  - a Haar-random 4D subspace
  - the bulk's top-4 PCA subspace
  - none (no feedback)
- Torque is normalised per arm to the same mean and spread.

**Score.** Phase slips (changes in winding number around the torus's 16
loops), with seeds paired. 30 seeds, T = 1000.

**Refutation standard (the user's).** E8 must have fewer slips than both random and PCA.

**Gates.** All passed:
- The bulk was on the root shell 74% of the time (required ≥ 50%).
- Feedback raised slips 2.28× over no feedback (required ≥ 1.2×).
- A rerun at dt/2 gave an E8 ÷ random ratio of 0.900, inside the main interval.
- The no-feedback slip rate changed by +4% at dt/2 (allowed: ±25%).

**Results.**

| Comparison | Ratio | 95% CI | Verdict |
|---|---|---|---|
| E8 ÷ random | 0.947 | [0.853, 1.051] | null |
| E8 ÷ PCA | 1.037 | [0.966, 1.114] | null |

**Predictions.**
- **User:** 20–40% fewer slips, band 0.60–0.80. **Ruled out.**
- **Claude:** 3–20% fewer slips, band 0.80–0.97. **Consistent.**

**Mechanism test.** Fit log(slips) against torque correlation time on the
random and PCA seeds. E8's seeds lie on that trend: offset +0.009 log slips,
95% CI [−0.089, +0.107]. The torque's correlation time accounts for E8's
result, with nothing left over for geometry.

**Reading.** A potential with E8 symmetry looks the same in every direction
up to 6th order, because the Weyl group has no invariant polynomials between
degrees 2 and 8. So low-order statistics cannot tell one projection from
another. Even when the bulk hopped between roots, which made the H4
projection's output measurably different in distribution, slips responded
only to how long the torque remembered its past, and E8's memory was
ordinary.

## Limitations

- **The seals are uneven.** v1 and v2 were sealed before running. v0's design
  was agreed before its run, but its pre-registration file was written after.
  E8-Engine was not pre-registered at all.
- **One prediction was revised before sealing.** In v2, Claude changed its
  prediction from "no difference" to "3–20% fewer slips" after a bulk-only
  check, and before the seal. That check measured no slips. The change is
  disclosed in the pre-registration. The user's v2 prediction came before that
  check.
- **Tuning before the seal.** v2's bulk temperature, noise level and feedback
  strength were set before the seal. Each was set using only bulk statistics,
  the no-feedback arm, or a coordinate-axes projection that isn't tested.
  Other choices could behave differently. Any such variant needs its own seal.
- **Power.** The intervals are about ±7% (v1) and ±10% (v2). Effects smaller
  than that are not excluded. The larger effects both of the user's
  predictions specified are excluded.
- **Scope.** These are small toy models: 64 nodes, one coupling form per
  version, fixed parameters. The nulls apply to these models, not to every
  possible use of lattice or E8 structure.
- **No independent replication.** The same two parties designed, ran and
  analysed every test. Timestamps rely on GitHub push times; commit dates can
  be edited.

## Conclusion

In three controlled tests, built-in geometric structure (a lattice, and the E8
root system with its H4 projection) gave no advantage over controls matched on
ordinary statistics. Wherever a difference appeared, an ordinary statistic
explained it: chaos, frequency spectrum, or correlation time. Claims of a
structural advantage in models like these should be tested against the same
matched controls, with predictions sealed before the run.

## Reproducing

| Version | Seal | Results commit | Command |
|---|---|---|---|
| v0 | `ba5b548` (written up after the run) | `ba5b548` | `python run_grid.py --name baseline-v0` |
| v1 | `ad7d455` | `23d077a` | `python run_grid.py --preset v1 --name v1` |
| v2 | `3ba4c29` | `a57433e` | `python run_v2.py --name v2` |

Results: `results/<name>/summary.md`. Log: [LEDGER.md](LEDGER.md).
