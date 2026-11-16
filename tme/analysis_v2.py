"""Pre-registered v2 analysis (see PREREGISTRATION-v2.md)."""

import numpy as np

from .analysis import paired_log_ratio, prediction_outcome
from .stats import t_ppf

USER_BAND = (0.60, 0.80)
CLAUDE_BAND = (0.80, 0.97)
OCCUPANCY_GATE = 0.5
FEEDBACK_GATE = 1.2


def _counts(res, arm):
    return np.asarray(res["slips"][arm], float) + 0.5  # continuity correction for zero counts


def ratio(res, a, b, alpha=0.05):
    return paired_log_ratio(_counts(res, a), _counts(res, b), alpha)


def gates(res, res_half=None):
    g = {
        "root_shell_occupancy": res["root_shell_occupancy"],
        "occupancy_ok": res["root_shell_occupancy"] >= OCCUPANCY_GATE,
        "feedback_ratio": float(np.mean(res["slips"]["random"]) / max(np.mean(res["slips"]["none"]), 1e-9)),
    }
    g["feedback_ok"] = g["feedback_ratio"] >= FEEDBACK_GATE
    if res_half is not None:
        main = ratio(res, "e8", "random")
        half = ratio(res_half, "e8", "random")
        g["dt_half_ratio"] = half["ratio"]
        g["dt_ratio_ok"] = main["lo"] <= half["ratio"] <= main["hi"]
        g["dt_none_rate_change"] = float(np.mean(res_half["slips"]["none"]) / np.mean(res["slips"]["none"]) - 1)
        g["dt_rate_ok"] = abs(g["dt_none_rate_change"]) <= 0.25
    g["passed"] = all(v for k, v in g.items() if k.endswith("_ok"))
    return g


def mechanism(res):
    """Fit log(slips) ~ correlation time over the random and PCA arms' seeds,
    then ask whether E8's seeds lie inside that fit's 95% prediction band."""
    x = np.concatenate([res["corr_time"]["random"], res["corr_time"]["pca"]])
    y = np.log(np.concatenate([_counts(res, "random"), _counts(res, "pca")]))
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    n = len(y)
    s2 = resid @ resid / (n - 2)
    xe = np.asarray(res["corr_time"]["e8"])
    ye = np.log(_counts(res, "e8"))
    # mean E8 residual and its 95% interval, against the random/PCA trend
    pred = coef[0] + coef[1] * xe
    XtX_inv = np.linalg.inv(X.T @ X)
    xbar = np.array([1.0, xe.mean()])
    se = np.sqrt(s2 * (1.0 / len(xe) + xbar @ XtX_inv @ xbar))
    d = float(np.mean(ye - pred))
    t = t_ppf(0.975, n - 2)
    return {
        "slope": float(coef[1]),
        "e8_offset": d,
        "lo": d - t * se,
        "hi": d + t * se,
        "explained": bool(d - t * se <= 0 <= d + t * se),
        "corr_time_mean": {k: float(np.mean(v)) for k, v in res["corr_time"].items()},
    }


def summary_markdown(res, res_half=None):
    g = gates(res, res_half)
    er = ratio(res, "e8", "random")
    ep = ratio(res, "e8", "pca")
    beats_both = er["hi"] < 1 and ep["hi"] < 1
    m = mechanism(res)
    cfg = res["config"]
    T = cfg["run_steps"] * cfg["dt"]

    def verdict(r):
        return "E8 fewer slips" if r["hi"] < 1 else ("E8 more slips" if r["lo"] > 1 else "null")

    user = prediction_outcome(er, USER_BAND, requires_torus_better=True)
    if not beats_both and user != "ruled out":
        user += "; but E8 does not beat both random and PCA, so the claim is not supported"
    lines = [
        "# v2 results: E8 projection feedback and phase slips",
        "",
        f"8 × 8 torus, {cfg['seeds']} seeds, T = {T:g} counted after a burn-in, dt = {cfg['dt']}. "
        f"Runtime {res['runtime_s']:.0f} s.",
        "",
        "## Gates",
        "",
        "| Check | Value | Required | Passed |",
        "|---|---|---|---|",
        f"| Bulk on the root shell | {g['root_shell_occupancy']:.2f} | ≥ {OCCUPANCY_GATE} | {'yes' if g['occupancy_ok'] else 'NO'} |",
        f"| Feedback matters (random ÷ none slips) | {g['feedback_ratio']:.2f} | ≥ {FEEDBACK_GATE} | {'yes' if g['feedback_ok'] else 'NO'} |",
    ]
    if res_half is not None:
        lines += [
            f"| E8 ÷ random at dt/2 lies inside the main 95% CI | {g['dt_half_ratio']:.3f} | in [{er['lo']:.3f}, {er['hi']:.3f}] | {'yes' if g['dt_ratio_ok'] else 'NO'} |",
            f"| No-feedback slip rate change at dt/2 | {100 * g['dt_none_rate_change']:+.0f}% | within ±25% | {'yes' if g['dt_rate_ok'] else 'NO'} |",
        ]
    lines += ["", f"**Gates {'passed' if g['passed'] else 'FAILED: the verdicts below do not count'}.**", "",
              "## Primary test",
              "",
              "Ratio = geometric mean over seeds of slip counts (each + 0.5), paired by seed. Below 1 means E8 has fewer slips.",
              "",
              "| Comparison | Ratio | 95% CI | Verdict |",
              "|---|---|---|---|",
              f"| E8 ÷ random | {er['ratio']:.3f} | [{er['lo']:.3f}, {er['hi']:.3f}] | **{verdict(er)}** |",
              f"| E8 ÷ PCA | {ep['ratio']:.3f} | [{ep['lo']:.3f}, {ep['hi']:.3f}] | **{verdict(ep)}** |",
              "",
              f"E8 beats both random and PCA: **{'yes' if beats_both else 'no'}**.",
              "",
              "| Prediction | Band (E8 ÷ random) | Result |",
              "|---|---|---|",
              f"| A (user): 20–40% fewer slips, and E8 beats PCA too | {USER_BAND[0]}–{USER_BAND[1]} | {user} |",
              f"| B (Claude): 3–20% fewer slips, from shorter torque correlation | {CLAUDE_BAND[0]}–{CLAUDE_BAND[1]} | {prediction_outcome(er, CLAUDE_BAND)} |",
              "",
              "## Mechanism test",
              "",
              "Fit log(slips) against torque correlation time across the random and PCA seeds. If E8's seeds sit on "
              "that trend, correlation time explains E8's result and no extra geometric effect is needed.",
              "",
              f"Slope {m['slope']:.3f} per time unit. E8 offset from the trend: {m['e8_offset']:+.3f} "
              f"(95% CI [{m['lo']:+.3f}, {m['hi']:+.3f}]) in log slips. "
              f"**{'Explained by correlation time' if m['explained'] else 'Not explained by correlation time alone'}.**",
              "",
              "| Arm | Mean slips | Mean torque correlation time |",
              "|---|---|---|"]
    for k in ("e8", "random", "pca", "none"):
        ct = m["corr_time_mean"].get(k)
        lines.append(f"| {k} | {np.mean(res['slips'][k]):.1f} | {'' if ct is None else f'{ct:.2f}'} |")
    return "\n".join(lines) + "\n"
