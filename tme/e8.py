"""E8 root system, the H4 projection, and a potential with E8 lattice symmetry."""

import itertools

import numpy as np

PHI = (1 + 5 ** 0.5) / 2


def e8_roots() -> np.ndarray:
    """The 240 roots of E8 (norm^2 = 2), in the even coordinate system."""
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((1.0, -1.0), repeat=2):
            v = np.zeros(8)
            v[i], v[j] = si, sj
            roots.append(v)
    for signs in itertools.product((0.5, -0.5), repeat=8):
        if sum(s < 0 for s in signs) % 2 == 0:
            roots.append(np.array(signs))
    return np.array(roots)


def e8_simple_roots() -> np.ndarray:
    """A base of simple roots for the roots above (Bourbaki convention)."""
    a = np.zeros((8, 8))
    a[0] = [0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, 0.5]
    a[1] = [1, 1, 0, 0, 0, 0, 0, 0]
    for k in range(2, 8):
        a[k, k - 2], a[k, k - 1] = -1, 1
    return a


def _reflection(a):
    return np.eye(8) - 2 * np.outer(a, a) / (a @ a)


def h4_projection() -> np.ndarray:
    """4 x 8 matrix with orthonormal rows: the projection of R^8 onto the 4D
    subspace where a Coxeter element of W(E8) acts with exponents 1, 11, 19, 29
    (rotation angles 2*pi/30 and 2*pi*11/30). This is the standard E8 -> H4
    projection: it sends the 240 roots onto two concentric 600-cells whose
    radii are in the ratio phi."""
    c = np.eye(8)
    for a in e8_simple_roots():
        c = c @ _reflection(a)
    w, v = np.linalg.eig(c)
    basis = []
    for m in (1, 11):
        k = np.argmin(np.abs(w - np.exp(2j * np.pi * m / 30)))
        basis += [v[:, k].real, v[:, k].imag]
    q, _ = np.linalg.qr(np.array(basis).T)
    return q.T


def random_projection(rng) -> np.ndarray:
    """Haar-random 4 x 8 matrix with orthonormal rows."""
    q, r = np.linalg.qr(rng.normal(size=(8, 8)))
    q = q * np.sign(np.diag(r))
    return q[:, :4].T


def potential_grad(u, roots_half, V0):
    """Gradient of V(u) = -(V0 / 120) * sum over the 120 root pairs of cos(2*pi r.u).

    V is periodic on the E8 lattice (r.lambda is an integer for every lattice
    vector lambda) and invariant under the Weyl group, with minima at the
    lattice points. u has shape (..., 8)."""
    ph = 2 * np.pi * (u @ roots_half.T)
    return (V0 / 120) * 2 * np.pi * (np.sin(ph) @ roots_half)


def positive_roots(roots):
    """One root from each +/- pair (120 of them)."""
    keep = []
    for r in roots:
        nz = r[np.nonzero(r)[0][0]]
        if nz > 0:
            keep.append(r)
    return np.array(keep)
