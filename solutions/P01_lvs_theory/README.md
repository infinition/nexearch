---
id: "P01"
name: "LVS Theory (Latent Vacuum Stationarity)"
abbreviation: LVS
domains: [physics, math]
category: physics-inspired
type: theory
status: limited
date_created: 2024
last_updated: 2026-04-24
author: Fabien
tags: [fixed-point, vacuum, stationarity, quantum-gravity, time-emergence, higgs, cosmology, JWST, Wheeler-DeWitt, Page-Wootters, asymptotic-safety, Coleman-Weinberg, symmetry-breaking, mass-frequency, dark-energy, non-locality, dimensionality, falsification, renormalization-group, Eichhorn-Held]
validation_tests_passed: 6
validation_tests_supported: 3
validation_tests_total: 9
global_flow_hypothesis_status: falsified
global_flow_alpha_s_optimum: 0.048
global_flow_alpha_s_measured: 0.1179
planck_bc_f_g_required: 0.010
planck_bc_f_y_required: 0.013
eichhorn_held_f_g: 0.055
eichhorn_held_f_y: 0.004
frg_truncation_uncertainty_pct: 60
higgs_mass_prediction_gev: 126
higgs_mass_measured_gev: 125.25
core_principle: "Observable reality corresponds to fixed points of the quantum vacuum landscape. Stability IS existence. It from Fix."
key_equation: "beta_i(M_Pl) = 0 (Planck-scale boundary condition, conditional deduction f_g, f_y ~ 1e-2)"
arxiv: null
paper_status: draft
github: null
builds_on: []
enables: ["002"]
related_to: ["001"]
---

# P01 - LVS Theory (Latent Vacuum Stationarity)

> **Status update 2026-04-24:** after a methodological audit (see `rigorous_2026_04/`), the strong "predictive" framing was retired. The *global* RG-flow minimization hypothesis is **falsified**. The *Planck-scale boundary-condition* formulation survives as a **conditional deduction** (not an exclusive prediction). Biased explorations from earlier iterations moved to `archives_biased_explorations/`.

## TL;DR
Meta-interpretive physics framework: **observable reality = fixed points of the quantum vacuum**. Unifies fine-tuning, measurement problem, and time emergence through one principle: **stability IS existence** ("It from Fix"). Synthesis of Asymptotic Safety + Page-Wootters + Coleman-Weinberg. Compatible with Higgs near-criticality (Buttazzo et al. 2013) but **does not mechanistically derive it**. Current status: interpretive framework / early-phase research programme, neither confirmed nor conclusively refuted by current FRG calculations.

## Current (rigorous) scientific status - April 2026

| Hypothesis tested | Result |
|---|---|
| Global RG-flow action minimization across M_Z -> M_Pl | **Falsified** (min at alpha_s = 0.048, measured 0.1179) |
| Planck-scale boundary condition beta_i(M_Pl) = 0 | Conditional deduction: requires f_g ~ 0.010, f_y ~ 0.013 from QG |
| Eichhorn-Held 2018 FRG values (f_g = 0.055, f_y = 0.004) | Factor 3-5 mismatch; within 60% truncation uncertainty |
| Robustness across 3 stationarity metrics | Passes (sigma1, sigma2, sigma3 agree) |
| Yukawa-sector residue | Any LVS must constrain gauge AND Yukawa jointly |

See [`rigorous_2026_04/LVS_Scientific_Status.md`](rigorous_2026_04/LVS_Scientific_Status.md) for the one-page status and [`rigorous_2026_04/LVS_Paper_Draft.md`](rigorous_2026_04/LVS_Paper_Draft.md) for the current preprint.

---

## Evolution of Thinking (Chronological)

### Phase 1 - The Spark (March 2026)
A YouTube video about consciousness and quantum mechanics. One fact hit differently: **the photon does not experience time**. `d(tau) = dt * sqrt(1 - v^2/c^2)` -> for v=c, d(tau) = 0. The mediator of ALL observation exists outside time.

### Phase 2 - The Chain of Reasoning
Five established facts leading to one hypothesis:
1. **(SR)** Spacetime interval along null geodesics = 0. Photon is atemporal.
2. **(QED)** All macroscopic observation is electromagnetic. We see through a timeless mediator.
3. **(QFT)** The quantum vacuum is a superposition of all field configurations.
4. **(CQG)** Wheeler-DeWitt: `H|Psi> = 0` - the universe has no time variable.
5. **(QM)** Stationary states are time-independent eigenstates.
6. **(LVS)** Observable reality = fixed points of the vacuum landscape.

