---
purpose: Research ideas backlog - raw ideas to explore in the future
last_updated: 2026-04-24
---

# Research TODO

> Write raw ideas here. An agent can read this to find the next thing to work on.
> Format: `- [ ] idea` (unchecked) or `- [x] idea` (done/started)

---

## High Priority

### LVS (P01) - post-reset priorities (2026-04-24)

- [ ] **Polish rigorous preprint** (P01) - `paper/lvs-preprint.md`: frame as conditional framework + negative result, prepare for arXiv submission (hep-th / gr-qc)
- [ ] **SARAH / RGBeta 2-loop validation** (P01) - check that 1-loop Planck-BC numbers (f_g ~ 0.010, f_y ~ 0.013) survive at 2-loop
- [ ] **Eichhorn-Held 2018 literature audit** (P01) - track what newer FRG truncations give for f_g, f_y; does the factor 3-5 mismatch shrink?
- [ ] **Joint gauge-Yukawa stationarity** (P01) - Yukawa residue beta_yt != 0 at M_Pl forces joint treatment
- [ ] **Direction 1: Pendleton-Ross IR attractor** (P01) - `scripts/direction2_attractor.py` - LVS as IR fixed-point selector?
- [ ] **Direction 2: Yukawa-sector joint** (P01) - `scripts/direction2_yukawa.py`
- [ ] **Direction 3: Hill-type attractor** (P01) - `figures/fig_hill_attractor.png` - analyse SM trajectory geometry
- [ ] **Identify one genuinely distinctive prediction** (P01) - current Planck-BC is dimensional and non-distinctive; find something that discriminates LVS from competing UV completions

### RAPC Modular Geometry (P02) - emergent geometry priorities (2026-04-24)

- [ ] **Weak bridge rule** (P02) - redesign patch gluing so fragmented sparse patches can connect without densifying
- [ ] **Large phase scan** (P02) - run 1000+ seeds per lambda on RTX 4070 Ti; map sparse-geometric phase width
- [ ] **Dimension diagnostics** (P02) - estimate emergent dimension from ball growth, graph Laplacian spectra, and spectral gap scaling
- [ ] **Basis-independent modular diagnostics** (P02) - replace Pauli projection with operator-algebraic non-factorization measures
- [ ] **Type-II crossed-product analogue** (P02) - formulate a finite-to-algebraic bridge toward Witten/CLPW style crossed products

### ML / other research lines

- [ ] **DirectLocal at GPT-2 scale** (005) - language modeling with per-block probes on Transformer
- [ ] **Mono-Forward CNN for CIFAR-10** (007) - reproduce paper result where MF beats BP (56.99% vs 54.25%)
- [ ] **NoProp full flow-matching** (006) - implement complete DeepMind paper, test CIFAR-10/100
- [ ] **SCFF proper implementation** - Self-Contrastive Forward-Forward from Nature Comms (paper: 98.7% MNIST, 80.75% CIFAR-10)
- [ ] **Multi-threaded C++ DirectLocal** (005) - 1 thread per layer for true parallelism, prove scaling advantage
- [ ] **Convolutional Reservoir for CIFAR-10** (003) - PyTorch impl with patch-based + Gabor + spatial pooling
- [ ] **NoProp-Reservoir V2 on Fashion-MNIST** (004) - fix OOM with chunked ridge regression
- [ ] **Proper v-PuNN implementation** (003) - native p-adic arithmetic library, paper reports 99.96%
- [ ] **NoProp-Reservoir V3** (004) - cosine noise schedule, more blocks, PyTorch GPU
- [ ] Multi-resolution fixed-point substrate (multigrid 8x8 -> 16x16 -> 32x32) for CIFAR-10
- [ ] Spatial Hebbian for EG conv layers - patch-level correlation instead of channel-average
- [ ] Benchmark FluidVLA on LIBERO manipulation tasks
- [ ] Benchmark FluidLM perplexity on WikiText-103

## Ideas to Explore (from 003 lab)

- [ ] p-Adic VAPO + Reservoir - ultrametric encoding of reservoir states (novel combo)
- [ ] Reservoir + Fixed-Point Substrate (002) - FPS dynamics as reservoir
- [ ] Entropy-gated reservoir selection (001 + 003) - activate only useful reservoirs per sample
- [ ] Online NoProp-Reservoir with recursive least squares for streaming data
- [ ] Scale Ultra Reservoir to ImageNet (PyTorch + GPU needed)
- [ ] NoProp-Reservoir for temporal/sequential data (where reservoirs truly shine)
- [ ] Combine NoProp-Reservoir with thermodynamic cooling schedule
- [ ] Neuromorphic reservoir on SpiNNaker/Loihi
- [ ] Write NeurIPS/ICML paper on NoProp-Reservoir architecture
- [ ] Can entropy-gated plasticity replace softmax attention in transformers?
- [ ] EG + spiking networks - entropy of spike rates as plasticity gate (neuromorphic hardware)
- [ ] Fixed-Point Substrate as world model - can the medium learn environment dynamics?
- [ ] Combine FPS (002) with Entropy-Gated (001) - FPS medium + EG learning rule
- [ ] LVS theory applied to quantum error correction - fixed points in code space
- [ ] Post-quantum lattice cryptography - can fixed-point iteration break/strengthen lattice problems?
- [ ] Information-theoretic bounds on local learning - what is the maximum accuracy without backprop?
- [ ] Distributed local learning - no gradient sync across GPUs, each GPU runs EG independently
- [ ] Can the fixed-point substrate paradigm work for NLP? Text as 1D spatial medium?
- [ ] Thermodynamic computing hardware - EG/FPS on analog chips

