"""Coupled phase / charge dynamics on a graph.

State per node i: phase theta_i, momentum p_i, charge q_i.

    H = sum_i p_i^2 / 2  -  K * sum_edges cos(theta_i - theta_j)

    dtheta_i/dt = p_i
    dp_i/dt     = -K * sum_{j~i} sin(theta_i - theta_j)
    dq_i/dt     = -sum_{j~i} g_ij (q_i - q_j),  g_ij = D (1 + cos(theta_i - theta_j)) / 2

Charge flows along edges with a symmetric conductance, so the flux on every
edge is antisymmetric and total charge is conserved exactly (to round-off) by
any integrator. Charge does not feed back on the phases in this version.

All arrays carry a leading seed axis: shape (S, N). The neighbour table has
shape (S, N, 4) so every seed can have its own graph.
"""

import numpy as np


def _gather(x: np.ndarray, nbr: np.ndarray) -> np.ndarray:
    """x: (S, N), nbr: (S, N, 4) -> values at neighbours, (S, N, 4)."""
    S, N, k = nbr.shape
    return np.take_along_axis(x, nbr.reshape(S, N * k), axis=1).reshape(S, N, k)


def wrap(x: np.ndarray) -> np.ndarray:
    """Map angles to (-pi, pi]."""
    return (x + np.pi) % (2 * np.pi) - np.pi


def force(theta, nbr, K):
    d = theta[:, :, None] - _gather(theta, nbr)
    return -K * np.sin(d).sum(axis=2)


def charge_rate(theta, q, nbr, D):
    d = theta[:, :, None] - _gather(theta, nbr)
    g = D * 0.5 * (1.0 + np.cos(d))
    return -(g * (q[:, :, None] - _gather(q, nbr))).sum(axis=2)


def potential(theta, nbr, K):
    """Per-seed potential energy, shape (S,). Each edge appears twice in the table."""
    d = theta[:, :, None] - _gather(theta, nbr)
    return -0.5 * K * np.cos(d).sum(axis=(1, 2))


def kinetic(p):
    return 0.5 * (p ** 2).sum(axis=1)


def energy(theta, p, nbr, K):
    return kinetic(p) + potential(theta, nbr, K)
