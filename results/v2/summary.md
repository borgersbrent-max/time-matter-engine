# v2 results: E8 projection feedback and phase slips

8 × 8 torus, 30 seeds, T = 1000 counted after a burn-in, dt = 0.02. Runtime 273 s.

## Gates

| Check | Value | Required | Passed |
|---|---|---|---|
| Bulk on the root shell | 0.74 | ≥ 0.5 | yes |
| Feedback matters (random ÷ none slips) | 2.28 | ≥ 1.2 | yes |
| E8 ÷ random at dt/2 lies inside the main 95% CI | 0.900 | in [0.853, 1.051] | yes |
| No-feedback slip rate change at dt/2 | +4% | within ±25% | yes |

**Gates passed.**

## Primary test

Ratio = geometric mean over seeds of slip counts (each + 0.5), paired by seed. Below 1 means E8 has fewer slips.

| Comparison | Ratio | 95% CI | Verdict |
|---|---|---|---|
| E8 ÷ random | 0.947 | [0.853, 1.051] | **null** |
| E8 ÷ PCA | 1.037 | [0.966, 1.114] | **null** |

E8 beats both random and PCA: **no**.

| Prediction | Band (E8 ÷ random) | Result |
|---|---|---|
| A (user): 20–40% fewer slips, and E8 beats PCA too | 0.6–0.8 | ruled out |
| B (Claude): 3–20% fewer slips, from shorter torque correlation | 0.8–0.97 | consistent |

## Mechanism test

Fit log(slips) against torque correlation time across the random and PCA seeds. If E8's seeds sit on that trend, correlation time explains E8's result and no extra geometric effect is needed.

Slope 0.014 per time unit. E8 offset from the trend: +0.009 (95% CI [-0.089, +0.107]) in log slips. **Explained by correlation time.**

| Arm | Mean slips | Mean torque correlation time |
|---|---|---|
| e8 | 451.9 | 48.20 |
| random | 481.9 | 49.34 |
| pca | 436.9 | 49.66 |
| none | 211.5 |  |