## Ideas from Literature Search (Session 2)

- [ ] **EGGROLL** (arXiv:2511.16652) - Evolution-guided gradient-free LLM training, outperforms PPO/GRPO on 7B models
- [ ] **SLL** (arXiv:2505.05181) - Stochastic Layer-wise Learning, matches BP on ImageNet with constant memory
- [ ] **Prospective Configuration** (Nature Neuroscience 2024) - infer target activity before plasticity, matches BP
- [ ] **DeepZero** (ICLR 2024) - zeroth-order gradient estimation, 86.94% CIFAR-10 from scratch
- [ ] **MeZO** for LLM fine-tuning - 30B params on single A100, 12x memory reduction
- [ ] **Forward Target Propagation** (arXiv:2506.11030) - second forward pass replaces backward
- [ ] **Burstprop** - burst-dependent plasticity, error encoded in spike bursts alongside inference
- [ ] **Heterosynaptic plasticity** (arXiv:2505.02248) - proven to be universal gradient machine (bio-plausible BP)
- [ ] **Thermodynamic computing** (Nature Comms 2025) - 7 orders of magnitude energy advantage on physical hardware
- [ ] **Coupled oscillator EP** (arXiv:2402.08579) - Equilibrium Propagation on physical oscillator networks

## Speculative / Long-term

- [ ] Unified theory: LVS fixed-points + entropy gating + world models = general intelligence?
- [ ] Biological validation: does the brain actually use entropy-gated plasticity?
- [ ] Quantum fixed-point substrate - quantum medium finding quantum equilibrium
- [ ] Category theory formalization of the fixed-point learning paradigm

## Done / Started

- [x] Entropy-Gated Learning V1-V4 on MNIST (97.46%) -> solution 001
- [x] Fixed-Point Substrate on MNIST/F-MNIST/CIFAR-10 (96.44%) -> solution 002
- [x] CIFAR-10 attempts for both EG and FPS -> open challenge
- [x] Gradient-Free Reservoir Lab: 35 approaches tested (97.28% MNIST) -> solution 003
- [x] NoProp-Reservoir invention: chain of reservoir denoisers (95.04% MNIST) -> solution 004
- [x] Ultra Reservoir on Fashion-MNIST (88.65%) -> solution 003
- [x] Ultra Reservoir on CIFAR-10 (46.43% - needs conv features) -> solution 003
- [x] Local Learning Paradigm Search: 6 rounds, 15+ algorithms (Session 2)
- [x] DirectLocal discovery: per-layer probes + detach, 98.15% MNIST, 56.47% CIFAR-10 -> solution 005
- [x] DirectLocal on Transformers: 96.22% vs 97.20% BP -> solution 005
- [x] CPU timing: DirectLocal 3.3x faster than BP for 12 layers -> solution 005
- [x] NoProp Diffusion implementation: 97.89% MNIST -> solution 006
- [x] Mono-Forward implementation: 98.12% MNIST -> solution 007
- [x] Gradient-free barrier confirmed: all zero-grad approaches <45% MNIST
- [x] Literature search: 40+ papers analyzed (SCFF, NoProp, MonoForward, EGGROLL, SLL, etc.)
- [x] LVS methodological reset (2026-04-24): strong global-flow form FALSIFIED at alpha_s=0.048 (P01)
- [x] LVS robustness test: sigma1/sigma2/sigma3 agree - "50% partial optimum" retracted as metric artifact (P01)
- [x] LVS Planck-BC dimensional analysis: f_g ~ 0.010, f_y ~ 0.013 (P01)
- [x] LVS Eichhorn-Held 2018 comparison: f_g=0.055, f_y=0.004 - factor 3-5 mismatch within ~60% truncation uncertainty (P01)
- [x] LVS Yukawa residue finding: beta_yt != 0 at M_Pl even when beta_gauge vanishes (P01)
- [x] Rigorous preprint promoted from `paper_v4_final` to `paper/lvs-preprint.md` (P01)
- [x] Archived biased explorations (d=3 / SU321 / DESI GPU sims, "f_g=0.010585 exactly" overclaim) to `archives_biased_explorations/` (P01)
- [x] RAPC Modular Geometry integrated as solution P02 with source scripts, notebook, writeups, JSON summaries, paper skeleton, and dashboard entries
- [x] RAPC BMV and modular-phase toy gates passed (finite Type-I models only)
- [x] RAPC spectral-locality scan found best sparse-geometric phase at 9/20 seeds across broad lambda range
- [x] RAPC patch gluing attempt failed to add bridges, identifying weak-bridge generation as the next bottleneck
