"""Pre-registered comparison (see PREREGISTRATION.md) and the summary table."""

import numpy as np


def _arm(results, topo, integ, proj):
    for a in results["arms"]:
        if (a["topology"], a["integrator"], a["projection"]) == (topo, integ, proj):
            return a
    raise KeyError((topo, integ, proj))


def compare(x, y):
    """Mean difference x - y, its standard error, and the verdict at 2 SE."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    diff = x.mean() - y.mean()
    se = np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
    if se == 0:
        verdict = "null" if diff == 0 else ("structured better" if diff > 0 else "shuffled better")
    elif diff > 2 * se:
        verdict = "structured better"
    elif diff < -2 * se:
        verdict = "shuffled better"
    else:
        verdict = "null"
    return {"diff": float(diff), "se": float(se), "verdict": verdict}


def primary_verdicts(results):
    """For each integrator x projection cell: torus vs shuffled on valid time."""
    out = []
    for integ in results["config"]["integrators"]:
        for proj in (False, True):
            t = _arm(results, "torus", integ, proj)
            s = _arm(results, "shuffled", integ, proj)
            c = compare(t["valid_time"], s["valid_time"])
            c.update({
                "integrator": integ,
                "projection": proj,
                "torus_mean": float(np.mean(t["valid_time"])),
                "shuffled_mean": float(np.mean(s["valid_time"])),
                "all_trusted": bool(all(t["valid_time_trusted"]) and all(s["valid_time_trusted"])),
                # seeds that never crossed the tolerance: their valid time is only a lower bound
                "censored": (int(np.sum(np.asarray(t["valid_time"]) >= results["times"][-1])),
                             int(np.sum(np.asarray(s["valid_time"]) >= results["times"][-1]))),
            })
            out.append(c)
    return out


def _fmt(x):
    return f"{x:.3g}"


def summary_markdown(results) -> str:
    cfg = results["config"]
    T = results["times"][-1]
    lines = [
        "# Results",
        "",
        f"N = {cfg['L']**2} nodes, dt = {cfg['dt']}, T = {T:g}, {cfg['seeds']} seeds, "
        f"reference dt/{cfg['ref_factor']}, tolerance {cfg['tol']} rad RMS. "
        f"Runtime {results['runtime_s']:.0f} s.",
        "",
        "## Primary test: torus vs shuffled, mean valid time",
        "",
        "Valid time = first time the run's error against the reference exceeds the tolerance. "
        "Higher is better. Verdict uses a 2-standard-error threshold on the difference. "
        "Censored = seeds that stayed under the tolerance for the whole run (torus/shuffled); "
        "if many are censored, run longer before reading the verdict.",
        "",
        "| Integrator | Projection | Torus | Shuffled | Diff ± SE | Verdict | Censored | Reference trusted |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for v in primary_verdicts(results):
        lines.append(
            f"| {v['integrator']} | {'on' if v['projection'] else 'off'} | {_fmt(v['torus_mean'])} | "
            f"{_fmt(v['shuffled_mean'])} | {_fmt(v['diff'])} ± {_fmt(v['se'])} | **{v['verdict']}** | "
            f"{v['censored'][0]}/{v['censored'][1]} | "
            f"{'yes' if v['all_trusted'] else 'NO'} |"
        )
    lines += [
        "",
        "## Confound check: how chaotic is each graph?",
        "",
        "If one graph is simply less chaotic, every method stays accurate longer on it, whatever the "
        "integrator. A valid-time gap that tracks the Lyapunov gap is about the dynamics, not about "
        "the numerics.",
        "",
        "| Topology | Lyapunov exponent (mean ± sd) | Reference horizon (mean) |",
        "|---|---|---|",
    ]
    for topo, info in results["topologies"].items():
        ly = info.get("lyapunov")
        ly_s = f"{_fmt(np.mean(ly))} ± {_fmt(np.std(ly, ddof=1))}" if ly else "not run"
        lines.append(f"| {topo} | {ly_s} | {_fmt(np.mean(info['reference_horizon']))} |")
    lines += [
        "",
        "## Secondary metrics at final time",
        "",
        "Energy drift is per node and is not scored for projection-on runs, which enforce it. "
        "Charge drift should be round-off in every arm.",
        "",
        "| Topology | Integrator | Projection | Median error | Median energy drift | Max charge drift | Projection failures |",
        "|---|---|---|---|---|---|---|",
    ]
    for a in results["arms"]:
        ed = "enforced" if a["projection"] else _fmt(np.median(a["energy_drift"][-1]))
        lines.append(
            f"| {a['topology']} | {a['integrator']} | {'on' if a['projection'] else 'off'} | "
            f"{_fmt(np.median(a['error'][-1]))} | {ed} | {_fmt(np.max(a['charge_drift']))} | "
            f"{a['projection_failures']} |"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# v1: paired, seed-by-seed comparison of final error (see PREREGISTRATION-v1.md)
# ---------------------------------------------------------------------------
from .stats import t_ppf  # noqa: E402

PRIMARY_CELL = ("leapfrog", False)
LYAPUNOV_GATE = 0.05
PHASE_LOCK_GATE = np.pi / 2
USER_BAND = (0.75, 0.85)      # prediction: torus error 15-25% lower
THEORY_BAND = (0.95, 1.05)    # prediction from linear mode theory: no difference


def paired_log_ratio(x, y, alpha):
    """Geometric-mean ratio x/y over paired seeds with a two-sided (1-alpha) CI."""
    d = np.log(np.asarray(x, float)) - np.log(np.asarray(y, float))
    n = len(d)
    m, se = d.mean(), d.std(ddof=1) / np.sqrt(n)
    t = t_ppf(1 - alpha / 2, n - 1)
    return {"ratio": float(np.exp(m)), "lo": float(np.exp(m - t * se)), "hi": float(np.exp(m + t * se)),
            "n": n, "alpha": alpha}


def _verdict(r):
    if r["hi"] < 1:
        return "torus better"
    if r["lo"] > 1:
        return "shuffled better"
    return "null"


def gates(results):
    out = {}
    for topo, info in results["topologies"].items():
        ly = info.get("lyapunov") or [float("nan")]
        out[topo] = {
            "lyapunov_mean": float(np.mean(ly)),
            "lyapunov_ok": bool(np.mean(ly) < LYAPUNOV_GATE),
            "max_edge_phase_diff": float(np.max(info["max_edge_phase_diff"])),
            "phase_locked": bool(np.max(info["max_edge_phase_diff"]) < PHASE_LOCK_GATE),
        }
    out["passed"] = all(v["lyapunov_ok"] and v["phase_locked"] for k, v in out.items() if k != "passed")
    return out


def v1_cells(results):
    cells = []
    integs = results["config"]["integrators"]
    n_secondary = 2 * len(integs) - 1
    for integ in integs:
        for proj in (False, True):
            primary = (integ, proj) == PRIMARY_CELL
            alpha = 0.05 if primary else 0.05 / n_secondary  # Bonferroni on secondary cells
            t = _arm(results, "torus", integ, proj)
            s = _arm(results, "shuffled", integ, proj)
            r = paired_log_ratio(t["error"][-1], s["error"][-1], alpha)
            # The reference must be far more accurate than the runs it scores.
            ref_err = max(max(results["topologies"][k]["reference_final_error"]) for k in ("torus", "shuffled"))
            arm_err = min(min(t["error"][-1]), min(s["error"][-1]))
            r.update({"integrator": integ, "projection": proj, "primary": primary,
                      "verdict": _verdict(r), "reference_ok": bool(ref_err < 0.01 * arm_err)})
            if not proj:
                e = paired_log_ratio(np.asarray(t["energy_drift"][-1]) + 1e-300,
                                     np.asarray(s["energy_drift"][-1]) + 1e-300, alpha)
                r["energy_ratio"] = e
            cells.append(r)
    return cells


def _overlaps(r, band):
    return r["lo"] <= band[1] and r["hi"] >= band[0]


def _within(r, band):
    return r["lo"] >= band[0] and r["hi"] <= band[1]


def prediction_outcome(r, band, requires_torus_better=False):
    """confirmed: CI inside band; consistent: CI overlaps band; ruled out: CI misses band.
    A directional prediction (torus better) also needs the CI to exclude 1."""
    if not _overlaps(r, band) or (requires_torus_better and r["lo"] > 1):
        return "ruled out"
    if _within(r, band):
        return "confirmed"
    if requires_torus_better and r["hi"] >= 1:
        return "consistent, but the interval still includes no difference"
    return "consistent"


def summary_v1_markdown(results) -> str:
    cfg = results["config"]
    T = results["times"][-1]
    g = gates(results)
    cells = v1_cells(results)
    prim = next(c for c in cells if c["primary"])
    lines = [
        "# v1 results: calm, phase-locked regime",
        "",
        f"N = {cfg['L']**2} nodes, dt = {cfg['dt']}, T = {T:g}, {cfg['seeds']} seeds, initial phase spread "
        f"{cfg['theta_scale']}, momentum spread {cfg['p_scale']}, reference dt/{cfg['ref_factor']}. "
        f"Runtime {results['runtime_s']:.0f} s.",
        "",
        "## Gate: is the regime actually calm?",
        "",
        f"Both topologies must have Lyapunov exponent < {LYAPUNOV_GATE} and every edge's phase difference must "
        "stay below π/2 for the whole reference run. If this fails, the run is invalid, not a null.",
        "",
        "| Topology | Lyapunov (mean) | Max edge phase difference | Passed |",
        "|---|---|---|---|",
    ]
    for topo in ("torus", "shuffled"):
        v = g[topo]
        lines.append(f"| {topo} | {_fmt(v['lyapunov_mean'])} | {_fmt(v['max_edge_phase_diff'])} rad | "
                     f"{'yes' if v['lyapunov_ok'] and v['phase_locked'] else 'NO'} |")
    lines += ["", f"**Gate {'passed' if g['passed'] else 'FAILED: the verdicts below do not count'}.**", ""]
    lines += [
        "## Primary test: leapfrog, projection off",
        "",
        "Ratio = geometric mean over seeds of (torus error ÷ shuffled error) at the final time, paired by seed. "
        "Below 1 means the torus is more accurate.",
        "",
        f"**Ratio {prim['ratio']:.3f}, 95% CI [{prim['lo']:.3f}, {prim['hi']:.3f}]: {prim['verdict']}.**",
        "",
        "| Prediction | Band | Result |",
        "|---|---|---|",
        f"| Torus 15–25% more accurate | {USER_BAND[0]}–{USER_BAND[1]} | "
        f"{prediction_outcome(prim, USER_BAND, requires_torus_better=True)} |",
        f"| Linear mode theory: no difference | {THEORY_BAND[0]}–{THEORY_BAND[1]} | "
        f"{prediction_outcome(prim, THEORY_BAND)} |",
        "",
        "## All four cells",
        "",
        f"Secondary cells use Bonferroni-corrected {100 * (1 - 0.05 / 3):.2f}% intervals.",
        "",
        "| Integrator | Projection | Error ratio | CI | Verdict | Energy drift ratio | Reference accurate enough |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in cells:
        er = c.get("energy_ratio")
        er_s = f"{er['ratio']:.3f} [{er['lo']:.3f}, {er['hi']:.3f}]" if er else "enforced"
        lines.append(
            f"| {c['integrator']}{' (primary)' if c['primary'] else ''} | {'on' if c['projection'] else 'off'} | "
            f"{c['ratio']:.3f} | [{c['lo']:.3f}, {c['hi']:.3f}] | **{c['verdict']}** | {er_s} | "
            f"{'yes' if c['reference_ok'] else 'NO'} |")
    lines += [
        "",
        "## Graph spectra",
        "",
        "| Topology | Largest Laplacian eigenvalue | Spectral gap |",
        "|---|---|---|",
    ]
    for topo, info in results["topologies"].items():
        lines.append(f"| {topo} | {_fmt(np.mean(info['laplacian_max']))} | {_fmt(np.mean(info['spectral_gap']))} |")
    lines += [
        "",
        "## Median final error per arm",
        "",
        "| Topology | Integrator | Projection | Median error | Median energy drift | Max charge drift |",
        "|---|---|---|---|---|---|",
    ]
    for a in results["arms"]:
        ed = "enforced" if a["projection"] else _fmt(np.median(a["energy_drift"][-1]))
        lines.append(f"| {a['topology']} | {a['integrator']} | {'on' if a['projection'] else 'off'} | "
                     f"{_fmt(np.median(a['error'][-1]))} | {ed} | {_fmt(np.max(a['charge_drift']))} |")
    return "\n".join(lines) + "\n"
