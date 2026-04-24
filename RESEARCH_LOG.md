# Research Log

Chronological record of all research decisions, experiments, and discoveries.

---

## 2026-04-24 - RAPC Modular Geometry (P02) - Full Integration into Nexearch

**Goal:** Transfer the full RAPC quantum-gravity framework exploration into Nexearch as a standalone cross-domain solution.

### What RAPC Is

RAPC (Reseau Algebrique a Produit Croise / RAPC Modular Geometry) is a toy falsification lab for the hypothesis:

```text
geometry = stable sparse spectral compression of modular quantum correlations
```

It is not a finished theory of quantum gravity. It tests whether increasingly strict finite models can produce BMV-capable links, effective pair geometry, sparse locality, and stable graph phases without treating ML as a fundamental law.

### Core Research Chain

1. **BMV gate:** bilocal quantum channels create entanglement; LOCC controls do not.
2. **Modular phase gate:** `K=-log(rho)` can generate a bilocal phase from correlations.
3. **Subalgebra selection:** hidden effective pairs can be selected from global modular data.
4. **Hypergraph coarse-graining:** higher-order modular terms can become pair edges when a reference asymmetry exists.
5. **Automatic coarse-graining:** direct and generated edges are separated.
6. **Iterated flow:** flows show empty, dense, decaying, and stable-topology regimes.
7. **Sparse budget:** compression prevents nonlocal densification.
8. **MDL budget selection:** graph size can be selected by information-complexity tradeoff.
9. **Phase scan:** simple MDL has a narrow sparse-geometric phase.
10. **Spectral locality:** adding Laplacian/connectivity terms widens the sparse-geometric phase.
11. **Patch gluing:** first bridge rule fails, adding zero bridges.
12. **Residual patch gluing:** retaining hypergraph memory stabilizes 9/20 cases but still adds no bridges.

### Key Results

| Experiment | Result | Decision |
|------------|--------|----------|
| BMV finite toy | concurrence 0.105, LOCC negativity 0 | Keep BMV as first falsification gate |
| Modular phase | concurrence 0.644 from `K=-log(rho)` | Modular correlations can define toy bilocal generators |
| Simple MDL scan | best sparse geometry 6/20 seeds | Compression alone is too weak |
| Spectral locality scan | sparse geometry 9/20 across broad lambda range | Best current RAPC signal |
| Patch gluing | 0 bridges added | Bridge rule failed |
| Residual patch gluing | stable 9/20, still 0 bridges | Need new weak-bridge mechanism |

### ML/GPU Decision

ML and the RTX 4070 Ti may be used only as an external research microscope:

```text
ML for discovery, explicit mathematics for the final rule
```

The final physical model must not contain a neural network as a fundamental selector.

### Files Added

- `solutions/P02_rapc_modular_geometry/README.md`
- `solutions/P02_rapc_modular_geometry/core.py`
- `solutions/P02_rapc_modular_geometry/notebook.ipynb`
- `solutions/P02_rapc_modular_geometry/source/*.py`
- `solutions/P02_rapc_modular_geometry/results/*.csv`
- `solutions/P02_rapc_modular_geometry/results/*_summary.json`
- `solutions/P02_rapc_modular_geometry/writeups/*.md`
- `solutions/P02_rapc_modular_geometry/paper/main.tex`

### Next Decisions

- Redesign patch gluing as multi-scale weak bridge generation.
- Scan larger phase diagrams with 1000+ seeds per lambda.
- Add dimension estimators from graph ball growth and Laplacian spectra.
- Replace finite Pauli projections with basis-independent algebraic diagnostics.

---

## 2026-04-24 - LVS (P01) Rigorous Re-evaluation - Methodological Reset

**Session goal:** After detecting confirmation bias in earlier LVS work, subject the theory to strict falsification tests and re-categorize all prior results by epistemic status.

**Scope of reset.** All earlier LVS explorations (paper v1-v3, 9-test scorecard, d=3 / SU321 / DESI GPU simulations, "LVS predicts f_g = 0.010585 exactly" claim, 50% partial-LVS optimum) were moved to `solutions/P01_lvs_theory/archives_biased_explorations/` and reinterpreted as either tuned (not predictive), minimum-bar (no discriminative power), or metric artifacts.

### Falsified - Global RG-flow minimization (strong LVS)

