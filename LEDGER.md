# Ledger

One entry per pre-registered test, added after the result is in. A seal commit
is the commit that pre-registered the test; it was pushed before the run.
Entries are never edited after the fact, except to fix a typo. Corrections go
in a new entry.

| Version | Question | Seal | Verdict |
|---|---|---|---|
| v0 | Does a torus lattice keep trajectories accurate longer than a degree-matched shuffled graph? (chaotic regime) | `ba5b548`, design agreed in conversation; the file was written up just after the run | **Null** |
| v1 | Same question, calm phase-locked regime, 30 seeds | `ad7d455` | **Null.** Prediction A ruled out, B consistent |
| v2 | Does feedback from an E8-symmetric bulk through the H4 projection suppress phase slips more than random or PCA projections? | `3ba4c29` | **Null.** Prediction A ruled out, B consistent |

## v0: chaotic regime

- **Pre-registration:** [PREREGISTRATION.md](PREREGISTRATION.md)
- **Results:** [results/baseline-v0/summary.md](results/baseline-v0/summary.md)
- **Setup:** 64 nodes, 10 seeds, T = 200, random initial phases.
- **Result:** No cell showed a torus advantage. Leapfrog cells showed the shuffled graph ahead at 2.1–2.3 SE, which is borderline with 10 seeds and shared seeds, so it isn't claimed. The Lyapunov exponent was 0.64 on both graphs, so chaos dominated every arm.
- **Lesson:** In a chaotic regime, structure can't show up in trajectory accuracy. That prompted v1.

## v1: calm, phase-locked regime

- **Pre-registration:** [PREREGISTRATION-v1.md](PREREGISTRATION-v1.md), sealed in `ad7d455` before the run.
- **Results:** [results/v1/summary.md](results/v1/summary.md), commit `23d077a`.
- **Gate:** passed. The Lyapunov exponent was 0.0066 on both graphs, and the largest edge phase difference was 0.59 rad (the limit was π/2).
- **Primary cell (leapfrog, projection off):** torus ÷ shuffled error ratio 1.056, 95% CI [0.986, 1.130]. **Null.**
- **Prediction A (user):** torus 15–25% more accurate, band 0.75–0.85. **Ruled out.**
- **Prediction B (Claude, linear mode theory):** no difference, band 0.95–1.05. **Consistent, not confirmed**, because the interval extends past 1.05.
- **Secondary cells:** all null, with point estimates 1.06–1.10. The cells share seeds, so this is one pattern, not four results. Energy drift ratio 0.997.
- **Lesson:** Near sync, accuracy depends on the graph's frequency spectrum. The lattice's structure gives no advantage over a degree-matched random graph.

## v2: E8 projection feedback and phase slips

- **Pre-registration:** [PREREGISTRATION-v2.md](PREREGISTRATION-v2.md), sealed in `3ba4c29` before the run.
- **Results:** [results/v2/summary.md](results/v2/summary.md).
- **Gates:** all passed.
  - The bulk was on the root shell 74% of the time (required: at least 50%).
  - Feedback raised slips 2.28× over no feedback (required: at least 1.2×).
  - At dt/2, the E8 ÷ random ratio was 0.900, inside the main interval, and the no-feedback slip rate changed by +4%.
- **E8 ÷ random:** 0.947, 95% CI [0.853, 1.051]. **Null.**
- **E8 ÷ PCA:** 1.037, 95% CI [0.966, 1.114]. **Null.** PCA had slightly fewer slips than E8 on average.
- **Refutation standard (E8 must beat both random and PCA):** not met, so the claim is not supported.
- **Prediction A (user):** 20–40% fewer slips, band 0.60–0.80. **Ruled out.**
- **Prediction B (Claude):** 3–20% fewer slips, band 0.80–0.97. **Consistent, not confirmed.** The interval extends past 0.97 and includes 1.
- **Mechanism test:** E8's seeds sit on the same slips-vs-torque-correlation-time trend as the random and PCA seeds. E8's offset from the trend is +0.009 log slips, 95% CI [−0.089, +0.107]. Correlation time accounts for everything E8 does, and no extra geometric effect shows up. E8's torque correlation time (48.2) was only slightly shorter than random's (49.3), less than the bulk-only check had suggested, which is why E8's advantage over random came out small and not significant.
- **Lesson:** Even with an E8-symmetric bulk and the exact H4 projection, the projection acts like any other 4D subspace with the same torque statistics. As with E8-Engine and v0–v1, the structure does not add an effect beyond what its ordinary statistics explain.
