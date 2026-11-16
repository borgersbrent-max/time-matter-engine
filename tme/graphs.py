"""Graph builders.

Every graph here is 4-regular, so neighbours are stored as an (N, 4) table.
That keeps the dynamics vectorised and guarantees the structured graph and its
control have the same size, edge count and degree sequence.
"""

import numpy as np

DEGREE = 4


def torus_edges(L: int) -> np.ndarray:
    """Edges of an L x L lattice with periodic boundaries (a 2D torus)."""
    if L < 3:
        raise ValueError("L must be >= 3, otherwise the torus has repeated edges")
    edges = []
    for r in range(L):
        for c in range(L):
            i = r * L + c
            edges.append((i, r * L + (c + 1) % L))  # right
            edges.append((i, ((r + 1) % L) * L + c))  # down
    return np.array(edges, dtype=np.int64)


def degree_preserving_shuffle(edges: np.ndarray, seed: int, swaps_per_edge: int = 10) -> np.ndarray:
    """Randomise a graph with double-edge swaps, keeping every node's degree.

    Each swap takes edges (a,b),(c,d) and rewires them to (a,d),(c,b) or
    (a,c),(b,d). Swaps that would create a self-loop or a duplicate edge are
    rejected. The result has the same degree sequence as the input.
    """
    rng = np.random.default_rng(seed)
    E = [tuple(e) for e in edges]
    present = {frozenset(e) for e in E}
    target = swaps_per_edge * len(E)
    done = attempts = 0
    while done < target:
        attempts += 1
        if attempts > 100 * target:
            raise RuntimeError("edge shuffle failed to converge")
        i, j = rng.choice(len(E), size=2, replace=False)
        a, b = E[i]
        c, d = E[j]
        if rng.random() < 0.5:
            n1, n2 = (a, d), (c, b)
        else:
            n1, n2 = (a, c), (b, d)
        if n1[0] == n1[1] or n2[0] == n2[1]:
            continue
        f1, f2 = frozenset(n1), frozenset(n2)
        if f1 in present or f2 in present or f1 == f2:
            continue
        present -= {frozenset(E[i]), frozenset(E[j])}
        present |= {f1, f2}
        E[i], E[j] = n1, n2
        done += 1
    return np.array(E, dtype=np.int64)


def neighbour_table(edges: np.ndarray, n_nodes: int) -> np.ndarray:
    """(N, 4) table of neighbours. Raises if the graph is not 4-regular."""
    nbrs = [[] for _ in range(n_nodes)]
    for a, b in edges:
        nbrs[a].append(b)
        nbrs[b].append(a)
    if any(len(x) != DEGREE for x in nbrs):
        raise ValueError("graph is not 4-regular")
    return np.array(nbrs, dtype=np.int64)
