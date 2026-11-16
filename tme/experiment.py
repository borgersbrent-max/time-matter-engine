"""The 8-arm control grid: integrator x projection x topology.

For each topology, every seed gets the same initial conditions (so the two
topologies are matched seed by seed) and the shuffled topology gets its own
shuffle per seed. Each arm is scored against a high-precision RK4 reference
run on the same graph from the same start.
"""

from dataclasses import dataclass, asdict, field
import itertools
import time

import numpy as np

from .dynamics import energy, wrap
from .graphs import torus_edges, degree_preserving_shuffle, neighbour_table
from .integrators import INTEGRATORS, rk4_step
from .projection import project_energy

TOPOLOGIES = ("torus", "shuffled")
PROJECTIONS = (False, True)


@dataclass
class Config:
    L: int = 8                 # lattice side; N = L*L nodes
    K: float = 1.0             # phase coupling
    D: float = 0.1             # charge conductance
    p_scale: float = 0.5       # std of initial momenta
    dt: float = 0.05           # step size for the arms under test
    steps: int = 4000          # steps per run (total time = steps * dt)
    check_every: int = 20      # record metrics every this many steps
    ref_factor: int = 16       # reference uses dt / ref_factor
    tol: float = 0.1           # trajectory error (rad RMS) that ends "valid time"
    seeds: int = 10
    base_seed: int = 0
    integrators: tuple = ("leapfrog", "rk4")
    lyapunov: bool = True      # estimate each topology's largest Lyapunov exponent


def build_graphs(cfg: Config, topology: str) -> np.ndarray:
    N = cfg.L * cfg.L
    lattice = torus_edges(cfg.L)
    tables = []
    for s in range(cfg.seeds):
        e = lattice if topology == "torus" else degree_preserving_shuffle(lattice, seed=cfg.base_seed + 10_000 + s)
        tables.append(neighbour_table(e, N))
    return np.stack(tables)


def initial_state(cfg: Config):
    N = cfg.L * cfg.L
    th, p, q = [], [], []
    for s in range(cfg.seeds):
        rng = np.random.default_rng(cfg.base_seed + s)
        th.append(rng.uniform(-np.pi, np.pi, N))
        pp = rng.normal(0.0, cfg.p_scale, N)
        p.append(pp - pp.mean())  # zero total momentum, so projection keeps it zero
        q.append(rng.uniform(0.5, 1.5, N))
    return np.array(th), np.array(p), np.array(q)


def _run(cfg, nbr, state, stepper, dt, n_sub, project, E0):
    """Run cfg.steps outer steps of size dt (each split into n_sub substeps).
    Returns states at every checkpoint (including t=0) and projection failures."""
    th, p, q = (x.copy() for x in state)
    h = dt / n_sub
    traj = [(th.copy(), p.copy(), q.copy())]
    fails = 0
    for step in range(1, cfg.steps + 1):
        for _ in range(n_sub):
            th, p, q = stepper(th, p, q, nbr, cfg.K, cfg.D, h)
        if project:
            p, f = project_energy(th, p, nbr, cfg.K, E0)
            fails += f
        if step % cfg.check_every == 0:
            traj.append((th.copy(), p.copy(), q.copy()))
    return traj, fails


def traj_error(a, b):
    """Per-seed RMS error over phases (wrapped) and momenta."""
    dth = wrap(a[0] - b[0])
    dp = a[1] - b[1]
    return np.sqrt((dth ** 2).mean(axis=1) + (dp ** 2).mean(axis=1))


def valid_time(err, times, tol):
    """First recorded time each seed's error exceeds tol; the final time if never."""
    out = np.full(err.shape[1], times[-1])
    for s in range(err.shape[1]):
        idx = np.nonzero(err[:, s] > tol)[0]
        if idx.size:
            out[s] = times[idx[0]]
    return out


