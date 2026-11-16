# Pre-registration: v2, E8 projection feedback and phase slips

Committed and pushed before any v2 comparison run. The push time on GitHub is
the seal. Every number in this file was fixed before any slip count was seen
for the E8, random or PCA arms.

## Framing: F is physics, not a numerical fix

F is a term in the equations of motion. Each arm is therefore a different
model, and there is no single true trajectory to score them against. The score
is a physical observable: **phase slips**, meaning changes in the winding
number around the torus's loops, compared between arms under identical bulk
motion and identical noise. A positive result would show that the mechanism
works *in this model*. It would not show that nature uses it.

## Model (`tme/v2.py`, `ConfigV2` defaults)

Each node i of the 8 × 8 torus carries a manifest phase θᵢ with momentum pᵢ,
and a bulk vector **u**ᵢ ∈ ℝ⁸.

- **Bulk:** d**u** = [−∇V(**u**) − κ**u**] dt + ε dW, with
  V(**u**) = −(V₀/120) Σ over the 120 root pairs **r** of cos(2π **r**·**u**).
  V has the full E8 lattice symmetry: it is periodic on the lattice,
  invariant under the Weyl group, and has its minima at the lattice points.
  The trap κ|**u**|²/2 keeps that symmetry. V₀ = 2, κ = 0.557, ε = 0.45.
- **Manifest:** dθ = p dt, and
  dp = [−αp − K Σⱼ sin(θᵢ − θⱼ) + τᵢ] dt + σ dB,
  with K = 1, α = 0.5, σ = 0.9.
- **Feedback:** τᵢ = β (hᵢ − μ)/sd, where hᵢ = |P**u**ᵢ|² and β = 0.25.
  μ and sd are each arm's own mean and standard deviation of h during
  burn-in, so every arm's torque has the same size; only its shape and timing
  can differ.
- **Numerics:** Euler–Maruyama, dt = 0.02. Burn-in T = 100 (no feedback,
  nothing counted), then T = 1000 counted. Winding numbers of the 16 loops
  (8 rows, 8 columns) are read every 5 steps. **30 seeds.**
- **Pairing:** the bulk does not depend on the manifest. Within a seed, every
  arm sees the same bulk trajectory and the same manifest noise, step for step.

## Arms (the projection P, 4 × 8)

| Arm | P |
|---|---|
| **e8** | The standard H4 projection: the 4D subspace where a Coxeter element of W(E8) has exponents 1, 11, 19, 29. Verified to send the 240 roots onto two 600-cells of 120 vertices each, with radius ratio φ (test `test_h4_projection_gives_two_600_cells`). |
| **random** | A Haar-random 4D subspace, new for each seed |
| **pca** | The top four principal directions of that seed's bulk during burn-in |
| **none** | β = 0, no feedback |

## Done before the seal (bulk-only, or no-feedback-only)

1. **Bulk temperature.** Too hot (ε ≥ 0.9), the bulk is a featureless Gaussian
   and every subspace looks identical (KS distance 0.01). Too cold (ε = 0.5
   with V₀ ≥ 4), it freezes at one site. The chosen setting puts the bulk on
   the root shell about 83% of the time, hopping about 88 times per node, and
   makes the distribution of h measurably different between E8 and a random
   subspace (KS 0.115). Mean and spread still match (0.855 vs 0.830, and
   0.553 vs 0.554), as Weyl symmetry requires.
2. **σ** was set from the no-feedback arm alone: about 43 slips per 200 time
   units.
3. **β** was set using a calibration arm that is not tested: P = the first
   four coordinate axes. β = 0.25 gave about 1.7× the no-feedback slip count,
   and larger β saturated.
4. **Torque statistics from the bulk alone, with no manifest and no slips.**
   E8 matches four random subspaces on skew and kurtosis: +0.72 / 4.09 for
   E8, against +0.55 to +0.90 and 3.6 to 5.2 for random. But **E8's h
   decorrelates faster at every lag**: autocorrelation 0.667 / 0.555 / 0.476
   at t = 0.1 / 5 / 20, against 0.70–0.71 / 0.60–0.62 / 0.52–0.53 for random.
   This informed Prediction B.

## Gates: if any fails, the run is invalid, not a null

1. The bulk is on the root shell (1 ≤ |**u**|² < 3) at least 50% of the time.
2. Feedback matters: the random arm's mean slip count is at least 1.2× the
   no-feedback arm's.
3. Time step: a full re-run at dt/2 (fresh noise, same seeds and projections)
   gives an E8 ÷ random ratio inside the main run's 95% CI, and changes the
   no-feedback slip rate by no more than 25%.

## Primary test

Per seed, compute log((slips_E8 + 0.5) ÷ (slips_random + 0.5)). The ratio is
the geometric mean of that over seeds, with a 95% t-interval. Below 1 means E8
has fewer slips. The same statistic is computed for E8 ÷ PCA.

**The claim is supported only if E8 beats both random and PCA**: both 95%
intervals entirely below 1. This is the refutation standard you set. Requiring
both to pass is stricter than either alone, so no multiple-comparison
correction is applied.

## Predictions, sealed

Each is scored on E8 ÷ random:

- **confirmed** if the 95% interval lies inside the band
- **consistent** if it overlaps the band
- **ruled out** if it misses the band

**Prediction A (user, stated before the bulk-only check in item 4): band 0.60–0.80**,
that is, 20–40% fewer slips. E8 must also beat PCA.
The argument: the E8-adapted projection shares symmetry with the lattice
harmonic structure, allowing resonant back-reaction that stabilises phase
locking, while a random projection adds geometric frustration and asymmetric
torque.

**Prediction B (Claude, made after the bulk-only check): band 0.80–0.97**,
that is, 3–20% fewer slips.
The argument: by symmetry, E8 can't differ from random in torque size, and
doesn't differ in skew or kurtosis. The one measured difference is that E8's
torque decorrelates faster. Slower torque acts like stronger low-frequency
noise, and the slip rate is very sensitive to noise (σ 0.85 → 0.9 more than
doubled slips). So E8 should slip somewhat less, through correlation time, not
through resonance. Before the bulk-only check, B was "no difference" (Weyl
symmetry). It changed because of that check, and that is recorded here.

## Mechanism test (secondary)

This test separates "E8 geometry" from "shorter correlation time". Fit
log(slips) against each seed's measured torque correlation time, using only
the random and PCA arms. Then ask whether E8's seeds lie on that trend (the
95% interval of E8's mean offset includes 0).

- **On the trend:** correlation time explains E8's result, and no further
  geometric effect is needed. This favours B's mechanism, even if A's
  magnitude band is hit.
- **Off the trend:** E8 does something correlation time alone doesn't
  account for. This favours A's mechanism.

## Run

`python run_v2.py --name v2` runs the main run and the dt/2 check, and writes
`results/v2/summary.md`.
