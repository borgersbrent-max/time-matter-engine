"""v2: manifest phases on the torus, driven by an E8-symmetric bulk through a 4D projection.

Per node i on the 8 x 8 torus:
  bulk     du_i = [-grad V(u_i) - kappa u_i] dt + eps dW_i        (u_i in R^8)
  manifest dtheta_i = p_i dt
           dp_i = [-alpha p_i - K sum_j sin(theta_i - theta_j) + tau_i] dt + sigma dB_i
  torque   tau_i = beta * (h_i - mu) / sd,   h_i = |P u_i|^2

V has the full E8 lattice symmetry (see tme/e8.py); the trap kappa |u|^2 / 2 keeps
it Weyl-invariant. The bulk does not depend on the manifest, so every arm sees
the same bulk trajectory and the same manifest noise. The arms differ only in P:

  e8     the H4 projection (Coxeter exponents 1, 11, 19, 29)
  random a Haar-random 4D subspace, new for every seed
  pca    the top-4 principal subspace of the bulk during burn-in, per seed
  none   beta = 0 (no feedback)

mu and sd are each arm's own mean and standard deviation of h during burn-in,
so every arm's torque has mean ~0 and standard deviation ~beta. Score: phase
slips, i.e. changes in the winding number of the 16 loops of the torus (8 rows,
8 columns), counted after burn-in.
"""

from dataclasses import dataclass, asdict
import time

import numpy as np

from .dynamics import wrap, force
from .e8 import e8_roots, positive_roots, h4_projection, random_projection, potential_grad
from .graphs import torus_edges, neighbour_table

ARMS = ("e8", "random", "pca", "none")


@dataclass
class ConfigV2:
    L: int = 8
    seeds: int = 30
    base_seed: int = 0
    dt: float = 0.02
    burn_steps: int = 5000       # T = 100, no counting, no feedback
    run_steps: int = 50000       # T = 1000, counting
    check_every: int = 5         # winding numbers read every 5 steps
    # bulk
    V0: float = 2.0
    kappa: float = 0.557
    eps: float = 0.45
    # manifest
    K: float = 1.0
    alpha: float = 0.5
    sigma: float = 0.9          # set before the seal from the no-feedback arm only
    beta: float = 0.25          # set before the seal from the coordinate-axes calibration arm only
    arms: tuple = ARMS


def windings(theta, L):
    """Winding numbers of the L row loops and L column loops, shape (S, 2L)."""
    S = theta.shape[0]
    g = theta.reshape(S, L, L)
    rows = wrap(np.roll(g, -1, axis=2) - g).sum(axis=2)
    cols = wrap(np.roll(g, -1, axis=1) - g).sum(axis=1)
    return np.rint(np.concatenate([rows, cols], axis=1) / (2 * np.pi)).astype(np.int64)


def integrated_corr_time(x, dt_sample, max_lag_time=100.0):
    """Integrated autocorrelation time of the torque, per seed.

    x: (n_samples, S, N). The autocorrelation is averaged over nodes and summed
    up to max_lag_time, or up to its first zero crossing if that comes earlier."""
    n = x.shape[0]
    z = x - x.mean(axis=0)
    z = z / (z.std(axis=0) + 1e-12)
    f = np.fft.rfft(z, n=2 * n, axis=0)
    ac = np.fft.irfft(f * np.conj(f), axis=0)[:n] / np.arange(n, 0, -1)[:, None, None]
    ac = ac.mean(axis=2)  # (n, S)
    max_lag = min(n - 1, int(max_lag_time / dt_sample))
    out = np.empty(ac.shape[1])
    for s in range(ac.shape[1]):
        a = ac[1:max_lag + 1, s]
        cut = np.argmax(a <= 0) if np.any(a <= 0) else len(a)
        out[s] = dt_sample * (0.5 + a[:cut].sum())
    return out


def _projections(cfg, u_burn):
    """One (S, 4, 8) projection stack per arm with feedback."""
    S = cfg.seeds
    P = {"e8": np.repeat(h4_projection()[None], S, axis=0)}
    # calibration only (not a test arm): the first four coordinate axes
    P["axes"] = np.repeat(np.eye(8)[:4][None], S, axis=0)
    if "random" in cfg.arms:
        P["random"] = np.stack([random_projection(np.random.default_rng(cfg.base_seed + 20_000 + s))
                                for s in range(S)])
    if "pca" in cfg.arms:
        pcs = []
        for s in range(S):
            x = u_burn[:, s].reshape(-1, 8)
            w, v = np.linalg.eigh(np.cov(x.T))
            pcs.append(v[:, np.argsort(w)[::-1][:4]].T)
        P["pca"] = np.stack(pcs)
    return {k: v for k, v in P.items() if k in cfg.arms}


