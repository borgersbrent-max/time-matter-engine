# Ledger

One entry per pre-registered test, added after the result is in. A seal commit
is the commit that pre-registered the test; it was pushed before the run.
Entries are never edited after the fact, except to fix a typo. Corrections go
in a new entry.

| Version | Question | Seal | Verdict |
|---|---|---|---|
| v0 | Does a torus lattice keep trajectories accurate longer than a degree-matched shuffled graph? (chaotic regime) | `ba5b548`, design agreed in conversation; the file was written up just after the run | **Null** |
| v1 | Same question, calm phase-locked regime, 30 seeds | `ad7d455` | **Null.** Prediction A ruled out, B consistent |

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
