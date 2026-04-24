# Testing the Latent Vacuum Stationarity Hypothesis via 1-Loop Gauge-Coupling Running: A Rigorous Negative Result

**Fabien Music Polly¹**
*¹Independent researcher, Sophia Antipolis, France; affiliated University of Oxford*

**Draft version — not peer-reviewed.** Preliminary exploratory analysis for discussion.

---

## Abstract

The Latent Vacuum Stationarity (LVS) framework proposes that physical reality corresponds to stable fixed points of an atemporal space of quantum-field configurations. We test the simplest quantitative version of this claim — that the Standard Model (SM) couplings should satisfy a stationarity condition βᵢ → 0 at some scale Λ_LVS between the electroweak and Planck scales. Using 1-loop renormalization group equations for the three gauge couplings and the top Yukawa, and three distinct robustness metrics, we find: (i) the condition is metric-robust (the three measures agree on the location of the optimum), (ii) the optimum is trivial, corresponding to BSM content that cancels SM β-coefficients as late as possible, and (iii) the Yukawa sector exhibits residual running that cannot be eliminated by gauge-sector manipulation alone. We interpret these as rigorous negative results that constrain the LVS programme: the naïve "vanishing β-function" formulation is either trivially satisfied or reduces to the existing asymptotic-safety programme. We identify three directions for a predictive LVS: full-loop asymptotic safety (à la Wetterich–Reuter), joint gauge–Yukawa stationarity, and Wilsonian extrema in the space of effective theories.

**Keywords:** fixed-point physics, asymptotic safety, renormalization group, foundations of the Standard Model, emergent time.

---

## 1. Introduction

The Latent Vacuum Stationarity (LVS) framework [1], proposed by the author, postulates that the physical universe corresponds to the subset of self-consistent (stationary) configurations of a timeless substrate of quantum potentialities. Several pieces of established physics motivate this view: the timelessness of the Wheeler–DeWitt equation [2], the emergence of time from correlations in a static state (Page–Wootters mechanism [3], confirmed experimentally [4]), the success of fixed-point arguments in predicting the Higgs mass [5], and the near-universal structure of fixed-point phenomena across classical mechanics, field theory, and thermodynamics.

The challenge is to move from interpretive framework to testable prediction. The simplest quantitative translation of LVS is:

> *If physical reality is a fixed point of the substrate, then the renormalization-group flow of the SM couplings should attain stationarity — βᵢ(μ\*) → 0 simultaneously for all couplings — at some energy scale Λ_LVS.*

This is a stronger statement than the standard asymptotic-safety hypothesis [6, 7]. Asymptotic safety requires the existence of a non-trivial UV fixed point including gravity, compatible with a predictive theory. LVS, in contrast, allows the stationarity to occur at any intermediate scale and does not commit to gravity's inclusion.

In this paper we test this simplest formulation of LVS rigorously and find it produces no non-trivial prediction. We interpret the negative result as valuable methodological progress: it narrows the class of viable LVS formulations and indicates where further work should focus.

## 2. Method

### 2.1 One-loop renormalization group equations

We use the 1-loop SM β-functions for the three gauge couplings (GUT normalization) and the top Yukawa coupling [8, 9]:

```
dg_i/d(log μ) = b_i^SM g_i³ / (16π²),  b^SM = (41/10, -19/6, -7)
dy_t/d(log μ) = y_t / (16π²) × [(9/2)y_t² - (17/20)g₁² - (9/4)g₂² - 8g₃²]
```

Initial conditions at the Z-pole are taken from PDG 2024:
- 1/α₁(M_Z) = 59.02, 1/α₂(M_Z) = 29.58, 1/α₃(M_Z) = 8.48
- y_t(M_Z) = √2 M_t/v_EW ≈ 0.99

We restrict to 1-loop because (a) 2-loop implementations require careful treatment of dozens of cross-terms best handled by validated tools (SARAH, RGBeta, FlexibleSUSY) rather than hand-coding, and (b) 1-loop is sufficient to demonstrate the qualitative features we test.

### 2.2 Parametrization of BSM extensions

We parametrize generic BSM extensions by two parameters (α, Λ_BSM):
- **α ∈ [0, 1.5]**: fraction of SM β-coefficient cancellation. α = 0 is pure SM; α = 1 is complete cancellation; α > 1 overshoots.
- **Λ_BSM**: the scale at which the BSM content activates, such that b_eff = (1-α) b_SM above Λ_BSM.

