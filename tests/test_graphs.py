import numpy as np
import pytest

from tme.graphs import torus_edges, degree_preserving_shuffle, neighbour_table


def edge_set(e):
    return {frozenset(x) for x in e.tolist()}


def test_torus_is_4_regular():
    L = 6
    e = torus_edges(L)
    assert len(e) == 2 * L * L
    nbr = neighbour_table(e, L * L)
    assert nbr.shape == (L * L, 4)
    assert len(edge_set(e)) == len(e)


def test_torus_rejects_small_L():
    with pytest.raises(ValueError):
        torus_edges(2)


def test_shuffle_preserves_degrees_and_is_simple():
    L = 8
    lattice = torus_edges(L)
    shuf = degree_preserving_shuffle(lattice, seed=1)
    assert len(shuf) == len(lattice)
    assert all(a != b for a, b in shuf)
    assert len(edge_set(shuf)) == len(shuf)
    deg = np.bincount(shuf.ravel(), minlength=L * L)
    assert (deg == 4).all()
    # actually randomised: most lattice edges are gone
    assert len(edge_set(shuf) & edge_set(lattice)) < 0.2 * len(lattice)


def test_shuffle_is_deterministic_per_seed():
    lattice = torus_edges(5)
    a = degree_preserving_shuffle(lattice, seed=3)
    b = degree_preserving_shuffle(lattice, seed=3)
    c = degree_preserving_shuffle(lattice, seed=4)
    assert edge_set(a) == edge_set(b)
    assert edge_set(a) != edge_set(c)