### Phase 3 - Paper v1
Formalized as meta-interpretive framework. Distinguished: (a) established physics, (b) interpretive steps, (c) LVS extrapolations. Built 5 interactive visualizations (Three.js, then migrated to Jupyter).

### Phase 4 - Validation
9-test empirical scorecard: 6 confirmed, 3 supported, 0 in tension. But honest reassessment: compatibility with known data is the MINIMUM bar for any reinterpretation.

### Phase 5 - Formalization Attempt
Discovered LVS is essentially a SYNTHESIS of three existing programs:
- **Asymptotic Safety** (Weinberg 1979 -> Reuter -> Eichhorn): UV fixed point of gravity
- **Coleman-Weinberg** (1973): Masses from potential curvature at minimum
- **Page-Wootters** (1983 -> Hoehn): Time emergence from static state

Key discovery: **Shaposhnikov-Wetterich (2010) predicted m_H = 126 GeV** from a fixed-point condition BEFORE the LHC discovery. This is the strongest result supporting LVS.

### Phase 6 - Honest Self-Critique
Acknowledged AI sycophancy bias. Acknowledged that the connected programs themselves are NOT proven (47, 43, and 53 years old respectively). LVS does not yet predict anything the Standard Model doesn't.

### Phase 7 - "The Framework IS the Problem"
Radical pivot: the problem of unification may be that different physics use **incompatible mathematical frameworks** (Hilbert space vs. Riemannian geometry vs. gauge fiber bundles). The real breakthrough would be finding the framework itself, not another equation within existing frameworks.

### Phase 8 - Symmetry Breaking Cascade
The universe as a cascade of symmetry breakings from a perfectly symmetric initial state. Space, time, constants as "scars" of the breaking. The pre-breaking state has no dimensions.

### Phase 9 - Mass = Frequency
`f = mc^2/h`. Every particle is its own clock. Gravity IS the desynchronization between clocks. Connects to Jacobson (1995), Verlinde (2011), Connes-Rovelli thermal time (1994).

### Phase 10 - LVS v3 Reformulation
An infinite set of featureless points. Interaction between points creates links (photons, gluons). The network of links IS observable reality. Dark energy doesn't exist - it's the non-interacting latent space. 3 dimensions emerge as the only stable network topology.

### Phase 11 - Essay "Du Point Fixe au Point de Rupture"
Complete intellectual journal documenting the entire journey: from the photon question through calculations, impasses, honest self-assessment, to the framework's limits and what remains.

### Phase 12 - Predictive Reformulation and Its Fall (April 2026)
An aggressive reformulation tried to turn LVS from interpretation into prediction by coupling it to Asymptotic Safety and deducing f_g = 0.010585, f_y = 0.013540 from a 2-loop inversion. Accompanying GPU simulations claimed spontaneous emergence of d=3, SU(3)xSU(2)xU(1), and the DESI w0/wa anomaly. Material preserved in `archives_biased_explorations/`.

### Phase 13 - Methodological Reset (April 2026)
A strict audit identified AI sycophancy and confirmation bias in Phase 12. Corrections applied:
1. **Robustness test**: three stationarity metrics (sigma1 absolute, sigma2 relative, sigma3 sub-linear) tested side-by-side. The previous "50% partial LVS optimum" evaporated - it was a metric artifact.
2. **Global flow falsified**: `int sum(beta^2) dt` from M_Z to M_Pl is minimized at alpha_s = 0.048, far from the measured 0.1179. The strong form of LVS as a global variational principle is dead.
3. **Eichhorn-Held audit**: ran the threshold functions from arXiv:1707.01107 with the paper's own (G_N*, Lambda*) = (3.29, -4.51). Got f_g^AS = 0.055, f_y^AS = 0.0037 - factor 3-5 away from the LVS-required 0.010 and 0.013. Within the ~60% truncation uncertainty, so not a refutation yet, but not a confirmation either.
4. **Honest reframing**: LVS is a conditional deduction generator, not a prediction machine. Dimensional analysis alone gives f ~ 1e-2 for ANY boundary-condition scheme at M_Pl.

