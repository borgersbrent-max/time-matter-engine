"""Energy projection: rescale momenta so total energy returns to its start value.

This enforces energy conservation by construction, so energy drift is NOT a
fair score for runs that use it. Those runs are scored on trajectory error.
"""

import numpy as np

from .dynamics import kinetic, potential


def project_energy(theta, p, nbr, K, E0):
    """Return (p_projected, n_failed). A seed fails when its potential alone
    already exceeds E0 (no real rescaling exists) or its kinetic energy is 0;
    its momenta are then left unchanged."""
    target = E0 - potential(theta, nbr, K)
    kin = kinetic(p)
    ok = (target > 0) & (kin > 0)
    scale = np.ones_like(kin)
    scale[ok] = np.sqrt(target[ok] / kin[ok])
    return p * scale[:, None], int((~ok).sum())
