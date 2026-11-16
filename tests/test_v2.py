import dataclasses

import numpy as np

from tme.e8 import e8_roots, h4_projection, random_projection, potential_grad, positive_roots, PHI
from tme.v2 import ConfigV2, run_v2, windings, integrated_corr_time


def test_e8_roots():
    R = e8_roots()
    assert R.shape == (240, 8)
    assert np.allclose((R ** 2).sum(1), 2)
    assert set(np.round(np.unique(R @ R.T), 9)) == {-2, -1, 0, 1, 2}


def test_h4_projection_gives_two_600_cells():
    P = h4_projection()
    assert np.allclose(P @ P.T, np.eye(4))
    y = e8_roots() @ P.T
    n = np.linalg.norm(y, axis=1)
    radii = np.unique(np.round(n, 8))
    assert len(radii) == 2 and abs(radii[1] / radii[0] - PHI) < 1e-8
    allowed = np.array([0, 0.5, 1, (PHI - 1) / 2, PHI / 2])  # |inner products| on a unit 600-cell
    for r in radii:
        s = y[np.isclose(n, r)] / r
        assert len(s) == 120
        ip = np.abs(s @ s.T).ravel()
        assert np.all(np.min(np.abs(ip[:, None] - allowed[None]), axis=1) < 1e-6)


def test_potential_is_lattice_periodic_and_weyl_symmetric():
    R = e8_roots()
    rh = positive_roots(R)
    rng = np.random.default_rng(0)
    u = rng.normal(size=8)
    g = potential_grad(u, rh, 1.0)
    assert np.allclose(potential_grad(u + R[17], rh, 1.0), g)  # roots generate the lattice
    a = R[3]
    refl = np.eye(8) - np.outer(a, a)  # Weyl reflection (|a|^2 = 2)
    assert np.allclose(potential_grad(refl @ u, rh, 1.0), refl @ g)


def test_random_projection_orthonormal():
    P = random_projection(np.random.default_rng(1))
    assert np.allclose(P @ P.T, np.eye(4))


def test_windings_detect_a_twist():
    L = 8
    c = np.tile(np.arange(L), L)
    th = (2 * np.pi * c / L)[None]  # one full twist along every row
    w = windings(th, L)
    assert (w[0, :L] == 1).all() and (w[0, L:] == 0).all()


def test_corr_time_white_noise_is_short():
    x = np.random.default_rng(0).normal(size=(4000, 2, 3))
    assert np.all(integrated_corr_time(x, 1.0) < 1.5)


def test_v2_smoke_and_pairing():
    cfg = dataclasses.replace(ConfigV2(), seeds=2, burn_steps=200, run_steps=400)
    r = run_v2(cfg, progress=lambda *_: None)
    assert set(r["slips"]) == {"e8", "random", "pca", "none"}
    assert set(r["corr_time"]) == {"e8", "random", "pca"}
    # with beta = 0 every arm is the none arm, step for step
    r0 = run_v2(dataclasses.replace(cfg, beta=0.0), progress=lambda *_: None)
    assert r0["slips"]["e8"] == r0["slips"]["random"] == r0["slips"]["none"]