Current paper (`rigorous_2026_04/LVS_Paper_Draft.md`): a rigorous negative result on 1-loop gauge-coupling stationarity, identifying three directions for a future predictive LVS (full asymptotic safety, joint gauge-Yukawa stationarity, Wilsonian extrema).

---

## Core Equations

**1. Wheeler-DeWitt (timeless substrate):**
$$\hat{H}|\Psi\rangle = 0$$

**2. LVS Master Equation (self-consistency):**
$$\Psi = F[\Psi]$$
The universe is the fixed point of itself.

**3. Principle of Stationary Action (unifies ALL physics):**
$$\delta S = 0$$

**4. Higgs mass from fixed-point condition (Shaposhnikov-Wetterich 2010):**
$$\lambda(M_{Pl}) = 0 \quad \text{AND} \quad \beta_\lambda(M_{Pl}) = 0 \implies m_H \approx 126 \text{ GeV}$$

**5. Page-Wootters time emergence:**
$$|\psi(t)\rangle_S = C\langle t|\Psi\rangle$$

**6. RG fixed points (physical constants = coordinates):**
$$\beta(g) = 0 \implies \text{scale-invariant theory}$$

**7. Mass-frequency equivalence:**
$$f = mc^2 / \hbar$$

**8. Top quark quasi-fixed-point ratio:**
$$y_t^2 \sim \frac{8}{9} g_3^2 \quad \text{(2.7\% from exact)}$$

**9. Minimal temporal resolution (novel LVS prediction):**
$$\Delta t_{min} \sim \hbar / (m_\nu c^2) \sim 10^{-14} \text{ s}$$

**10. Lambda from holographic relation:**
$$\Lambda \sim 1/N_{surf} \quad \text{where } N_{surf} \sim 10^{122}$$

---

## What LVS Explains

| Problem | LVS Explanation | Strength |
|---------|----------------|----------|
| Fine-tuning | Constants are properties of a self-consistent fixed point, not "tuned" | Strong |
| Measurement problem | Outcomes persist when recorded in stationary macroscopic configurations | Strong |
| Problem of time | Emerges from internal correlations (Page-Wootters) in globally static state | Strong |
| Mass origin | Confined interaction energy = depth of a fixed point (proton = 99% QCD) | Strong |
| Gravitational time dilation | Proximity to deep fixed points = approach to atemporal substrate | Strong |
| Non-locality (Bell) | Correlated features of a single global fixed point; space is emergent | Strong |
| JWST early galaxies | Fixed points manifest where stationarity is satisfied, not by accretion | Medium |
| Cosmological expansion | Progressive actualization of vacuum configuration space | Speculative |
| Dark energy | Non-interacting latent space, not a substance | Speculative |
| d=3 spatial dimensions | Only stable network topology (Ehrenfest + quantum + Huygens + knots) | Medium |
| Anthropic principle | Dissolved - constants are structurally co-defined with observers | Medium |

---

## Empirical Validation (9 tests)

| # | Test | Result | Status |
|---|------|--------|--------|
| 1 | Hadron masses vs lattice QCD | R2 = 0.999998 | CONFIRMED |
| 2 | Proton mass = 99% interaction energy | Yang 2018 | CONFIRMED |
| 3 | Hadron lifetime hierarchy | 64 orders correlation | CONFIRMED |
| 4 | RG coupling convergence | Near GUT scale | SUPPORTED |
| 5 | JWST early massive galaxies | 8/8 explained | ADVANTAGE |
| 6 | Page-Wootters experimental | Moreva 2014 | CONFIRMED |
| 7 | Neutrino seesaw hierarchy | M_R ~ GUT scale | SUPPORTED |
| 8 | Bell inequality violations | 8/8 experiments | CONFIRMED |
| 9 | Antimatter gravity ALPHA 2023 | g_anti = g +/- 0.3% | CONFIRMED |

**Score: 6 confirmed, 3 supported, 0 in tension**

**Additional quantitative results:**
- 1-loop Higgs prediction: m_H ~ 136 GeV (8.6% from experiment; 2-loop gives 126 GeV)
- Top quark quasi-fixed-point: y_t^2 ~ (8/9)g_3^2 (2.7% deviation)
- Lambda prediction (Fisher-KPP): Lambda_pred/Lambda_obs = 1.08 (but may be tautological)

---

## Testable Predictions