This is a minimal parametrization that can accommodate MSSM-like, asymptotic-safety-like, or partial-cancellation scenarios.

### 2.3 Stationarity metrics

A central methodological question is: how do we measure "closeness to stationarity"? We test three metrics:

| Metric | Expression | Character |
|--------|------------|-----------|
| σ₁ | Σᵢ βᵢ² | Absolute, dimensionful |
| σ₂ | Σᵢ (βᵢ/cᵢ)² | Relative (logarithmic rate), dimensionless |
| σ₃ | Σᵢ √\|βᵢ/cᵢ\| | Sub-linear |

If the three metrics identify the same optimum region in (α, Λ_BSM) space, the LVS optimum is robust and reflects genuine structure. If they disagree, the optimum is an artifact of the choice of measure.

## 3. Results

### 3.1 Validation

Our 1-loop code reproduces the MSSM unification benchmark: couplings meet at μ = 10¹⁶·³ GeV with α_GUT⁻¹ ≈ 24.3 and residual gap Δ ≈ 0.06. This matches the standard literature [7] and confirms correctness of the RGE integration.

### 3.2 Robustness test

The three stationarity metrics yield:

| Metric | α_opt | log₁₀(Λ_BSM/GeV) |
|--------|-------|-------------------|
| σ₁ (absolute) | 1.00 | 18.0 |
| σ₂ (relative) | 0.95 | 18.0 |
| σ₃ (sub-linear) | 1.00 | 18.0 |

The three metrics agree that the LVS-optimal configuration is complete (or near-complete) cancellation of the SM β-coefficients, activated as late as possible. The agreement is quantitatively tight: α-differences ≤ 0.05, Λ-differences ≤ 0. **The robustness test passes.**

### 3.3 The optimum is trivial

Although the optimum is robust, it is physically trivial: "to stop the running, zero out the β-coefficients." The latter condition b_SM + Δb = 0 is a *constraint on BSM content* (specific multiplets must cancel the SM contributions) but does not *predict* any new scale, coupling, or particle. Any BSM content producing the required cancellation works equally; the optimum has no preference for MSSM over extended Higgs sectors or exotic fermions.

### 3.4 Yukawa residue

A fine scan around (α ≈ 1, Λ_BSM = 10¹⁸ GeV) reveals that σ₂ is minimized at α = 0.96 rather than 1.00, with a 0.2% improvement. Decomposition shows this effect arises entirely from the Yukawa sector: the top Yukawa β-function remains non-zero even when the gauge β's vanish, because it contains terms proportional to y_t² and g_i² that cannot all be simultaneously eliminated by adjusting gauge b-coefficients alone.

This establishes that **any LVS stationarity programme must treat gauge and Yukawa sectors jointly**; a gauge-only formulation is structurally incomplete.

## 4. Discussion

### 4.1 A rigorous negative result

We have quantitatively tested the simplest version of LVS — "gauge couplings should cease running" — and found: (a) the condition is robust to choice of metric, but (b) the optimum is trivial, and (c) Yukawa couplings introduce a residual structure that the gauge-only formulation cannot address.

This is a **negative result** in the classical sense: it disconfirms the simplest LVS formulation as a source of novel predictions. It is also a **methodologically valuable** result: it tells us exactly where the simple formulation fails, and therefore where further theoretical work is needed.

### 4.2 Methodological notes

Two observations from this analysis are worth recording for future work:

**First**: an initial 2-loop implementation produced g₁(10¹⁷ GeV) with +23% deviation from the Buttazzo et al. 2013 benchmark [10]. The discrepancy was caught by cross-validation against the published benchmark, and the 2-loop calculation was abandoned in favour of the 1-loop analysis presented here. Novel 2-loop+ calculations should be validated with SARAH / RGBeta / FlexibleSUSY before any conclusion is drawn.

**Second**: an initial finding of "50% partial LVS is optimal" was revealed as an artifact once the robustness test was applied. The test replaced the single stationarity metric with three alternatives (sigma_1, sigma_2, sigma_3 of Section 2.3). All three agreed on a different, trivial optimum, and the "50% preferred" result evaporated.

Both episodes underscore that methodological discipline — multi-metric tests and benchmark cross-validation — remains the primary safeguard against spurious findings.

### 4.3 Three directions for a predictive LVS

We identify three directions in which the LVS programme could become predictive rather than interpretive:

