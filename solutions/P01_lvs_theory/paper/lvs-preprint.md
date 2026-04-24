# Latent Vacuum Stationarity as a Boundary Condition at the Planck Scale: A Conditional Framework

**Fabien Polly**¹

¹*Independent researcher, Sophia Antipolis, France; affiliated with University of Oxford*



---

## Abstract

We propose Latent Vacuum Stationarity (LVS) as an interpretive framework in which the physical vacuum corresponds to stationary configurations of the renormalization group (RG) flow. We test the simplest quantitative formulation - that Standard Model (SM) parameters globally minimize the RG action - and falsify it: the global minimum of $\int \sum_i \beta_i^2 \, dt$ along the SM trajectory requires $\alpha_s(M_Z) \approx 0.048$, incompatible with the measured value $\alpha_s(M_Z) = 0.1179$. We then examine a weaker formulation in which LVS acts only as a boundary condition at the Planck scale, requiring $\beta_i \to 0$ for all couplings at $M_{Pl}$. Within the Asymptotic Safety scenario, this yields a conditional deduction: if LVS holds, the gravity-induced anomalous dimensions must satisfy $f_g \sim 10^{-2}$ and $f_y \sim 10^{-2}$. Current functional renormalization group (FRG) estimates from Eichhorn & Held (2018) yield $f_g \approx 0.055$ and $f_y \approx 0.004$, differing from LVS requirements by a factor 3–5. Given the acknowledged $\sim$60% truncation uncertainty in current FRG calculations, LVS is neither confirmed nor definitively refuted. The framework is compatible with the observed near-criticality of the Higgs sector [Buttazzo et al. 2013] but does not mechanistically explain it. We position LVS as an interpretive candidate awaiting convergence of FRG calculations.

**Keywords:** renormalization group, asymptotic safety, Higgs near-criticality, fixed-point physics, Planck-scale boundary conditions.

---

## 1. Introduction

The Standard Model extrapolated to the Planck scale exhibits a remarkable feature: the Higgs quartic coupling $\lambda$ and its beta function $\beta_\lambda$ approach zero simultaneously near $M_{Pl}$ [1,2]. This "near-criticality" has motivated several theoretical frameworks, including asymptotic safety with matter [3,4], Higgs inflation [5], and anthropic selection [6].

In this letter we propose a complementary interpretive framework, which we call *Latent Vacuum Stationarity* (LVS): the hypothesis that the physical vacuum corresponds to a stationary configuration of the RG flow, in the sense that the beta functions of all SM couplings vanish (or are minimized) at a characteristic scale.

LVS is motivated by two observations. First, fixed-point physics is ubiquitous across scales: the Higgs near-criticality [1,2], the infrared quasi-fixed points of Pendleton-Ross [7] and Hill [8], and the ultraviolet fixed points of asymptotic safety [9–11]. Second, the timelessness of the Wheeler-DeWitt equation [12] and the Page-Wootters mechanism [13,14] suggest that stationarity may be a foundational feature of physical reality rather than an accidental property of specific theories.

The aim of this letter is to test whether LVS, taken as a principle, produces falsifiable constraints on SM parameters. We find that the strong (global) form of LVS is falsified, while a weaker (boundary-condition) form yields conditional deductions that are currently compatible with - but not specific to - asymptotic safety.

The letter is organized as follows. Section 2 tests and falsifies global LVS. Section 3 formulates LVS as a Planck-scale boundary condition and computes the required anomalous dimensions. Section 4 compares these to current FRG estimates. Section 5 discusses the epistemological status and open problems.

---

## 2. Global LVS: Formulation and Falsification

### 2.1 Formulation

The strongest form of LVS posits that the SM couplings minimize a global functional of the RG flow between the electroweak scale and the Planck scale:

$$S_{\text{LVS}}[\alpha_s, \alpha_1, \alpha_2, y_t] = \int_{\log M_Z}^{\log M_{Pl}} \sum_i \beta_i^2(\mu) \, d\log \mu \quad (1)$$

or equivalently the Euclidean length $L_{\text{LVS}} = \int \sqrt{\sum_i \beta_i^2} \, d\log \mu$.

If LVS were a global variational principle, the measured values of the SM couplings should minimize (1) or $L_{\text{LVS}}$.

### 2.2 Numerical test

We integrate the one-loop SM RGEs for $(g_1, g_2, g_3, y_t)$ from $M_Z$ to $M_{Pl}$ using the standard coefficients [15,16] and scan $\alpha_s(M_Z)$ over the range $[0.01, 0.16]$ while fixing the other couplings at their measured values. For each value of $\alpha_s$, we integrate and compute both (1) and $L_{\text{LVS}}$.

