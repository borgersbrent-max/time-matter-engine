# time-matter-engine

A sandbox for testing whether structure in a simulation's graph improves long-horizon numerical accuracy. Every test runs against a randomised control from the start.

The first version (v0) simulates coupled phase oscillators that carry a conserved charge on a 4-regular graph. It compares a 2D torus lattice with the same lattice shuffled once (same degree for every node), under two integrators, with and without energy projection. Everything is scored against a high-precision reference run.

See [PREREGISTRATION.md](PREREGISTRATION.md) for the hypothesis and success test. Those were agreed and coded before the first run.

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
python -m pytest -q            # 14 tests: graphs, conservation, convergence order, projection
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

1. Run 30+ seeds to settle whether the leapfrog gap is real.
2. Move to a non-chaotic regime (low energy, phase-locked), where long-horizon drift is a numerical question rather than a chaos question.
3. Add the pieces left out of v0 (6D bulk coordinates, the projection operator F, discrete rewiring events) one at a time, each under the same controls.
