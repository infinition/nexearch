---
purpose: Rigorous LVS work (April 2026) after methodological reset
date: 2026-04-24
status: current
---

# LVS - Rigorous Analysis (April 2026)

This folder contains the current, methodologically strict LVS work. Earlier explorations have been moved to `../archives_biased_explorations/` because they were done under confirmation bias.

## Key documents (read in this order)

1. **`LVS_Scientific_Status.md`** - One-page honest status. Start here.
2. **`LVS_Paper_Draft.md`** - Intermediate draft: "Testing the LVS hypothesis via 1-Loop Gauge-Coupling Running: A Rigorous Negative Result".
3. **`../paper/lvs-preprint.md`** and **`../paper/main.tex`** - **The current rigorous paper** (supersedes `LVS_Paper_Draft.md`).

## Key results (April 2026)

### Falsified
- **Global RG-flow minimization** (hypothesis: SM parameters minimize int sum(beta_i^2) dt from M_Z to M_Pl). Numerical test: the minimum sits at alpha_s(M_Z) = 0.048, incompatible with the measured 0.1179. Reproduce with `scripts/rigorous_alpha_s_test.py`.

### Robustness test (passed)
- Three stationarity metrics (sigma1 absolute, sigma2 relative, sigma3 sub-linear) agree on the same optimum -> the previous "50% partial LVS optimum" was a metric artifact that evaporated under the multi-metric test. See `figures/fig_robustness_test.png`.

### Yukawa residue
- Even when gauge beta vanishes, beta_yt remains nonzero at M_Pl. Any LVS programme must treat gauge and Yukawa jointly. See `figures/fig_yukawa_residue.png`.

### Eichhorn-Held comparison (conditional)
- Planck-scale BC LVS needs f_g ~ 0.010, f_y ~ 0.013 (dimensional analysis result, not distinctive to LVS).
- Eichhorn & Held 2018 (arXiv:1707.01107) give f_g ~ 0.055, f_y ~ 0.004 at the Reuter fixed point.
- Factor 3-5 mismatch. **LVS not confirmed**, but not definitively refuted given the ~60% truncation uncertainty in current FRG.
- Reproduce with `scripts/verify_eichhorn_held.py`.

## Contents

```
rigorous_2026_04/
+-- LVS_Scientific_Status.md      # 1-page honest status
+-- LVS_Paper_Draft.md            # Intermediate early draft (superseded by ../paper/)
+-- scripts/
|   +-- rigorous_alpha_s_test.py      # Falsification of global flow
|   +-- verify_eichhorn_held.py       # f_g, f_y reproduction from Eichhorn-Held
|   +-- metric_robustness.py          # 3-metric robustness test
|   +-- sm_rge_1loop_validated.py     # Validated 1-loop SM RGE integrator
|   +-- analytical_verification.py    # Analytical sanity checks
|   +-- final_analysis.py             # Final numerical pass
|   +-- fine_scan_sigma2.py           # Fine scan around alpha~1, Lambda=1e18
|   +-- stationarity_deep_dive.py     # Deep dive on stationarity structure
|   +-- direction2_attractor.py       # Pendleton-Ross-style IR attractor
|   +-- direction2_yukawa.py          # Yukawa-sector joint stationarity
|   +-- launch_boss_experiments.py    # Legacy experiment launcher
+-- notebooks/
|   +-- LVS_Final_Notebook.ipynb      # Main notebook (reproduces all figures)
|   +-- lvs_rg_calculation.ipynb      # RG calculation walkthrough
+-- figures/
|   +-- fig_robustness_test.png       # 3-metric agreement
|   +-- fig_yukawa_residue.png        # Yukawa residue at M_Pl
|   +-- fig_stationarity_analytical.png
|   +-- fig_ratios_stationarity.png
|   +-- fig_higgs_yukawa_final.png
|   +-- fig_final_coincidence.png
|   +-- fig_hill_attractor.png
|   +-- rigorous_alpha_s_test.png     # Falsification plot
|   +-- lvs_rg_flow.png
|   +-- lvs_unification_metric.png
+-- references/                        # Eichhorn-Held source material
|   +-- TopmassfromAS.tex             # arXiv:1707.01107 LaTeX
|   +-- SM_gravity_running_full.pdf
|   +-- Yukawa_trajectories.pdf
|   +-- gLambdacontours.pdf
+-- *.json                             # Numerical results for each script
```

## Python env

`C:/Users/infinition/miniconda3/envs/lerobot312/python.exe` (same as project default).

Dependencies: numpy, scipy, matplotlib. No GPU required for this folder (GPU-heavy FPS sims live in `../archives_biased_explorations/`).

## Honest epistemic status

LVS is **not** a predictive theory. It is:
- a research programme in its early phase,
- an interpretive framework compatible with Higgs near-criticality (Buttazzo et al. 2013),
- a **conditional deduction** generator (f_g, f_y ~ 1e-2) that can be measured against future FRG calculations.

For a paper-ready one-paragraph summary, see section 4 of `LVS_Scientific_Status.md`.
