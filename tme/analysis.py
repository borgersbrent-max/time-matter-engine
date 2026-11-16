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