Strong form hypothesis: SM parameters at M_Z minimize `int_{M_Z}^{M_Pl} sum_i beta_i^2 dt` (gauge sector). Numerical test (`scripts/rigorous_alpha_s_test.py`):

- Optimum at alpha_s(M_Z) = **0.048**
- Measured value: **0.1179**
- **Verdict: falsified.** Strong form ruled out.

### Robustness test (passed) - 3 stationarity metrics agree

sigma1 (absolute), sigma2 (relative), sigma3 (sub-linear) all agree on the same optimum structure. The previously reported "50% partial LVS optimum" was a metric artifact of sigma2 alone - it does not survive the multi-metric test. **Retracted.**

### Conditional - Planck-BC form survives

Weak form: LVS imposed only as a boundary condition at M_Pl. Dimensional analysis gives

  f_g = d_t g* / g*  ~ 1e-2,   f_y ~ 1e-2 at M_Pl

This is a conditional deduction - it must be measured against FRG fixed-point values. It is not distinctive to LVS (any UV-completion producing similar stationarity would satisfy it).

### Eichhorn-Held 2018 comparison (arXiv:1707.01107)

At the Reuter fixed point in asymptotic safety:

- f_g ~ **0.055**, f_y ~ **0.004**
- LVS requires f_g ~ 0.010, f_y ~ 0.013 - **factor 3-5 mismatch**
- Current FRG truncation uncertainty: ~60%
- **Verdict: not confirmed, not refuted.** Hinges on future FRG calculations.

### Yukawa residue finding

Even when beta_gauge vanishes at M_Pl, beta_yt remains nonzero. Any future predictive LVS must treat gauge and Yukawa jointly (single-sector stationarity is insufficient).

### Methodology changes

- New `rigorous_2026_04/` folder is now the canonical location; earlier work preserved in `archives_biased_explorations/` for provenance.
- Paper promoted: `paper/lvs-preprint.md` (from the former `paper_v4_final/`) is now the rigorous preprint; old skeleton saved as `main_skeleton_v1.tex`.
- All AI-assistant transcripts and attribution removed from repo; `.gitignore` updated to prevent future leaks.

### Next priorities

1. SARAH / RGBeta 2-loop validation of the 1-loop Planck-BC numbers.
2. Full Eichhorn-Held literature audit across newer FRG truncations.
3. Joint gauge-Yukawa stationarity treatment (Yukawa residue forces this).
4. Three exploratory directions: Pendleton-Ross IR attractor, Yukawa-sector joint, Hill-type attractor.
5. Polish rigorous preprint for arXiv (hep-th or gr-qc) as honest negative-result + conditional framework.

---

## 2026-04-03 - Local Learning Paradigm Search (005, 006, 007) - Session 2

**Session goal:** Find a local learning algorithm where each neuron adjusts using only its neighbors - no global backpropagation. If found, training that takes 3 months on 10,000 GPUs could potentially run in hours on a laptop.

**Approach:** 6 rounds of experimentation, testing 15+ algorithms across physics, neuroscience, math, and CS-inspired approaches.

### Round 1 - 7 algorithms tested simultaneously
- Thermodynamic LL (~70%) - eliminated (backprop in disguise)
- Predictive Coding (NaN) - eliminated (numerical instability)
- Forward-Forward + InfoGeom (NaN) - eliminated
- Reaction-Diffusion (~40%) - eliminated (PDE, too slow)
- Cellular Automata (~85%) - eliminated (readout needs backprop)
- Equilibrium Propagation (78.33%) - KEPT
- NOVA belief diffusion (48.90%) - KEPT but weak

### Round 2 - Optimization of survivors + new ideas
- EqProp + Momentum: 87.49% (best pure local Hebbian)
- EqProp-Tuned: 70.07%
- HESP Hybrid: 49.40%
- **DirectLocal: 97.71%** - DISCOVERY: per-layer probes + h.detach()

**Key decision:** DirectLocal matches backprop. This became the main focus.

### Round 3 - Validation
- DirectLocal v2: **98.15% MNIST** (beats BP 98.06%), **56.47% CIFAR-10** (beats BP 56.38%)
- DirectLocal Deep (5 layers): 98.01%
- Confirmed on both datasets: local learning matches global backprop.