**Results.**
- Minimum of $S_{\text{LVS}}$: $\alpha_s(M_Z) = 0.048$
- Minimum of $L_{\text{LVS}}$: $\alpha_s(M_Z) = 0.049$
- Measured value [17]: $\alpha_s(M_Z) = 0.1179 \pm 0.0010$

Both metrics identify the same global minimum region, far from the measured value. For $\alpha_s(M_Z) < 0.04$, $y_t$ encounters a Landau pole before reaching $M_{Pl}$, confirming that the identified minimum is not a boundary artifact.

### 2.3 Conclusion

The measured SM parameters do not minimize $S_{\text{LVS}}$ or $L_{\text{LVS}}$. **The strong form of LVS, as a global variational principle over the SM RG flow, is falsified.**

This is a robust negative result that narrows the space of viable LVS formulations.

---

## 3. Boundary-Condition LVS at the Planck Scale

### 3.1 Weaker formulation

A weaker form of LVS requires stationarity only at the ultraviolet boundary:

$$\beta_i(\mu = M_{Pl}) = 0 \quad \text{for all couplings } i. \quad (2)$$

Within pure SM running, condition (2) is not satisfied: $\beta_{g_3}(M_{Pl}) \neq 0$ and $\beta_{y_t}(M_{Pl}) \neq 0$. If LVS is to hold, additional ultraviolet physics must cancel these contributions.

### 3.2 Coupling to asymptotic safety

In the asymptotically safe gravity framework [9–11,18], quantum gravity induces gauge- and Yukawa-dependent anomalous dimensions. Following Eichhorn & Held [4], the modified beta functions read:

$$\beta_{g_i} = \beta_{g_i}^{\text{SM}} - G_N \, g_i \, f_g(\Lambda) \quad (3)$$

$$\beta_{y_t} = \beta_{y_t}^{\text{SM}} + G_N \, y_t \, f_y(\Lambda) \quad (4)$$

where $G_N$ and $\Lambda$ are the dimensionless Newton coupling and cosmological constant, and $f_g(\Lambda)$, $f_y(\Lambda)$ are threshold functions of the gravitational coupling.

### 3.3 LVS requirement

Imposing condition (2) together with (3)–(4) at $\mu = M_{Pl}$, using the Buttazzo et al. [2] extrapolated SM values $(g_1, g_2, g_3, y_t)|_{M_{Pl}}$:

$$f_g^{\text{LVS}} \approx 0.010, \quad f_y^{\text{LVS}} \approx 0.013 \quad (5)$$

These are the values that quantum gravity *would need to supply* for LVS to hold as a boundary condition. They are not predictions of LVS in isolation, but *conditional deductions* contingent on the LVS hypothesis.

### 3.4 Epistemological caveat

It must be emphasized that any framework requiring $\beta$-function cancellation at $M_{Pl}$ via quantum-gravity corrections will require anomalous dimensions of order $10^{-2}$ by simple dimensional analysis: since $\beta_{g_i}^{\text{SM}}(M_{Pl}) \sim 10^{-2}$ and $g_i(M_{Pl}) \sim 0.5$, cancellation requires $f \sim 10^{-2}$. This ordering is therefore not a distinctive signature of LVS.

---

## 4. Comparison with Current Asymptotic Safety Estimates

### 4.1 Eichhorn-Held fixed-point values

The Eichhorn-Held analysis [4] uses a truncated FRG calculation with SM matter content ($N_S = 4$ scalars, $N_V = 12$ gauge fields, $N_W = 45$ Weyl fermions), following Donà-Eichhorn-Percacci [18]. Within this truncation:

$$G_N^* = 3.29, \quad \Lambda^* = -4.51 \quad \text{(Eichhorn-Held Eq. 9)} \quad (6)$$

Note that $\Lambda^* = -4.51$ is markedly different from pure Einstein-Hilbert gravity (where $\Lambda^* \sim +0.2$); the inclusion of SM matter pushes the cosmological constant strongly negative, as established in [18] and required for the observationally viable regime of [4].

Evaluating the threshold functions (Eichhorn-Held Eqs. 3 and 5):

$$f_g(\Lambda^*) = \frac{5(1 - 4\Lambda^*)}{18\pi(1-2\Lambda^*)^2} \approx 0.01677 \quad (7)$$

$$f_y(\Lambda^*) = \frac{96 + \Lambda^*(-235 + \Lambda^*(103 + 56\Lambda^*))}{12\pi(3 + 2\Lambda^*(-5+4\Lambda^*))^2} \approx -0.00113 \quad (8)$$

The effective dimensions, with $G_N^*$ factored explicitly per Eqs. (3)–(4):

$$f_g^{\text{AS}} = G_N^* \cdot f_g(\Lambda^*) \approx 0.055 \quad (9)$$

