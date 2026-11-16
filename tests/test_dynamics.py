import numpy as np
import pytest

from tme.dynamics import force, potential, energy, wrap
from tme.graphs import torus_edges, degree_preserving_shuffle, neighbour_table
from tme.integrators import leapfrog_step, rk4_step
from tme.projection import project_energy

L, K, D = 4, 1.0, 0.1
N = L * L


def setup(topology="torus", seed=0):
    e = torus_edges(L) if topology == "torus" else degree_preserving_shuffle(torus_edges(L), seed=seed)
    nbr = neighbour_table(e, N)[None]
    rng = np.random.default_rng(seed)
    th = rng.uniform(-np.pi, np.pi, (1, N))
    p = rng.normal(0, 0.5, (1, N))
    p -= p.mean()
    q = rng.uniform(0.5, 1.5, (1, N))
    return nbr, th, p, q


def run(step, nbr, th, p, q, dt, n):
    for _ in range(n):
        th, p, q = step(th, p, q, nbr, K, D, dt)
    return th, p, q


@pytest.mark.parametrize("topology", ["torus", "shuffled"])
def test_force_is_minus_grad_potential(topology):
    nbr, th, _, _ = setup(topology)
    f = force(th, nbr, K)
    h = 1e-6
    for i in range(N):
        tp, tm = th.copy(), th.copy()
        tp[0, i] += h
        tm[0, i] -= h
        num = -(potential(tp, nbr, K) - potential(tm, nbr, K)) / (2 * h)
        assert abs(num[0] - f[0, i]) < 1e-6


@pytest.mark.parametrize("step", [leapfrog_step, rk4_step])
def test_charge_and_momentum_conserved(step):
    nbr, th, p, q = setup("shuffled")
    Q0, P0 = q.sum(), p.sum()
    th, p, q = run(step, nbr, th, p, q, 0.05, 1000)
    assert abs(q.sum() - Q0) < 1e-10
    assert abs(p.sum() - P0) < 1e-10


@pytest.mark.parametrize("step,order", [(leapfrog_step, 2), (rk4_step, 4)])
def test_convergence_order(step, order):
    nbr, th, p, q = setup()
    T = 1.0
    ref = run(rk4_step, nbr, th, p, q, T / 4096, 4096)
    errs = []
    for n in (32, 64, 128):
        out = run(step, nbr, th, p, q, T / n, n)
        errs.append(np.abs(wrap(out[0] - ref[0])).max() + np.abs(out[1] - ref[1]).max())
    rates = np.log2(np.array(errs[:-1]) / np.array(errs[1:]))
    assert np.all(np.abs(rates - order) < 0.4), rates


def test_leapfrog_energy_error_stays_bounded():
    nbr, th, p, q = setup()
    E0 = energy(th, p, nbr, K)
    drifts = []
    for _ in range(20):
        th, p, q = run(leapfrog_step, nbr, th, p, q, 0.05, 500)
        drifts.append(abs(energy(th, p, nbr, K) - E0)[0])
    # symplectic: energy error oscillates, it does not grow with time
    assert max(drifts) < 0.05 * abs(E0[0]) + 0.05
    assert np.mean(drifts[-5:]) < 3 * np.mean(drifts[:5]) + 1e-3


def test_projection_restores_energy():
    nbr, th, p, q = setup()
    E0 = energy(th, p, nbr, K)
    th2, p2, _ = run(rk4_step, nbr, th, p, q, 0.3, 50)  # deliberately sloppy
    p3, fails = project_energy(th2, p2, nbr, K, E0)
    assert fails == 0
    assert abs(energy(th2, p3, nbr, K) - E0)[0] < 1e-10
    assert abs(p3.sum()) < 1e-10