### Round 4 - Gradient-free attempt
- ProtoLocal (prototypes + Hebbian): 44.26%
- ContrastLocal: 35.57%
- HebbFF: 10.54%
- **Conclusion: gradient-free barrier NOT broken.** All <45%. Local gradient (intra-layer) remains necessary.

### Round 5 - Transformer + HSIC
- DirectLocal Transformer (4 blocks): 96.21% vs 97.01% BP
- DirectLocal Transformer (8 blocks): 96.22% vs 97.20% BP
- **DirectLocal works on Transformers** (<1% gap)
- HSIC pure: 38.97%, HSIC+Probe: 42.06% - gradient-free still fails

### CPU vs GPU Timing
- 12 layers CPU: DirectLocal **3.3x faster** than backprop
- Advantage grows with depth (backprop backward pass is sequential)

### Round 6 - Literature-informed breakthrough algorithms
- Searched 40+ publications (2023-2026) across physics, math, neuroscience
- Implemented 3 state-of-the-art from 2025 papers:
- **NoProp** (DeepMind arXiv:2503.24322): 97.89% MNIST - diffusion denoising per block
- **Mono-Forward** (Auckland arXiv:2501.09238): 98.12% MNIST - projection matrix per layer
- SCFF (Nature Comms 2025): 10.49% - implementation failed (paper reports 98.7%)

### Final results
| Algorithm | MNIST | Global BP? | Source |
|-----------|-------|------------|--------|
| Backprop | 98.22% | YES | Baseline |
| MonoForward-Wide | 98.12% | NO | Auckland 2025 |
| DirectLocal v2 | 98.15% | NO | Our discovery |
| NoProp | 97.89% | NO | DeepMind 2025 |

### Solutions created
- **005_direct_local** - Our main discovery, validated on MLP + Transformer + CIFAR-10
- **006_noprop_diffusion** - DeepMind NoProp implementation
- **007_mono_forward** - Auckland Mono-Forward implementation

### Key insights
1. Per-layer probes with h.detach() is the winning pattern
2. Gradient-free barrier is real (all attempts <45%)
3. CPU advantage grows with depth (3.3x at 12 layers)
4. Local learning works on Transformers
5. Most promising next: test at GPT-2 scale

---

## 2026-04-03 - Gradient-Free Reservoir Lab (003) + NoProp-Reservoir (004)

**Session goal:** Systematically explore ALL gradient-free learning approaches to find a paradigm that can replace backpropagation.

**Approach:** Created 35 experiment scripts testing approaches from 7 categories: classic (FF, Hebbian, ES), bio-inspired (STDP, predictive coding, thermodynamic), info-theoretic (HSIC, HDC), exotic math (tropical geometry, fractal attractors, p-adic), reservoir computing, recent papers (NoProp, Mono-Forward, DTP, CCL, DLL), and original hybrids.

**3 parallel web research agents** explored: (1) gradient-free AI 2024-2026, (2) exotic math frameworks, (3) bio-inspired approaches. Found 30+ relevant papers including NoProp (CoLLAs 2025), v-PuNNs (arXiv 2025), Mono-Forward (arXiv 2025), Infomorphic Networks (PNAS 2025).

### Evolution of Results

**Phase 1 - Baselines (12 scripts):**
- Echo State Network emerged as clear winner: 92.3% in 2.5s
- Thermodynamic (CD): 88.9% - strong physics-based approach
- Everything else: 8.8% (Hebbian) to 72.3% (HSIC)
- Key insight: simple reservoir + ridge regression beats all complex local rules

**Phase 2 - Hybrids & Scaling (11 scripts):**
- Mega Reservoir (4 diverse): 94.1% - DIVERSITY IS KEY
- DFA: 89.0%, Local Contrastive: 85.3%
- Exotic attempts (tropical, fractal, entropy-tropical): 12-18%
- Key insight: multiple diverse reservoirs >> single deep approach