$$f_y^{\text{AS}} = -G_N^* \cdot f_y(\Lambda^*) \approx 0.0037 \quad (10)$$

### 4.2 Comparison

Comparing (5) with (9)–(10):

| Quantity | LVS requirement | Eichhorn-Held AS | Ratio |
|----------|-----------------|-------------------|-------|
| $f_g$    | $\approx 0.010$ | $\approx 0.055$   | 5.5   |
| $f_y$    | $\approx 0.013$ | $\approx 0.004$   | 0.30  |

### 4.3 Status

**The quantitative mismatch is significant but must be weighed against systematic uncertainty.** Eichhorn-Held explicitly state [4]: *"Including variations of $G_N^*$, $\Lambda^*$ induced by changes of the regulator underlying the functional RG implementation according to Tab. I in [18] leads to changes of up to 60% in the fixed-point values."*

With this uncertainty, the LVS value $f_g^{\text{LVS}} = 0.010$ lies outside the one-sigma range of current FRG estimates; $f_y^{\text{LVS}} = 0.013$ differs from FRG by a factor larger than the quoted uncertainty but in a regime where the sign of $f_y$ is already discussed as sensitive to truncation choices.

**LVS is therefore neither confirmed nor conclusively refuted by current AS calculations.** The framework survives within the stated systematic uncertainty but will be tested sharply as FRG truncations improve.

---

## 5. Discussion

### 5.1 What LVS does not do

In its current form, LVS does not:

1. **Mechanistically explain the Higgs near-criticality.** Unlike the Shaposhnikov-Wetterich [3] derivation from asymptotic safety, LVS takes $\lambda(M_{Pl}) \approx 0$ and $\beta_\lambda(M_{Pl}) \approx 0$ as inputs and offers a reinterpretation, not a derivation.

2. **Produce differential predictions distinguishing it from asymptotic safety or other UV completions.** The conditional deduction $f \sim 10^{-2}$ follows from dimensional analysis for any model imposing stationarity at $M_{Pl}$.

3. **Possess a complete mathematical formalism.** No LVS action or master equation currently exists from which the stationarity principle could be derived or from which further consequences could be extracted.

### 5.2 What LVS does

LVS offers:

1. **A unified interpretive frame** connecting several observed fixed-point phenomena (Higgs near-criticality, infrared quasi-fixed points, asymptotic safety) under a single ontological principle.

2. **A conditional deduction** ($f_g, f_y \sim 10^{-2}$) that provides a benchmark for future FRG calculations.

3. **A methodological demonstration** that the simplest "global variational" form of LVS is falsified (Section 2), narrowing the space of viable formulations.

### 5.3 Status

We position LVS as a **research program in its early phase** and an **interpretive framework**, not as a predictive theory comparable to supersymmetry or string theory. The latter possess complete formalisms, extensive communities, and differential predictions (even if experimentally unverified); LVS currently has none of these.

Specifically, the status assessment in Table 1 clarifies where LVS stands:

| Criterion | Supersymmetry / Strings | LVS (current) |
|-----------|------------------------|---------------|
| Master equation / action | Yes | No |
| Differential predictions | Yes (unverified) | No |
| Community size | $10^3$–$10^4$ | 1 |
| Peer-reviewed papers | $10^4$+ | 0 (this preprint) |
| Development time | 40–50 years | $\sim$1 year |

### 5.4 Open problems

For LVS to become a predictive framework, the following must be developed:

1. **A formal variational principle.** An "LVS action" whose extremization yields the stationarity condition, and which can be quantized or deformed to produce falsifiable consequences.

2. **Independent derivation of $f_g, f_y$.** Currently these values are deduced from LVS given the measured SM couplings. A derivation from first principles within the LVS framework would be required for genuine prediction.

3. **Extension beyond the gauge-Yukawa sector.** LVS should have implications for the cosmological constant, dark energy dynamics, and neutrino masses. Formulating these precisely is a major open program.

### 5.5 A falsifiable statement

Despite its immaturity, LVS in its current form makes one falsifiable claim:

> *If future FRG calculations, upon convergence of truncation schemes, establish that the gravity-induced anomalous dimensions at the Reuter fixed point satisfy $|f_g - f_g^{\text{LVS}}| \gg$ truncation uncertainty, with $f_g^{\text{LVS}} \approx 0.010$, then LVS as a Planck-scale boundary condition is refuted.*

This commits LVS to a specific numerical target and places the burden of adjudication on the asymptotic safety community's future calculations.

---

## 6. Conclusions

