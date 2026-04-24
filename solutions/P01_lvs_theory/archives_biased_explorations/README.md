---
purpose: Archive of LVS explorations retired for confirmation bias
archived_on: 2026-04-24
reason: Work done under AI sycophancy / confirmation bias - results overstated, methodology insufficiently adversarial. NOTE: the final rigorous paper (`paper_v4`) and the research synthesis have been PROMOTED out of this folder; only the genuinely biased material remains here.
---

# LVS - Archived Biased Explorations (intermediate iterations)

> **Start here:** the rigorous final paper lives in `../paper/` (both `main.tex` and `lvs-preprint.md`). The research synthesis is `../LVS_Master_Synthesis.md`. The rigorous scientific audit is `../rigorous_2026_04/LVS_Scientific_Status.md`. Everything in this folder is **retired** because it claimed too much or was tuned toward target answers.

## What IS in this folder (retired material)

### `paper_v3_predictive/`
Intermediate "predictive LVS" paper draft from the phase where LVS was framed as producing exact predictions. Superseded by the final rigorous preprint in `../paper/lvs-preprint.md`, which correctly presents LVS as a conditional-deduction interpretive framework.

### `advanced_experiments/`
GPU simulations claiming spontaneous emergence of:
- DESI w0/wa dark-energy anomaly (exp1_desi_fit.py) - Fisher-KPP fit tuned toward target
- Exact 2-loop inversion f_g = 0.010585, f_y = 0.013540 (exp2_2loop_inversion.py) - the *math* is fine, but calling it an LVS "prediction" is incorrect (dimensional analysis gives f ~ 1e-2 for any BC scheme)
- Gauge group SU(3)xSU(2)xU(1) emergence (exp3_matrix_SU321.py) - potentials/ICs tuned toward known answer

### `simulations_FPS/`
GPU cosmology and field-theory simulations claiming:
- Dimension 3 emergence (sim1_dimensions.py)
- Gauge-group crystallization (sim2_gpu_crystallization.py)
- Fisher-KPP cosmological expansion (sim3_fisher_kpp_expansion.py)

These demonstrate that a *tuned* model can reproduce known physics. They do NOT demonstrate that LVS predicts them ab initio.

### `scripts_legacy/`
Voie 1 / Voie 2 / Voie 3 notebooks from the predictive-framing phase. The alpha_s falsification test from this phase was redone cleanly and lives in `../rigorous_2026_04/scripts/rigorous_alpha_s_test.py`.

## What got PROMOTED out of this archive

- **`paper_v4_final/` -> `../paper/`** (main.tex and lvs-preprint.md). This is the CURRENT rigorous paper.
- **`LVS_Master_Synthesis.md` -> `../LVS_Master_Synthesis.md`**. Research synthesis document (top-level).

## Status

Read-only archive. Kept for provenance. Do NOT cite results from this folder as LVS predictions. Do NOT re-integrate without independent adversarial validation.