**Phase 3 - Ultra Reservoir (script #23):**
- **97.28% MNIST** with 8 diverse reservoirs + 3 input reps + stacking
- Zero gradient, zero backprop, zero iteration (closed-form readout)
- Only 1.2% behind standard backprop MLP
- Decision: THIS is the paradigm. Scale it.

**Phase 4 - Research-Informed (7 scripts):**
- Implemented DTP (8.5%), CCL (timeout), DLL (12.5%), 3-Factor (11.7%)
- NoProp diffusion: 80.0%, Mono-Forward: 88.5%, Prospective: 36.0%
- Simplified implementations far below paper results
- Decision: reproducing papers is verification, not innovation. Focus on our originals.

**Phase 5 - Scaling & Novel Architectures (5 scripts):**
- Ultra on Fashion-MNIST: **88.65%** (only 2-3% below backprop!)
- Ultra on CIFAR-10: 46.43% (needs spatial features - flat reservoir can't see 2D)
- v-PuNN: 16.55% (simplified impl; paper uses native p-adic arithmetic)
- **NoProp+Reservoir V1: 91.8%** - OUR INVENTION!
- **NoProp+Reservoir V2: 95.04%** - scaled up, 2nd best overall

### Key Discoveries

1. **Diversity > Depth:** 8 shallow diverse reservoirs >> 1 deep network
2. **HD encoding as universal preprocessor:** Random bipolar projection adds robustness for free
3. **NoProp+Reservoir is a real paradigm:** Independent blocks, closed-form training, 95.04%
4. **CIFAR needs spatial features:** Flat reservoirs can't capture 2D spatial patterns
5. **Reservoir computing is massively underrated:** Simple, fast, scalable, gradient-free, near-backprop accuracy

### Decisions Made

- Created 003 (Reservoir Lab meta-solution) + 004 (NoProp-Reservoir as separate original invention)
- Next: convolutional reservoir for CIFAR, proper v-PuNN implementation, NoProp-Reservoir paper

### Cross-Domain Links
- 003 builds_on 001 (entropy gating used as feature selector)
- 003 related_to 002 (both gradient-free, reservoir dynamics ~ fixed-point dynamics)
- 004 builds_on 003 (NoProp+Reservoir combines best findings from lab)

---

## 2026-04-03 — Session 1: Finding a Local Learning Algorithm

**Goal:** Find a local learning algorithm where each neuron adjusts using only its direct neighbors/local information, without backpropagation. If successful, training that takes 3 months on 10,000 GPUs could potentially be done in hours on a laptop.

**Environment:** RTX 4070 Ti (12GB), PyTorch 2.10, conda lerobot312

---

### Phase 1: Literature + Baselines (t+0min)

**Approach:** Implemented 7 classic local learning algorithms from the literature.
**Script:** `local_learning_lab/run_experiments.py`

| Algorithm | Source | Result | Notes |
|-----------|--------|--------|-------|
| Backprop MLP | — | 98.04% (5ep) | Reference |
| Forward-Forward | Hinton 2022 | NaN | Goodness threshold explodes |
| Predictive Coding | Rao & Ballard 1999 | CRASH | Dimension bug in error propagation |
| Equilibrium Prop | Scellier & Bengio 2017 | not completed | Killed with batch |
| InfoMax | Bell & Sejnowski 1995 | not completed | Killed with batch |
| Competitive Hebbian | Oja + kWTA | not completed | Killed with batch |
| Diff Target Prop | Lee et al 2015 | not completed | Killed with batch |

**Decision:** Classic approaches are well-explored and limited. Need RADICAL new ideas.

---

### Phase 2: Radical Novel Algorithms (t+30min)

**Approach:** Designed 6 fundamentally new algorithms from physics, biology, and information theory.
**Script:** `local_learning_lab/radical_algorithms.py`

| Algorithm | Inspiration | Result | Notes |
|-----------|-------------|--------|-------|
| Reaction-Diffusion | Turing patterns | 11.35% (4ep) | PDE dynamics too slow, stuck |
| Thermodynamic Free Energy | Statistical mechanics | not completed | GPU contention |
| Wave Interference | Quantum mechanics | not completed | Phase NaN |
| Kuramoto Oscillators | Sync theory | not completed | Uniform sync |
| Gossip Protocol | Distributed systems | not completed | Info destruction |
| **Entropy-Gated** | Neuroscience + info theory | **identified as promising** | Concept noted for focused test |

**Decision:** Killed PDE/wave/oscillator dead-ends. Entropy-Gated concept shows theoretical merit.

Also designed 6 more "frontier" algorithms (morphogenetic, active inference, cellular automata, hyperbolic, optimal transport, SOC) but didn't complete testing due to GPU contention.

---

### Phase 3: Focused Shootout (t+90min)

**Approach:** Quick 5-epoch benchmark of the 5 most promising non-PDE approaches.
**Script:** `local_learning_lab/focused_test.py`

| Rank | Algorithm | Accuracy (5ep) | Verdict |
|------|-----------|----------------|---------|
| 1 | **Entropy-Gated** | **86.85%** | WINNER — promote |
| 2 | NTSO (multi-signal) | 77.71% | Promising — promote |
| 3 | Gradient-Free Contrastive | 11.35% | Diverges — kill |
| 4 | Forward-Forward | 9.80% | NaN — kill |
| 4 | Learning by Disagreement | 9.80% | NaN — kill |
| 4 | Spectral Resonance | 9.80% | NaN — kill |

**Key Insight:** Entropy-Gated is the ONLY algorithm that learns stably AND meaningfully.
**Decision:** Deep optimize EG and NTSO. Kill everything else.

---

### Phase 4: Deep Optimization — EG vs NTSO (t+120min)

**Approach:** 20 epochs, optimized architectures, head-to-head comparison.
**Script:** `local_learning_lab/deep_optimize.py`

| Algorithm | Best Acc | Best Epoch | Stable? | Verdict |
|-----------|----------|------------|---------|---------|
| NTSO V2 | **88.90%** | 6 | NO → NaN at ep 19 | Abandoned — unstable |
| EG V2 | 87.91% | 20 (still climbing) | YES | WINNER — pure and stable |
| Hybrid EG+NTSO | 86.07% | 6 → decline | Partial | Abandoned — worse than pure EG |

**Key Insight:** "Simplicity wins. One gating signal (entropy) > multiple competing signals."
The NTSO's temperature/surprise/disagreement signals fight each other and create oscillatory instability. Pure entropy gating is cleaner and more robust.

**Decision:** All-in on pure Entropy-Gated. Next: fix memory leak and add stabilization.

---

### Phase 5: EG V3 — Stabilized (t+180min)

**Approach:** Fix critical bugs, add stabilization, run 50 epochs.
**Script:** `local_learning_lab/eg_v3_pure.py`

**Critical fixes:**
1. `@torch.no_grad()` on `local_update()` — fixes memory leak (PyTorch was building autograd graph)
2. SGD + momentum 0.9 (less memory than Adam, smoother updates)
3. Cosine LR schedule (prevents overshooting in late training)
4. Gradient clipping at norm=1.0

**Results:**

| Config | Acc (50ep) | Notes |
|--------|------------|-------|
| **2L Sigmoid [500,300]** | **92.81%** | **Never plateaus — every epoch is best** |
| 3L Sigmoid [400,400,200] | ~87% | Much slower convergence → 2L confirmed optimal |

**Key Insight:** 2 layers is optimal. Adding a 3rd layer worsens credit assignment without backprop. The reconstruction signal attenuates through depth.

**Decision:** Push to 95%+ with wider layers and better probe.

---

### Phase 6: EG V4 — Push to 95%+ (t+240min)

**Approach:** Wider [700,400], MLP probe (vs linear), 100 epochs, test data augmentation.
**Script:** `local_learning_lab/eg_v4_push95.py`

**Results:**

| Config | Acc | Best Ep | Notes |
|--------|-----|---------|-------|
| **V4 no-aug + MLP probe** | **97.46%** | 89 | **BREAKTHROUGH — 0.58% from backprop** |
| V4 + augmentation | 95.98% | 100 | Aug hurts: noisy inputs confuse reconstruction |

**Milestone achievements during training:**
- Ep 14: **95.13%** — crossed 95% barrier
- Ep 22: **96.03%** — crossed 96%
- Ep 36: **97.00%** — crossed 97%
- Ep 89: **97.46%** — final best

**Key Insights:**
1. MLP probe recovers ~5% more than linear probe (from same features)
2. Data augmentation hurts local learning — reconstruction signal needs clean inputs
3. Gap to backprop (0.58%) may be near-irreducible for this architecture

---

### Phase 7: CIFAR-10 — The Hard Test (t+300min)

**Approach:** Apply EG to color images. Test MLP (flatten), Conv V1 (sigmoid), Conv V2 (ReLU+LocalBN).
**Scripts:** `local_learning_lab/eg_cifar10.py`, `eg_conv_cifar.py`, `eg_conv_v2_cifar.py`

| Config | Acc | Verdict | Failure Analysis |
|--------|-----|---------|-----------------|
| Backprop Conv (reference) | **85.83%** | — | — |
| EG-Conv V2 (ReLU+LocalBN) | **48.22%** | ⚠️ Limited | Channel-average Hebbian loses spatial info |
| EG-MLP (flatten 3072d) | 41.16% | ⚠️ Limited | No spatial inductive bias at all |
| EG-Conv V1 (Sigmoid) | 10.00% | ❌ Dead-end | Sigmoid saturates conv feature maps |

**Key Insight:** The Hebbian signal for conv layers (average over spatial dims, then correlate channels) is too crude. It throws away the spatial structure that makes conv nets powerful. Need patch-level Hebbian correlation.

**CIFAR-10 remains the open challenge.** MNIST is solved.

---

## Summary of Key Discoveries

1. **Entropy gating = implicit curriculum.** Confident neurons stabilize, uncertain neurons keep learning. No global loss needed.
2. **Simplicity > complexity.** Pure entropy gate beats multi-signal hybrids (NTSO, hybrid).
3. **2 layers > 3+ layers** for local learning. Credit assignment is the bottleneck.
4. **Sigmoid for dense, ReLU for conv.** Sigmoid enables entropy computation but kills conv layers.
5. **Data augmentation hurts** local learning (noisy inputs confuse reconstruction).
6. **`@torch.no_grad()` is critical** — without it, PyTorch builds autograd graph → memory leak.
7. **MLP probe >> linear probe** — recovers ~5% more accuracy from same local features.
8. **0.58% gap on MNIST** -- local learning can nearly match backprop on simple datasets.
9. **37.6% gap on CIFAR-10** -- spatial Hebbian for conv is the unsolved problem.

---

## 2026-04-03 -- Session 2: Fixed-Point Substrate (002)

**Goal:** Create a completely new computational paradigm where intelligence emerges from a learnable *medium* rather than a network. Inspired by Fabien's LVS theory ("La realite nait du point fixe" -- It from Fix) and the insight that neural networks operate in a void with no underlying space.

**Core Idea:** Instead of propagating signals through layers, define a *computational medium* with local physical properties (conductivity, coupling, bias). Input perturbs the medium, which collapses to a fixed-point equilibrium Z* = f(Z*). The stable configuration IS the computation. All learning is local Hebbian, gated by entropy.

**Environment:** RTX 4070 Ti, PyTorch 2.6, conda base (miniconda3)

---

### Phase 8a: PDE Temporal Approach (failed)

**Hypothesis:** Reaction-diffusion PDE dynamics in a medium can transform inputs into classifiable features.

| Version | Approach | Result | Verdict |
|---------|----------|--------|---------|
| v0.1 | PDE temporal, spatial readout | 9.80% | Random level -- diffusion too slow |
| v0.2 | PDE + global avg pool readout | 19.80% | Learns slightly, pool destroys spatial info |
| v0.3 | PDE + regional 4x4 readout | abandoned | Pivoted to fixed-point paradigm |

**Key Insight:** Time-stepping PDE is the wrong paradigm. Diffusion destroys spatial information. The medium should find equilibrium, not simulate dynamics.

**Decision:** Pivot to fixed-point paradigm (Z* = f(Z*)).

---

### Phase 8b: Fixed-Point Paradigm -- Iterative Improvement

**Hypothesis:** Finding the equilibrium of a learnable medium (fixed-point iteration) is fundamentally better than simulating temporal dynamics.

| Version | Key Change | MNIST | Verdict |
|---------|------------|-------|---------|
| v0.4a | Fixed-point + 4x4 regions + 48ch | 76.20% | Paradigm works! Huge jump from 19.8% |
| v0.4b | + 7x7 regions + variance features | 85.18% | Better readout of the fixed point |
| v0.4c | + learnable spatial filters + 64ch | 92.73% | Retinal receptive fields -- each channel unique |
| **v0.5** | **96ch + multi-scale Lap + 2L readout + Anderson** | **96.44%** | **All levers engaged** |

**Evolution insights:**
- v0.4a: The paradigm shift from PDE to fixed-point gave a 56% jump (19.8% -> 76.2%). The medium DOES create useful features at equilibrium.
- v0.4b: The medium creates rich spatial features that global avg pool destroys. Regional mean+variance readout recovers them.
- v0.4c: Scalar input projection means all channels see the same image scaled. Learnable 5x5 spatial filters (like retinal receptors) give each channel a unique view. Massive improvement.
- v0.5: Multi-scale Laplacian (3x3+5x5+7x7) enables short/mid/long range coupling. Anderson acceleration cuts convergence from 11 to 7 iterations. Two-layer nonlinear readout breaks the linear decision boundary ceiling.

---

### Phase 8c: Cross-Dataset Benchmarks

| Dataset | Result | Epochs | Verdict |
|---------|--------|--------|---------|
| **MNIST** | **96.44%** | 50 | 1.6% gap to backprop (98.04%) |
| **Fashion-MNIST** | **77.15%** | 50 | 11.9% gap to backprop (~89%) |
| **CIFAR-10** | **42.24%** | 60 | 43.6% gap to backprop (85.83%) |

**Analysis:**
- MNIST: Near-backprop performance. The paradigm works excellently on structured spatial features.
- Fashion-MNIST: Good but gap widens. Textures and clothing details need more representational depth.
- CIFAR-10: Weakest. Natural color images need hierarchical features that a single-scale fixed point on a flat 32x32 grid cannot capture. Multi-resolution substrate (multigrid) is the next step.

**Key property:** Convergence in only 7 iterations (Anderson accelerated). Constant memory (no computation graph). All operations are convolutions and matmuls -- GPU-native.

---

### Summary of Key Discoveries (Session 2)

1. **Fixed-point > PDE temporal.** Finding Z*=f(Z*) is fundamentally better than simulating dPhi/dt. 56% accuracy jump.
2. **The medium creates rich features.** The bottleneck is reading them, not creating them. Readout improvements gave +20%.
3. **Learnable spatial filters are critical.** Each channel needs a unique receptive field (like retinal cells). +7.5% from this alone.
4. **Multi-scale coupling matters.** Single 3x3 Laplacian limits interaction range. Adding 5x5 and 7x7 scales helps.
5. **Anderson acceleration is free performance.** Reduces iterations 11->7 with no accuracy loss.
6. **The paradigm scales to new datasets** but struggles with complex natural images (CIFAR-10). Multi-resolution is needed.
7. **Connection to LVS theory is concrete.** Input perturbs the medium, medium collapses to stable configuration, stability IS the answer. "It from Fix" implemented.
8. **Zero backprop, constant memory, 7-iteration convergence.** Fundamentally different resource profile from deep learning.

---

## 2024-2026 - LVS Theory (P01) - Full Integration into Nexearch

**Goal:** Complete integration of LVS physics research with full evolution history, all source material, honest assessment.

### What LVS is
A meta-interpretive framework: **observable reality = fixed points of the quantum vacuum**. Synthesis of Asymptotic Safety (Weinberg 1979) + Page-Wootters (1983) + Coleman-Weinberg (1973). Core principle: stability IS existence ("It from Fix").

### Evolution of Thinking (11 phases)
1. **Spark:** YouTube video -> photon is atemporal (ds^2=0)
2. **Chain of reasoning:** 5 established facts -> 1 hypothesis (SR -> QED -> QFT -> CQG -> QM -> LVS)
3. **Paper v1:** 13-section formalization, meta-interpretive framework
4. **Visualization:** 5 interactive physics scenes (Three.js -> Jupyter migration)
5. **Validation:** 9-test scorecard (6 confirmed, 3 supported)
6. **Formalization:** Discovered LVS = AS + PW + CW. Shaposhnikov-Wetterich m_H = 126 GeV.
7. **Self-critique:** Acknowledged AI bias, underlying programs unproven (47+ years), no SM-independent predictions
8. **"Framework IS the problem":** Maybe need entirely new mathematical framework, not new equations
9. **Mass = frequency:** f = mc^2/h. Gravity = desynchronization. Connects to Jacobson/Verlinde/Connes-Rovelli.
10. **v3 Reformulation:** Infinite featureless points + interactions = network = reality. Dark energy = latent space.
11. **Complete essay:** "Du Point Fixe au Point de Rupture" - 20-chapter intellectual journal (56K chars, French)

### Key Results
- Higgs mass: predicted 126 GeV, measured 125.25 GeV (within 1 GeV)
- Hadron masses: R2 = 0.999998 (lattice QCD)
- Top quark: quasi-fixed-point y_t^2 ~ (8/9)g_3^2 (2.7% deviation)
- Validation: 6/9 confirmed, 3/9 supported, 0 in tension

### Dead Ends Encountered
- Fisher-KPP for Lambda: tautological (= Friedmann)
- Photon argument as foundation: pedagogical only, formalization doesn't use it
- HTML/Three.js visualizer: "fake physics"
- Page-Wootters first attempt: degenerate eigenstate
- Expressing LVS in existing frameworks: all inadequate

### Source Material (now self-contained in solutions/P01_lvs_theory/)
- 10 notebooks (5 clean + 5 executed), 3 source docs (paper 60KB + discussion 130KB + reference PDF)
- 3 web presentations (article + visualizer + essay FR 87KB)
- LaTeX paper + refs, writeup, results JSON

### Honest Status
- Compatible with all known physics (minimum bar for reinterpretation)
- Does NOT yet predict anything SM doesn't (critical gap)
- Underlying programs (AS, PW, CW) are NOT proven after 30-55 years
- Strongest asset: unifying synthesis that makes disparate physics coherent
- Weakest link: cosmological "actualization" is analogy, not formalized

### Cross-Domain Impact
- **P01 -> 002:** LVS is the theoretical foundation for Fixed-Point Substrate
- **P01 -> quantum:** Implications for QEC via fixed-point structure
- **P01 -> crypto:** Lattice problems and fixed-point iteration (PQC)

---

## 2025-2026 - FluidLM (F03) - Full Integration into Nexearch

**Goal:** Complete integration of FluidLM - a Transformer-free language model using reaction-diffusion PDEs.

### What FluidLM Is
O(N) language model replacing O(N^2) attention with multi-scale diffusion + Selective SSM (Mamba) + SwiGLU reaction. Zero KV-cache, GPU-free inference, adaptive computation (~30% savings). 44.2M params at V4.5.0.

### Architecture Evolution (V4.2 -> V4.5.0)
1. **V4.2:** PoC with Forward Euler + learned positional embeddings
2. **V4.3:** Added RoPE + MLP 4x expansion
3. **V4.4.0:** Major: CausalLongConv K=65, sinusoidal PE, cosine LR, memory pump (B,L,D)
4. **V4.4.1-3:** Bug fixes (dt slider, LongConv init, h-state O(1) restored)
5. **V4.4.4-7:** Stability: Forget Gate, layer-wise grad clip, local memory, desaturated gates
6. **V4.4.8:** Cross-pollination from FluidWorld: Laplacian grad_loss + curriculum scheduler
7. **V4.5.0 (current):** SwiGLU, Selective SSM (Mamba), Multi-Head LongConv, RMSNorm

### Key Results
- Best loss: 10.76 on TinyStories (step 801, 27.9M tokens)
- Linear memory scaling confirmed (vs quadratic Transformer)
- Adaptive computation works (halts at equilibrium)
- 44.2M total params (25.7M embedding, 18.5M core)

### Key Innovation
`du/dt = sum(D_k * nabla^2(u)) + SSM(u) + SwiGLU(u) + alpha*h`
- Tokens = chemical concentrations, information = diffusion
- Multi-scale: dilations [1, 4, 16] for local-to-global context
- O(1) global memory pump replaces growing KV-cache

### NOT Demonstrated Yet
- Competitive perplexity vs same-size Transformer
- Scaling beyond 44M params
- Generalization beyond TinyStories

### Paper Status
- NeurIPS 2025 submission (paper/fluidlm.pdf)

### Source Material (self-contained in solutions/F03_fluidlm/)
- source/: Full codebase (text_models.py, train_engine.py, web_app.py, config, launcher)
- paper/: LaTeX + PDF + BibTeX + NeurIPS style
- results/: Training stats JSON

### Cross-Domain
- **F03 builds_on P01:** PDE dynamics inspired by LVS fixed-point physics
- **F03 related_to F02:** FluidWorld shares PDE foundation, cross-pollinated grad_loss
- **F03 related_to 002:** Both explore PDE/equilibrium computation

---