**(A) Full asymptotic safety.** Wetterich–Reuter asymptotic safety requires β(g*) = 0 at all orders, including gravity. This framework has produced at least one major success (Higgs mass prediction, Shaposhnikov–Wetterich 2010 [5]). A reformulation of LVS as "the physical Universe sits at a UV fixed point of all couplings including gravity" would inherit the predictive power of this programme while adding an interpretive layer.

**(B) Joint gauge–Yukawa stationarity.** Our result (section 3.4) shows that a complete stationarity principle must constrain Yukawa couplings alongside gauge couplings. This might produce non-trivial Yukawa relations — e.g., Pendleton–Ross-type quasi-fixed-point predictions [11] — that differ from the SM baseline.

**(C) Wilsonian extrema.** Rather than "couplings do not run," one could formulate LVS as "the physical theory is the extremum of some action on the space of effective theories," giving a variational principle in theory-space. This would embed LVS in rigorous Wilsonian language and might produce non-trivial flow equations.

### 4.4 Status of LVS as an interpretive framework

The negative result of this paper does not invalidate LVS as an *interpretive* framework in the sense of Bohm, Everett, or QBism — which re-describe existing physics in alternative language without producing differential predictions. The value of LVS in this sense is conceptual: articulating a coherent narrative linking the timelessness of Wheeler–DeWitt, the Page–Wootters mechanism, asymptotic safety, and non-locality of Bell correlations. Our results bear on the *quantitative* aspiration of LVS, not on its interpretive value.

## 5. Conclusion

We have tested the simplest quantitative formulation of the Latent Vacuum Stationarity hypothesis — gauge-coupling stationarity at some scale Λ_LVS — using 1-loop RGEs and three independent robustness metrics. The result is a rigorous negative: the naïve formulation either reduces to a trivial "zero the β-coefficients" constraint or requires extension to include the Yukawa sector jointly. We identify three directions (full asymptotic safety, joint gauge–Yukawa stationarity, Wilsonian extrema) in which a predictive LVS could be developed.

Negative results have scientific value: they narrow the space of viable theories. This work constrains the LVS programme without refuting its underlying philosophical motivations, and indicates where further theoretical development should focus.

## References

[1] Music Polly, F. *Latent Vacuum Stationarity: a framework essay*. Draft manuscript, 2026.

[2] DeWitt, B. S. *Quantum Theory of Gravity. I. The Canonical Theory*. Phys. Rev. 160, 1113 (1967).

[3] Page, D. N. and Wootters, W. K. *Evolution without evolution: Dynamics described by stationary observables*. Phys. Rev. D 27, 2885 (1983).

[4] Moreva, E. *et al.*, *Time from quantum entanglement: An experimental illustration*. Phys. Rev. A 89, 052122 (2014).

[5] Shaposhnikov, M. and Wetterich, C. *Asymptotic safety of gravity and the Higgs boson mass*. Phys. Lett. B 683, 196 (2010).

[6] Weinberg, S. *Ultraviolet divergences in quantum theories of gravitation*, in *General Relativity: an Einstein Centenary Survey*, ed. Hawking, S. W. and Israel, W. (Cambridge, 1979), pp. 790–831.

[7] Reuter, M. and Saueressig, F. *Quantum Gravity and the Functional Renormalization Group: The Road towards Asymptotic Safety* (Cambridge, 2019).

[8] Machacek, M. E. and Vaughn, M. T. *Two-loop renormalization group equations in a general quantum field theory*. Nucl. Phys. B222, 83 (1983); B236, 221 (1984); B249, 70 (1985).

[9] Luo, M.-X. and Xiao, Y. *Two-loop renormalization group equations in the standard model*. Phys. Rev. Lett. 90, 011601 (2003) [hep-ph/0207271].

[10] Buttazzo, D. *et al.*, *Investigating the near-criticality of the Higgs boson*. JHEP 12 (2013) 089 [arXiv:1307.3536].

[11] Pendleton, B. and Ross, G. G. *Mass and Mixing Angle Predictions from Infrared Fixed Points*. Phys. Lett. B 98, 291 (1981).

## Acknowledgements

Any errors in coefficients, signs, or derivations are the sole responsibility of the author. This preliminary analysis should be independently verified using validated RGE tools (SARAH, RGBeta, FlexibleSUSY) before any publication-grade claims are drawn.

---

**Data and code availability:** The Jupyter notebook and Python scripts reproducing all figures and numerical values in this paper are available in the supplementary material.

**Competing interests:** The author declares no competing interests.