| # | Prediction | Testability | Status |
|---|-----------|-------------|--------|
| 1 | Higgs mass ~ 126 GeV | Already confirmed (LHC 2012) | Confirmed |
| 2 | Top quark quasi-fixed-point ratio | Already confirmed (2.7% match) | Confirmed |
| 3 | Antimatter falls like matter | Confirmed (ALPHA 2023) | Confirmed |
| 4 | Temporal resolution limit: dt_min ~ hbar/(m_nu c^2) | Not yet testable | Novel |
| 5 | Lambda evolves (w != -1) if interaction front slows | DESI hints at 2-3 sigma | Testable |
| 6 | Non-Gaussian CMB features from fixed-point selection | Planck/future missions | Testable |
| 7 | Modified dispersion near Planck scale | High-energy astrophysics | Future |
| 8 | Hawking radiation encodes fixed-point structure | Theoretical | Far future |
| 9 | All 80+ hadron masses from QCD stationarity | Lattice QCD | Testable |
| 10 | Muon g-2 compatible either way | Fermilab ongoing | Compatible |

---

## Connections to Other Physics

| Field | Connection | Key Reference |
|-------|-----------|---------------|
| Asymptotic Safety | UV fixed point of gravity = LVS foundation | Weinberg 1979, Reuter 1998, Eichhorn |
| Coleman-Weinberg | Masses from potential curvature at minimum | Coleman-Weinberg 1973 |
| Page-Wootters | Time emergence from static state | Page-Wootters 1983, Moreva 2014 |
| Shaposhnikov-Wetterich | Higgs mass from lambda(M_Pl)=0 | Phys Lett B 683 (2010) |
| Connes NCG | SM gauge group from algebra C+H+M_3(C) | Connes 1996 (but m_H=170 wrong) |
| Jacobson | Einstein equations from horizon thermodynamics | Jacobson 1995 |
| Verlinde | Gravity as entropic force | Verlinde 2011 |
| Connes-Rovelli | Thermal time hypothesis | Connes-Rovelli 1994 |
| ER=EPR | Space from entanglement | Maldacena-Susskind 2013 |
| Holography/AdS-CFT | Information on boundary | Maldacena 1997 |
| Causal Sets | Discrete spacetime events | Sorkin 1987 |
| Hartle-Hawking | No-boundary proposal | Hartle-Hawking 1983 |
| Barbour | Timeless physics | Barbour "End of Time" |

---

## Honest Assessment: What LVS Is and Is NOT