def lyapunov_estimate(cfg, nbr, state, d0=1e-8, renorm_every=20):
    """Largest Lyapunov exponent per seed, by the two-trajectory method
    (RK4 at dt / 4, renormalising the separation every renorm_every steps)."""
    th, p, q = (x.copy() for x in state)
    rng = np.random.default_rng(cfg.base_seed + 99)
    v = rng.normal(size=(2,) + th.shape)
    v /= np.sqrt((v ** 2).sum(axis=(0, 2)))[None, :, None]
    th2, p2 = th + d0 * v[0], p + d0 * v[1]
    q2 = q.copy()
    h = cfg.dt / 4
    log_sum = np.zeros(th.shape[0])
    n_steps = cfg.steps * 4
    for step in range(1, n_steps + 1):
        th, p, q = rk4_step(th, p, q, nbr, cfg.K, cfg.D, h)
        th2, p2, q2 = rk4_step(th2, p2, q2, nbr, cfg.K, cfg.D, h)
        if step % renorm_every == 0:
            dth, dp = th2 - th, p2 - p
            d = np.sqrt((dth ** 2).sum(axis=1) + (dp ** 2).sum(axis=1))
            log_sum += np.log(d / d0)
            th2 = th + dth * (d0 / d)[:, None]
            p2 = p + dp * (d0 / d)[:, None]
    return log_sum / (n_steps * h)


def run_grid(cfg: Config, progress=print) -> dict:
    t_start = time.time()
    times = np.arange(0, cfg.steps + 1, cfg.check_every) * cfg.dt
    state0 = initial_state(cfg)
    results = {"config": asdict(cfg), "times": times.tolist(), "topologies": {}, "arms": []}

    for topo in TOPOLOGIES:
        nbr = build_graphs(cfg, topo)
        E0 = energy(state0[0], state0[1], nbr, cfg.K)
        progress(f"[{topo}] reference runs (dt/{cfg.ref_factor} and dt/{2 * cfg.ref_factor})")
        ref, _ = _run(cfg, nbr, state0, rk4_step, cfg.dt, cfg.ref_factor, False, E0)
        ref2, _ = _run(cfg, nbr, state0, rk4_step, cfg.dt, 2 * cfg.ref_factor, False, E0)
        ref_self = np.array([traj_error(a, b) for a, b in zip(ref, ref2)])
        # The reference is only trusted while it agrees with a finer reference
        # to well inside the tolerance used for scoring.
        ref_horizon = valid_time(ref_self, times, cfg.tol / 10)
        topo_info = {
            "reference_horizon": ref_horizon.tolist(),
            "E0": E0.tolist(),
        }
        if cfg.lyapunov:
            progress(f"[{topo}] Lyapunov estimate")
            topo_info["lyapunov"] = lyapunov_estimate(cfg, nbr, state0).tolist()
        results["topologies"][topo] = topo_info

        for integ, proj in itertools.product(cfg.integrators, PROJECTIONS):
            progress(f"[{topo}] {integ}, projection {'on' if proj else 'off'}")
            traj, fails = _run(cfg, nbr, state0, INTEGRATORS[integ], cfg.dt, 1, proj, E0)
            err = np.array([traj_error(a, b) for a, b in zip(traj, ref)])
            E = np.array([energy(s[0], s[1], nbr, cfg.K) for s in traj])
            Q = np.array([s[2].sum(axis=1) for s in traj])
            vt = valid_time(err, times, cfg.tol)
            results["arms"].append({
                "topology": topo,
                "integrator": integ,
                "projection": proj,
                "valid_time": vt.tolist(),
                # valid time beyond the reference's own horizon can't be checked
                "valid_time_trusted": (vt <= ref_horizon).tolist(),
                "error": err.tolist(),
                "energy_drift": (np.abs(E - E0[None, :]) / (cfg.L * cfg.L)).tolist(),
                "charge_drift": np.abs(Q - Q[0][None, :]).tolist(),
                "projection_failures": fails,
            })
    results["runtime_s"] = time.time() - t_start
    return results