def _h(u, P):
    """|P u|^2 per seed and node. u: (S, N, 8), P: (S, 4, 8)."""
    return (np.einsum("snd,skd->snk", u, P) ** 2).sum(axis=2)


def run_v2(cfg: ConfigV2, progress=print) -> dict:
    t0 = time.time()
    S, L = cfg.seeds, cfg.L
    N = L * L
    nbr = np.repeat(neighbour_table(torus_edges(L), N)[None], S, axis=0)
    roots = e8_roots()
    rh = positive_roots(roots)
    rng = np.random.default_rng(cfg.base_seed)
    sq = np.sqrt(cfg.dt)

    def bulk_step(u):
        return u + cfg.dt * (-potential_grad(u, rh, cfg.V0) - cfg.kappa * u) + cfg.eps * sq * rng.normal(size=u.shape)

    def manifest_step(th, p, tau, noise):
        p = p + cfg.dt * (-cfg.alpha * p + force(th, nbr, cfg.K) + tau) + cfg.sigma * sq * noise
        th = th + cfg.dt * p
        return th, p

    # start: each node's bulk on a random root, manifest synchronised at rest
    u = roots[rng.integers(0, 240, size=(S, N))]
    th = np.zeros((S, N))
    p = np.zeros((S, N))

    # burn-in: bulk and manifest evolve, no feedback, nothing counted
    progress("burn-in")
    samples = []
    for step in range(cfg.burn_steps):
        u = bulk_step(u)
        th, p = manifest_step(th, p, 0.0, rng.normal(size=(S, N)))
        if step % 10 == 0 and step >= cfg.burn_steps // 5:
            samples.append(u.copy())
    u_burn = np.array(samples)  # (n, S, N, 8)

    P = _projections(cfg, u_burn)
    norm = {}
    for k, Pk in P.items():
        hb = np.array([_h(x, Pk) for x in u_burn])  # (n, S, N)
        norm[k] = (hb.mean(axis=(0, 2)), hb.std(axis=(0, 2)))  # per seed

    # every arm starts from the same burned-in state
    state = {k: (th.copy(), p.copy()) for k in cfg.arms}
    W = {k: windings(th, L) for k in cfg.arms}
    slips = {k: np.zeros(S, dtype=np.int64) for k in cfg.arms}
    torque_sd = {k: [] for k in P}
    root_occ = []
    tau_series = {k: [] for k in P if k in cfg.arms and k != "none"}
    TAU_EVERY = 25

    progress("run")
    for step in range(1, cfg.run_steps + 1):
        u = bulk_step(u)
        noise = rng.normal(size=(S, N))
        for k in cfg.arms:
            if k == "none":
                tau = 0.0
            else:
                mu, sd = norm[k]
                tau = cfg.beta * (_h(u, P[k]) - mu[:, None]) / sd[:, None]
            th_k, p_k = manifest_step(*state[k], tau, noise)
            state[k] = (th_k, p_k)
            if k in tau_series and step % TAU_EVERY == 0:
                tau_series[k].append(np.asarray(tau, dtype=np.float32))
            if step % cfg.check_every == 0:
                w = windings(th_k, L)
                slips[k] += np.abs(w - W[k]).sum(axis=1)
                W[k] = w
                if k != "none" and step % 500 == 0:
                    torque_sd[k].append(float(np.std(tau)))
        if step % 500 == 0:
            n2 = (u ** 2).sum(axis=2)
            root_occ.append(float(np.mean((n2 >= 1.0) & (n2 < 3.0))))

    corr_time = {k: integrated_corr_time(np.array(v), cfg.dt * TAU_EVERY).tolist()
                 for k, v in tau_series.items()}
    return {
        "config": asdict(cfg),
        "slips": {k: v.tolist() for k, v in slips.items()},
        "corr_time": corr_time,
        "torque_sd": {k: (float(np.mean(v)) if v else None) for k, v in torque_sd.items()},
        "root_shell_occupancy": float(np.mean(root_occ)) if root_occ else None,
        "runtime_s": time.time() - t0,
    }