### What LVS IS:
- A **synthesis** of Asymptotic Safety + Page-Wootters + Coleman-Weinberg
- A **meta-interpretive framework** (like Many-Worlds or QBism for QM)
- **Compatible** with all known physics (but that's the minimum)
- An **organizing principle** ("It from Fix") that makes disparate physics coherent

### What LVS is NOT (yet):
- NOT a **complete dynamical theory** (no Lagrangian, no new equations of motion)
- NOT **falsifiable** beyond SM predictions (the critical test it hasn't passed)
- NOT proven that the underlying programs (AS, PW, CW) are correct (47+ years each)
- NOT the first to make any of its "predictions" (Shaposhnikov published m_H first)

### Known Weak Points:
| Claim | Assessment | Rating |
|-------|-----------|--------|
| Photon argument (Section 2) | Pedagogical, not foundational. Formalization never uses it. | Weak |
| Cosmological expansion = actualization | No formalism found. Fisher-KPP is analogy only. | 20% |
| Dark energy = actualization tendency | No support from any formalism. Most speculative. | Speculative |
| JWST "naturally explained" | Overstatement. No quantitative calculation. | 30% |
| Validation scorecard | Compatibility != explanation. Minimum bar. | Honest |

---

## Failed Approaches and Dead Ends

| Approach | What happened | Lesson |
|----------|---------------|--------|
| HTML/Three.js visualizer | "Fake physics" - shapes not computed | Migrated to Jupyter with real equations |
| Page-Wootters first attempt | sigma_z oscillated 0 to 0 (degenerate) | Need N-level clock (32 levels min) |
| Gravitational corrections to Higgs | a_grav, b_grav too crude, nonsensical | Need proper 2-loop calculation |
| Fisher-KPP for Lambda | Lambda_pred/Lambda_obs = 1.08 | Tautological (= Friedmann equations) |
| Connes NCG Higgs prediction | 170 GeV (WRONG, corrected post-hoc) | NCG program has issues |
| Expressing LVS in existing frameworks | Hilbert/Riemannian/fiber bundles all inadequate | Maybe need fundamentally new framework |
| Photon argument as foundational | Formalization showed it plays no role | Pedagogical only, not structural |
| Proving AS / extending PW to full QG | Hundreds of physicists tried for decades | Not realistic for one person |
| **Global RG-flow minimization (2026-04)** | alpha_s_opt = 0.048 vs measured 0.1179 | Strong LVS falsified; only Planck-BC form survives |
| **"Partial 50% LVS optimum"** | Robustness test with 3 metrics showed it was an artifact | Always test against multiple metrics |
| **"LVS predicts f_g = 0.010585 exactly"** (Phase 12) | Dimensional analysis gives f ~ 1e-2 for ANY BC scheme | Not a distinctive LVS signature |
| **GPU sim of d=3 / SU(3)xSU(2)xU(1) / DESI** (Phase 12) | Potentials/ICs tuned toward target answers | Confirmation bias - archived in `archives_biased_explorations/` |

---

## Files (self-contained)

### source_docs/ - Theory Documents
| File | Content | Size |
|------|---------|------|
| `LVS_Paper_v2.md` | **Main paper** - 13 sections, complete theoretical exposition | 60 KB |
| `discussion.md` | **Critical analysis** - evolution of thinking, honest assessment, all open questions | 130 KB |
| `LVS_reference.pdf` | Reference PDF | 7.7 MB |

### notebooks/ - Computational Work
| File | Key Result |
|------|------------|
| `LVS_Formalization.ipynb` | **STRONGEST**: Shaposhnikov-Wetterich m_H = 126 GeV |
| `LVS_Validation.ipynb` | 9 empirical tests: 6 confirmed, 3 supported |
| `LVS_Experiments.ipynb` | RG flows, Higgs stability, Page-Wootters simulation |
| `LVS_Calculations.ipynb` | Why d=3 is special (orbital + quantum + Huygens + knot stability) |
| `LVS_Visualizations.ipynb` | QCD landscape, RG flow, crystallization, time emergence, Schwarzschild |
| `*_executed.ipynb` | All notebooks with outputs preserved |

### web/ - Web Presentations
| File | Content |
|------|---------|
| `LVS_Article.html` | Accessible article (English, 57KB) |
| `LVS_Visualizer.html` | Interactive 5-scene physics visualizer (48KB) |
| `LVS_Essay_Du_Point_Fixe_au_Point_de_Rupture.html` | **Complete intellectual journal** (French, 87KB) - from the photon question through calculations, impasses, honest self-critique, to limits |

### writeups/
| File | Type | Size | Language |
|------|------|------|----------|
| `Du Point Fixe au Point de Rupture.md` | Book (20 chapters) | 63 KB | French |
| `Et_si_lunivers_etait_en_pause.md` | Article (vulgarisation) | 38 KB | French |
| `it_from_fix.md` | Essay | 4 KB | English |

### paper/ - CURRENT RIGOROUS PAPER
- `paper/main.tex` - **Current preprint** "Latent Vacuum Stationarity as a Boundary Condition at the Planck Scale: A Conditional Framework" (the rigorous paper v4)
- `paper/lvs-preprint.md` - Markdown source of the same preprint
- `paper/refs.bib` - BibTeX references
- `paper/main_skeleton_v1.tex` - Original 2024 skeleton (kept for provenance)

### results/
- `validation_tests.json` - 9 empirical tests
- `global_flow_falsification.json` - April 2026 alpha_s scan result (falsification of strong LVS)
- `eichhorn_held_comparison.json` - f_g, f_y comparison with Eichhorn-Held 2018
- `stationarity_metric_robustness.json` - 3-metric agreement test

### LVS_Master_Synthesis.md (top level)
Research synthesis. Summarises the shift from interpretation to conditional prediction and what the computational substrate (FPS) was meant to demonstrate. Read alongside `rigorous_2026_04/LVS_Scientific_Status.md` for epistemic calibration.

### rigorous_2026_04/ - METHODOLOGICAL AUDIT (read for provenance)
- `LVS_Scientific_Status.md` - One-page honest status
- `LVS_Paper_Draft.md` - Intermediate early draft (superseded by `paper/`)
- `scripts/rigorous_alpha_s_test.py` - Falsification of global flow
- `scripts/verify_eichhorn_held.py` - f_g, f_y reproduction from Eichhorn-Held
- `scripts/metric_robustness.py` - 3-metric robustness test
- `notebooks/LVS_Final_Notebook.ipynb` - Reproduces all figures
- `references/` - Eichhorn-Held arXiv:1707.01107 source material

### archives_biased_explorations/ - Retired for confirmation bias
- `paper_v3_predictive/` - Paper v3 draft with overclaimed predictions (retired)
- `advanced_experiments/` - DESI/2-loop/SU321 GPU experiments tuned toward target answers
- `simulations_FPS/` - FPS emergent-dimension GPU sims (tuned, not blind)
- `scripts_legacy/` - Voie 1/2/3 notebooks from predictive-framing phase

---

## Key Quotes

> "Observable physical reality corresponds to the set of stationary configurations - fixed points - of the quantum vacuum configuration space."

> "Stability is not a property that some configurations happen to possess; it is the criterion of physical existence."

> "Time is the relational cost of being a local observer in an atemporal whole."

> "The universe exists not because it was created, designed, or selected, but because it is the configuration that satisfies its own conditions of existence. It is the answer that is its own question."

> "The problem is not that we cannot find the right equation. It is that we are looking for the equation on the wrong type of paper."

> "Reinventing the wheel is not nonsensical if the current wheel does not roll."

---

## Cross-References

- **Enables [002 Fixed-Point Substrate](../002_fixed_point_substrate/):** FPS is the computational realization of LVS's "reality from fixed points"
- **Related to [001 Entropy-Gated Learning](../001_entropy_gated_learning/):** Both explore non-gradient paradigms
- **Potential links to quantum computing:** Fixed-point structure in quantum error correction
- **Potential links to cryptography:** Lattice-based PQC and fixed-point iteration

---

## Next Steps / Roadmap (rewritten 2026-04-24 under rigorous methodology)

### Priority 1 - Lock in the negative result (current preprint)
- [x] Falsify global RG-flow minimization (done - scripts/rigorous_alpha_s_test.py)
- [x] Pass 3-metric robustness test (done - scripts/metric_robustness.py)
- [x] Reproduce Eichhorn-Held f_g, f_y (done - scripts/verify_eichhorn_held.py)
- [ ] Compute formal uncertainty on f_g^LVS, f_y^LVS given measured (M_t, alpha_s) error bars
- [ ] Validate 1-loop RGE against published Buttazzo 2013 benchmark (within 0.5%)
- [ ] Polish `rigorous_2026_04/LVS_Paper_Draft.md` and post to arXiv [hep-th] + PhilSci-Archive

### Priority 2 - Cross-check with validated tools
- [ ] Re-run 2-loop Machacek-Vaughn using SARAH / RGBeta / FlexibleSUSY (the hand-coded 2-loop had +23% deviation from Buttazzo, so it was dropped)
- [ ] Literature review: do Eichhorn, Held, Wetterich, Pawlowski publish any independent f_g, f_y estimates? Are any ~1e-2?

### Priority 3 - Three directions for a predictive LVS
- [ ] **(A) Full asymptotic safety**: reformulate LVS as "Universe at UV fixed point of ALL couplings including gravity" - inherit Shaposhnikov-Wetterich predictive power
- [ ] **(B) Joint gauge-Yukawa stationarity**: constrain Yukawa alongside gauge - may yield Pendleton-Ross-type quasi-fixed-point predictions
- [ ] **(C) Wilsonian extrema**: variational principle on theory-space, not coupling-space - needs rigorous formulation

### Priority 4 - Engagement & cross-domain (secondary until above lands)
- [ ] Submit preprint to FQXi / Foundations of Physics
- [ ] Contact Eichhorn, Hoehn, or Rovelli for expert feedback (especially on the f_g, f_y comparison)
- [ ] Formalize LVS -> FPS bridge (P01 -> 002)
- [ ] Track Euclid / DESI Year-5 for variable-Lambda hints (but do NOT fit Fisher-KPP to them - it's tautological)

### Archived (do not pursue)
- Tuned GPU simulations to "show" emergence of d=3 / SU(3)xSU(2)xU(1) / DESI w0,wa. Confirmation-bias prone; archived.
- "LVS predicts f = 0.010585 exactly" framing. It's a dimensional-analysis result, not a distinctive signature.
