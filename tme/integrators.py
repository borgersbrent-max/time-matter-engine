"""Time steppers. Each takes and returns (theta, p, q)."""

from .dynamics import force, charge_rate


def rk4_step(theta, p, q, nbr, K, D, dt):
    """Classical RK4 on the full state. Not symplectic."""

    def f(th, pp, qq):
        return pp, force(th, nbr, K), charge_rate(th, qq, nbr, D)

    k1 = f(theta, p, q)
    k2 = f(theta + 0.5 * dt * k1[0], p + 0.5 * dt * k1[1], q + 0.5 * dt * k1[2])
    k3 = f(theta + 0.5 * dt * k2[0], p + 0.5 * dt * k2[1], q + 0.5 * dt * k2[2])
    k4 = f(theta + dt * k3[0], p + dt * k3[1], q + dt * k3[2])
    w = dt / 6.0
    return (
        theta + w * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
        p + w * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
        q + w * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]),
    )


def _charge_substep(theta, q, nbr, D, h):
    """RK4 for the charge equation with the phases held fixed."""
    k1 = charge_rate(theta, q, nbr, D)
    k2 = charge_rate(theta, q + 0.5 * h * k1, nbr, D)
    k3 = charge_rate(theta, q + 0.5 * h * k2, nbr, D)
    k4 = charge_rate(theta, q + h * k3, nbr, D)
    return q + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def leapfrog_step(theta, p, q, nbr, K, D, dt):
    """Split-operator step: half charge, kick-drift-kick for (theta, p), half charge.

    The (theta, p) part is the symplectic velocity Verlet scheme.
    """
    q = _charge_substep(theta, q, nbr, D, 0.5 * dt)
    p = p + 0.5 * dt * force(theta, nbr, K)
    theta = theta + dt * p
    p = p + 0.5 * dt * force(theta, nbr, K)
    q = _charge_substep(theta, q, nbr, D, 0.5 * dt)
    return theta, p, q


INTEGRATORS = {"leapfrog": leapfrog_step, "rk4": rk4_step}
