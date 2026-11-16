# time-matter-engine

A sandbox for testing whether structure in a simulation's graph improves long-horizon numerical accuracy. Every test runs against a randomised control from the start.

The first version (v0) simulates coupled phase oscillators that carry a conserved charge on a 4-regular graph. It compares a 2D torus lattice with the same lattice shuffled once (same degree for every node), under two integrators, with and without energy projection. Everything is scored against a high-precision reference run.

Every version is pre-registered: [v0](PREREGISTRATION.md), [v1](PREREGISTRATION-v1.md). Results are logged in [LEDGER.md](LEDGER.md) and written up in [NEGATIVE-RESULTS.md](NEGATIVE-RESULTS.md).

**v2 result: null.** [PREREGISTRATION-v2.md](PREREGISTRATION-v2.md) tested whether feedback from an E8-symmetric bulk, through the exact H4 projection, suppresses phase slips on the torus more than random or PCA projections do. It doesn't: E8 ÷ random was 0.947, CI [0.853, 1.051], and E8 ÷ PCA was 1.037, CI [0.966, 1.114]. What E8 does differently is fully explained by its torque's correlation time. See [results/v2/summary.md](results/v2/summary.md) and the [ledger](LEDGER.md). Run it with `python run_v2.py --name v2`.

**So far, structure has never beaten its matched control. The torus lattice lost to a shuffled graph, in the chaotic regime (v0) and the calm one (v1). The E8/H4 projection lost to random and PCA projections (v2).**

## v1 result: null, Prediction A ruled out

From [results/v1/summary.md](results/v1/summary.md): calm phase-locked regime, 64 nodes, 30 seeds, T = 500, pre-registered in [PREREGISTRATION-v1.md](PREREGISTRATION-v1.md), sealed in commit `ad7d455` before the run.

- **The regime was calm.** The Lyapunov exponent was 0.0066 on both graphs, about 100× lower than v0, and no edge's phase difference went above 0.6 rad. So the gate passed and the verdicts count.
- **Primary test (leapfrog, projection off): ratio 1.056, 95% CI [0.986, 1.130], a null.** The torus is not more accurate.
- **Prediction A (torus 15–25% more accurate, 0.75–0.85): ruled out.** The interval doesn't reach the band.
- **Prediction B (linear mode theory, no difference, 0.95–1.05): consistent, not confirmed.** The interval overlaps the band but extends past 1.05.
- **All four cells are nulls.** The point estimates are all slightly above 1 (1.06–1.10), so the torus is, if anything, a little worse. The cells share seeds, though, so this is one pattern seen four times, not four independent results. Taken at face value, it fits the torus's higher top frequency (λ_max = 8 vs 7.35), and testing it needs more seeds.
- Energy drift doesn't differ either (ratio 0.997). Charge is conserved to round-off.

## v0 result: null

From [results/baseline-v0/summary.md](results/baseline-v0/summary.md): 64 nodes, 10 seeds, T = 200.

| Integrator | Projection | Torus valid time | Shuffled valid time | Verdict |
|---|---|---|---|---|
| leapfrog | off | 8.6 | 9.9 | shuffled better (2.3 SE) |
| leapfrog | on | 8.3 | 9.4 | shuffled better (2.1 SE) |
| rk4 | off | 19.8 | 20.0 | null |
| rk4 | on | 21.0 | 20.1 | null |

- **The lattice does not beat the shuffled control in any cell.** By the pre-registered test, this is a null result. For leapfrog, the shuffled graph does slightly better, but only just past the 2 SE threshold with 10 seeds, so it needs more seeds before it means anything.
- **Both graphs are equally chaotic.** Their Lyapunov exponents are 0.644 and 0.639. The system is chaotic: even the reference only agrees with a finer reference until about t = 34, and every arm has lost the true trajectory long before T = 200. In this regime, long-horizon accuracy is limited by chaos, not by the method.
- **The integrator matters much more than the graph.** RK4 stays valid about twice as long as leapfrog at the same dt.
- **Energy projection does not change valid time.** It fixes the energy, but the trajectory still diverges.
- **Charge is conserved to round-off in every arm** (≤ 1e-13), as the flux construction guarantees.

## Run it

```bash
pip install -r requirements.txt
python -m pytest -q            # graphs, conservation, convergence order, projection, stats
python run_grid.py --quick     # ~2 s smoke run
python run_grid.py --name my-run --seeds 20 --steps 8000   # full grid, ~4 min at defaults
```

Run `python run_grid.py --help` to see every parameter. Results are written to `results/<name>/`.

## Layout

| Path | Contents |
|---|---|
| `tme/graphs.py` | Torus lattice, degree-preserving shuffle, neighbour table |
| `tme/dynamics.py` | Hamiltonian, forces, charge flux, energy |
| `tme/integrators.py` | Leapfrog (split operator) and RK4 |
| `tme/projection.py` | Energy projection |
| `tme/experiment.py` | The 8-arm grid, reference runs, Lyapunov estimate |
| `tme/analysis.py` | Pre-registered verdicts and the summary table |
| `run_grid.py` | Command-line runner |

## Next steps

1. v1b: sweep energy from the calm regime up to the v0 setting.
2. Add the pieces left out of v0 (6D bulk coordinates, the projection operator F, discrete rewiring events) one at a time, each under the same controls.