We have examined two formulations of the Latent Vacuum Stationarity framework. The strong form - global minimization of the RG flow length - is numerically falsified by the measured value of $\alpha_s(M_Z)$. The weaker form - stationarity as a Planck-scale boundary condition - yields a conditional deduction $f_g \sim f_y \sim 10^{-2}$ for the gravity-induced anomalous dimensions. Current FRG estimates from Eichhorn & Held (2018) give $f_g \approx 0.055$ and $f_y \approx 0.004$, differing from LVS requirements by factors of 3–5. Given the $\sim$60% truncation uncertainty acknowledged in current AS calculations, LVS is neither confirmed nor definitively refuted.

We emphasize that LVS in its current form is not a predictive theory. It is an interpretive framework compatible with the Higgs near-criticality observed by Buttazzo et al. [2] but not mechanistically explanatory of it. Its conditional deduction $f \sim 10^{-2}$ is not a distinctive signature but a generic consequence of dimensional analysis for any boundary-condition framework at $M_{Pl}$.

The scientific value of this work is threefold: (i) the falsification of global LVS is a rigorous negative result; (ii) the identification of a conditional testability window against future FRG refinements; (iii) the articulation of a conceptual framework that unifies several observed fixed-point phenomena under a single principle.

Future progress requires convergence of FRG truncations in asymptotic safety (so that $f_g^{\text{AS}}$ and $f_y^{\text{AS}}$ can be compared to LVS with reduced systematic error) and the development of a genuine LVS formalism with an associated action or master equation. Without these, LVS remains at the level of a research program hypothesis.

---


## References

[1] G. Degrassi et al., "Higgs mass and vacuum stability in the Standard Model at NNLO," JHEP **08** (2012) 098 [arXiv:1205.6497].

[2] D. Buttazzo, G. Degrassi, P. P. Giardino, G. F. Giudice, F. Sala, A. Salvio, A. Strumia, "Investigating the near-criticality of the Higgs boson," JHEP **12** (2013) 089 [arXiv:1307.3536].

[3] M. Shaposhnikov and C. Wetterich, "Asymptotic safety of gravity and the Higgs boson mass," Phys. Lett. B **683** (2010) 196 [arXiv:0912.0208].

[4] A. Eichhorn and A. Held, "Top mass from asymptotic safety," Phys. Lett. B **777** (2018) 217 [arXiv:1707.01107].

[5] F. L. Bezrukov and M. Shaposhnikov, "The Standard Model Higgs boson as the inflaton," Phys. Lett. B **659** (2008) 703 [arXiv:0710.3755].

[6] G. F. Giudice, "Naturally speaking: The naturalness criterion and physics at the LHC," in *Perspectives on LHC Physics* (2008) [arXiv:0801.2562].

[7] B. Pendleton and G. G. Ross, "Mass and mixing angle predictions from infrared fixed points," Phys. Lett. B **98** (1981) 291.

[8] C. T. Hill, "Quark and lepton masses from renormalization group fixed points," Phys. Rev. D **24** (1981) 691.

[9] S. Weinberg, "Ultraviolet divergences in quantum theories of gravitation," in *General Relativity: An Einstein Centenary Survey*, eds. S. W. Hawking and W. Israel (Cambridge, 1979), 790.

[10] M. Reuter, "Nonperturbative evolution equation for quantum gravity," Phys. Rev. D **57** (1998) 971 [hep-th/9605030].

[11] M. Reuter and F. Saueressig, *Quantum Gravity and the Functional Renormalization Group* (Cambridge, 2019).

[12] B. S. DeWitt, "Quantum theory of gravity. I. The canonical theory," Phys. Rev. **160** (1967) 1113.

[13] D. N. Page and W. K. Wootters, "Evolution without evolution: Dynamics described by stationary observables," Phys. Rev. D **27** (1983) 2885.

[14] E. Moreva et al., "Time from quantum entanglement: An experimental illustration," Phys. Rev. A **89** (2014) 052122.

[15] M. E. Machacek and M. T. Vaughn, "Two-loop renormalization group equations in a general quantum field theory. III: Scalar quartic couplings," Nucl. Phys. B **249** (1985) 70.

[16] M.-X. Luo and Y. Xiao, "Two-loop renormalization group equations in the Standard Model," Phys. Rev. Lett. **90** (2003) 011601 [hep-ph/0207271].

[17] Particle Data Group (R. L. Workman et al.), "Review of Particle Physics," Prog. Theor. Exp. Phys. **2024** (2024) 083C01.

[18] P. Donà, A. Eichhorn, R. Percacci, "Matter matters in asymptotically safe quantum gravity," Phys. Rev. D **89** (2014) 084035 [arXiv:1311.2898].

---

*Submitted to arXiv [hep-th]. Corresponding author: Fabien Polly, [email].*

*This preprint has not undergone peer review. Feedback from the community is welcomed.*