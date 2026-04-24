---
purpose: Complete archive of all failed and abandoned approaches with detailed failure analysis
last_updated: 2026-04-24
total_failed: 56
---

# Failed & Abandoned Approaches Archive

> **For any agent/researcher:** Check this list BEFORE exploring a new idea. If something similar is here, understand WHY it failed before investing time. Some approaches here have partial merit — see "Worth Revisiting?" column.

---

## Summary Table

| # | Approach | Category | Best MNIST | Tested In | Failure Mode | Worth Revisiting? |
|---|----------|----------|------------|-----------|-------------|-------------------|
| 1 | Forward-Forward (Hinton) | local-learning | 9.80% | Phase 1,3 | NaN | Maybe (needs threshold tuning) |
| 2 | Predictive Coding | local-learning | crash | Phase 1 | Dimension bug | Yes (correct implementation) |
| 3 | Equilibrium Propagation | local-learning | — | Phase 1 | Not completed | Yes (well-published method) |
| 4 | InfoMax | local-learning | — | Phase 1 | Not completed | Maybe |
| 5 | Competitive Hebbian | gradient-free | — | Phase 1 | Not completed | Maybe |
| 6 | Diff Target Propagation | local-learning | — | Phase 1 | Not completed | Yes (combine with EG?) |
| 7 | Reaction-Diffusion | physics-inspired | 11.35% | Phase 2 | Stuck at random | No — dead-end |
| 8 | Thermodynamic Free Energy | physics-inspired | — | Phase 2 | Not completed | Ideas reused in NTSO |
| 9 | Wave Interference | physics-inspired | — | Phase 2 | NaN expected | No — numerically fragile |
| 10 | Kuramoto Oscillators | physics-inspired | — | Phase 2 | Uniform sync | No — non-discriminative |
| 11 | Gossip Protocol | gradient-free | — | Phase 2 | Info destruction | No — averaging kills signal |
| 12 | Learning by Disagreement | gradient-free | 9.80% | Phase 3 | NaN | No — no error signal |
| 13 | Gradient-Free Contrastive | gradient-free | 11.35% | Phase 3 | Loss explodes | Maybe (with clipping) |
| 14 | Spectral Resonance | physics-inspired | 9.80% | Phase 3 | NaN | No — freq drift |
| 15 | NTSO (multi-signal) | local-learning | 88.90% | Phase 3,4 | Diverges ep 19 | Maybe (with stabilization) |
| 16 | EG+NTSO Hybrid | hybrid | 86.07% | Phase 4 | Stagnates | No — simpler EG is better |
| 17 | EG-Conv V1 (Sigmoid) | local-learning | 10% CIFAR | Phase 7 | Saturation | No — sigmoid kills conv |
| 18 | Thermodynamic LL (S2) | local-learning | ~70% | S2-R1 | Backprop disguised | No — target prop = backprop light |
| 19 | Predictive Coding (S2) | local-learning | NaN | S2-R1 | Numerical instability | Maybe |
| 20 | FF + InfoGeom (S2) | local-learning | NaN | S2-R1 | Numerical instability | Maybe |
| 21 | Reaction-Diffusion NN (S2) | physics-inspired | ~40% | S2-R1 | PDE too slow | No — eliminated by design |
| 22 | Cellular Automata NN (S2) | novel-arch | ~85%* | S2-R1 | Readout uses backprop | No — not truly local |
| 23 | NOVA belief diffusion (S2) | local-learning | 48.90% | S2-R1 | Belief diffusion too slow | Maybe |
| 24 | EqProp-Tuned (S2) | local-learning | 70.07% | S2-R2 | Slow convergence | No — DirectLocal dominates |
| 25 | HESP Hybrid (S2) | hybrid | 49.40% | S2-R2 | EqProp+error clash | No |
| 26 | ProtoLocal (S2) | gradient-free | 44.26% | S2-R4 | Prototypes not discriminative | Maybe (RBF kernel) |
| 27 | HebbFF (S2) | gradient-free | 10.54% | S2-R4 | Hebbian FF diverges | No |
| 28 | ContrastLocal (S2) | gradient-free | 35.57% | S2-R4 | Signal too weak, degrades | No |
| 29 | HSIC pure (S2) | gradient-free | 38.97% | S2-R5 | Linear kernel insufficient | Maybe (RBF) |
| 30 | HSIC+Probe (S2) | hybrid | 42.06% | S2-R5 | HSIC features unhelpful | No |
| 31 | SCFF impl (S2) | gradient-free | 10.49% | S2-R6 | Implementation failed | Yes (paper: 98.7%) |
| 32 | EqProp+Momentum (S2) | local-learning | 87.49% | S2-R2 | Gap too large (11%) | No — surpassed by DLL |
| 40 | LVS global RG-flow min (strong) | physics-theory | — | P01 2026-04 | alpha_s opt=0.048 vs 0.1179 | No — falsified; weak (Planck-BC) form remains |
| 41 | "50% partial-LVS optimum" | physics-theory | — | P01 2026-04 | sigma2-only artifact; sigma1/sigma3 disagree | No — retracted |
| 42 | "f_g=0.010585 exactly" overclaim | physics-theory | — | P01 2026-04 | Dimensional coincidence sold as precision | No — replaced by honest Planck-BC framing |
| 43 | d=3 / SU321 / DESI GPU tuned sims | physics-sim | — | P01 2026-03 | Post-hoc tuning, not pre-registered | Only with pre-registered protocols |

---

## Session 2 Failed Approaches (Detailed) — Local Learning Paradigm Search

### F18-22 — Round 1 Eliminations
Seven algorithms tested simultaneously. Thermodynamic LL was backprop in disguise (target propagation). Predictive Coding and Forward-Forward crashed with NaN due to numerical instability. Reaction-Diffusion was eliminated for being PDE-based (too slow). Cellular Automata worked but its readout layer needed backprop.

### F23 — NOVA (Neighbor-Only Variational Alignment)
Our original synthesis combining predictive coding errors, Hebbian correlation, and neighbor confidence. Belief diffusion was too slow to converge — 48.90% after 5 epochs. The idea of "confidence modulated by neighbor variance" was sound but the diffusion mechanism was inefficient.

### F26-28 — Gradient-Free Round (Round 4)
Three approaches attempted to eliminate ALL gradients: ProtoLocal (class prototypes + Hebbian), HebbFF (Hebbian Forward-Forward), ContrastLocal (contrastive + prototypes). ALL failed with <45% accuracy. Key lesson: **the gradient-free barrier has not been broken.** Local gradient (within each layer) is necessary for discriminative feature extraction.

### F29-30 — HSIC Round (Round 5)
HSIC (Hilbert-Schmidt Independence Criterion) was used as a gradient-free loss. Both pure HSIC (38.97%) and HSIC+Probe hybrid (42.06%) failed. The linear kernel HSIC does not provide sufficient discriminative signal. RBF kernels might help but are O(B^2) per layer.

### F31 — SCFF Implementation
Self-Contrastive Forward-Forward (Nature Communications 2025) was implemented in simplified form. Our implementation only reached 10.49% — likely due to missing augmentation pipeline and incorrect negative generation. The paper reports 98.7% on MNIST and 80.75% on CIFAR-10, so the method works but requires careful implementation.

---

## Detailed Failure Analysis

### Category 1: PDE / Continuous Dynamics

#### Reaction-Diffusion Learning
- **Core idea:** Each neuron = chemical concentration. Learning = diffusion between neighbors (Turing patterns).
- **Equation:** `du_i/dt = u(1-u)(u-a) + D * sum(u_j - u_i) + alpha * input`
- **Result:** 11.35% on MNIST (4 epochs, ~50s/epoch)
- **Why it failed:** PDE dynamics have their OWN attractors (Turing pattern equilibria) that are unrelated to classification. The diffusion process creates spatial patterns but they don't encode class information. Also extremely slow due to iterative dynamics (5 steps per forward pass).
- **Dead-end?** YES. Fundamental mismatch between PDE attractors and classification objectives.

#### Wave Interference Learning
- **Core idea:** Signals are complex numbers (amplitude + phase). Learning = phase alignment.
- **Equation:** `y = sum(|w|*|x|*exp(i*(phi_w + phi_x)))`, update: align phases
- **Result:** Not completed (expected NaN from analysis)
- **Why it would fail:** `atan2` and complex exponentials create discontinuities. Phase wrapping at ±pi causes gradient jumps. Float32 insufficient for stable phase arithmetic.
- **Dead-end?** YES for float32. Maybe revisitable with float64 or proper phase unwrapping.

#### Kuramoto Oscillators
- **Core idea:** Neurons are coupled oscillators. Learning = sync pattern formation.
- **Equation:** `dtheta_i/dt = omega_i + sum(K_ij * sin(theta_j - theta_i))`
- **Result:** Not completed
- **Why it would fail:** Kuramoto model converges to global sync (all same phase) or cluster sync. Neither produces discriminative representations — all inputs produce the same output pattern.
- **Dead-end?** YES. Synchronization ≠ discrimination.

### Category 2: Pure Topology / No Error Signal

#### Learning by Disagreement (LBD)
- **Core idea:** Neurons learn ONLY when they disagree with neighbors. No loss function.
- **Equation:** `dW = disagreement * sign(neighbor_mean - y) * x`
- **Result:** 9.80% (NaN) on MNIST
- **Why it failed:** Without ANY form of prediction error, the update direction is random. Neighbor disagreement tells you THAT something is wrong but not WHICH direction to fix it. Weights random-walk → NaN.
- **Dead-end?** YES. Need error signal of some form (reconstruction, prediction, contrastive).
- **Lesson:** Topology alone is insufficient. The brain uses prediction error (dopamine), not just disagreement.

#### Gossip Protocol
- **Core idea:** Neurons exchange "beliefs" with neighbors and average them. Consensus = learning.
- **Equation:** `belief = alpha*f(input) + (1-alpha)*mean(neighbor_beliefs)`
- **Result:** Not completed
- **Why it would fail:** Averaging neighboring activations converges to the global mean. All neurons produce identical outputs. Information is destroyed, not created.
- **Dead-end?** YES. Consensus averaging is fundamentally information-destroying.

### Category 3: Gradient-Free Geometric

#### Gradient-Free Contrastive Neighbors (GFCN)
- **Core idea:** Preserve input neighborhood structure: similar inputs → similar outputs.
- **Equation:** `dW = pull*(y2-y1)*x + push*(y1-y2)*x` based on cosine similarity
- **Result:** 11.35% on MNIST, loss explodes (20 → 100+)
- **Why it failed:** Cosine similarity between random mini-batch pairs is extremely noisy. Pull/push forces don't cancel out → weight norms diverge exponentially.
- **Worth revisiting?** Maybe with gradient clipping, normalized weights, and larger batch for more stable similarity estimates.

#### Spectral Resonance
- **Core idea:** Neurons = oscillators at different frequencies. Each specializes in a frequency band.
- **Equation:** `response = drive * sigmoid(frequency)`, frequency updated by variance
- **Result:** 9.80% (NaN) on MNIST
- **Why it failed:** Frequency parameters drift without bound. No anchoring mechanism. High-variance neurons get higher frequencies → even higher activation → even higher variance → positive feedback → NaN.
- **Dead-end?** YES without frequency bounding. The concept of spectral decomposition has merit but needs explicit constraints.

### Category 4: Unstable Multi-Signal Approaches

#### NTSO (Neuro-Thermodynamic Self-Organization)
- **Core idea:** Plasticity from MULTIPLE signals: surprise + entropy + neighbor disagreement + temperature.
- **Equation:** `plast = sigmoid(0.4*(surprise-1) + 0.3*disagree + 0.3*(T-0.5))`
- **Result:** **88.90% on MNIST** (peak at epoch 6), then diverges → NaN at epoch 19
- **Why it failed:** The temperature annealing creates a positive feedback loop. As neurons cool (low T), they become less plastic → can't correct accumulating errors → errors grow → sudden collapse. The 4 competing signals (surprise, entropy, disagreement, temperature) oscillate against each other.
- **Worth revisiting?** YES — with heavy stabilization (gradient clipping, T floor, slower annealing). The 88.9% peak shows it WORKS briefly. Key question: can you make it stable?
- **Lesson:** Single signal (entropy alone) is more robust than multi-signal. Simplicity > expressiveness.

#### EG+NTSO Hybrid
- **Core idea:** Combine the best of EG (entropy gate) and NTSO (surprise + temperature).
- **Result:** 86.07% on MNIST (peak ep 6, then slow decline to 83%)
- **Why it failed:** Hybrid is WORSE than either pure approach. The entropy gate from EG and the temperature from NTSO fight each other — both try to control plasticity but in contradictory ways.
- **Dead-end?** YES. Don't hybridize competing plasticity mechanisms.
- **Lesson:** Mixing local learning rules doesn't help. Each rule has its own attractor.

### Category 5: Architecture-Specific Failures

#### EG-Conv V1 (Sigmoid Conv Layers for CIFAR-10)
- **Core idea:** Apply proven EG sigmoid layers to convolutional architecture.
- **Result:** 10.00% on CIFAR-10 (random chance), stuck from epoch 1
- **Why it failed:** Sigmoid activation in conv layers causes complete saturation. All spatial positions output ~0.5. Entropy is maximal everywhere → plasticity is uniform → no differentiation between neurons → no learning. The narrow [0,1] range of sigmoid crushes the variance of convolutional feature maps.
- **Dead-end?** YES for sigmoid + conv. ReLU + LocalBN (V2) partially fixes this (48.22%).
- **Lesson:** Sigmoid works for dense layers (MNIST) because input is already normalized. For conv layers with varying spatial statistics, ReLU is mandatory.

### Category 6: Not Yet Tested (Frontier Concepts)

These were designed but not benchmarked due to time/GPU constraints. Documented here for future exploration.

| Approach | Core Idea | Code Location | Priority |
|----------|-----------|---------------|----------|
| Morphogenetic | Cells differentiate via local morphogen gradients (biology) | `local_learning_lab/frontier_algorithms.py` | Medium |
| Active Inference (Friston) | Each neuron minimizes its own variational free energy | `local_learning_lab/frontier_algorithms.py` | High |
| Cellular Automata | CA rule network learns to learn (meta-learning local rules) | `local_learning_lab/frontier_algorithms.py` | Medium |
| Hyperbolic Geometry | Neurons in Poincare disk, Mobius transformations | `local_learning_lab/frontier_algorithms.py` | Low |
| Optimal Transport | Sinkhorn iteration as weight matrix | `local_learning_lab/frontier_algorithms.py` | Low |
| Self-Organized Criticality | Sandpile dynamics, power-law avalanches | `local_learning_lab/frontier_algorithms.py` | Medium |

---

### Category 7: LVS Theory Dead Ends (P01)
**These are approaches tried within the LVS physics research that didn't work.**

| Approach | What happened | Lesson |
|----------|---------------|--------|
| HTML/Three.js visualizer | Produced "fake physics" - shapes not equations | Always compute from real equations, not approximate |
| Page-Wootters first attempt | sigma_z = 0 to 0 (degenerate eigenstate) | Need N-level clock system (32+ levels) |
| Gravitational corrections to Higgs | a_grav, b_grav coefficients too crude | Need proper 2-loop, not rough approximations |
| Fisher-KPP for Lambda | Lambda_pred/Lambda_obs = 1.08 | Tautological - equivalent to Friedmann equations |
| Connes NCG Higgs prediction | Predicted 170 GeV (WRONG, corrected post-hoc) | NCG has structural problems |
| Photon argument as foundation | Formalization never uses ds^2=0 | Pedagogical only, not foundational - remove from paper core |
| Expressing LVS in existing math frameworks | Hilbert space / Riemannian / fiber bundles all inadequate | Perhaps need fundamentally new mathematical framework |
| Padmanabhan Lambda calculation | Numerical overflow (H_0 became numpy array) | Careful numerics needed, redefined constants locally |
| Trying to prove Asymptotic Safety | Hundreds tried for 47 years, not proven | Not realistic for one researcher |
| Extending Page-Wootters to full QG | Works for toy systems, fails for infinite DOF | Major open problem in quantum gravity |

---

## Meta-Lessons (What We Learned From All Failures)

1. **You need an error signal.** Pure topology/geometry/sync without prediction error → random walk → NaN.
2. **Simpler plasticity rules > complex ones.** One signal (entropy) beats 4 signals (NTSO).
3. **PDE dynamics are a dead-end** for learning. Their attractors don't align with classification.
4. **Sigmoid for dense, ReLU for conv.** Never use sigmoid in convolutional layers.
5. **Stability is more important than peak accuracy.** NTSO peaked higher (88.9%) than EG V2 (87.9%) but EG won in the end (97.46%) because it never diverged.
6. **2 layers optimal** for local learning. Deeper = worse credit assignment.
7. **Reconstruction is the key signal.** All successful approaches include "can I predict my input from my output?" as the primary learning driver.

---

## From 003 Gradient-Free Reservoir Lab (2026-04-03)

35 gradient-free methods tested. 14 new failures documented below:

### F26 - Forward-Forward (Hinton) - Simplified
- **Solution:** 003 | **Acc:** 17.4% | **Time:** 115s
- **Failure:** Our simplified implementation with label overlay on first pixels. Goodness threshold hard to tune. Paper reports 98.5% with full architecture.
- **Lesson:** FF needs careful negative data generation and architecture-specific tricks.
- **Worth Revisiting?** Yes - implement Self-Contrastive FF (NatComm 2025) which fixes negative data problem.

### F27 - Pure Hebbian + WTA
- **Solution:** 003 | **Acc:** 8.8% | **Time:** 33s
- **Failure:** Oja's rule + winner-take-all finds features but cannot discriminate classes.
- **Lesson:** Hebbian alone needs a supervised signal. Works better as component (e.g., in reservoir feature selection).
- **Worth Revisiting?** No - unless combined with GHL (2026 paper: first Hebbian to scale to ResNet-1202).

### F28 - Simulated Annealing for Weights
- **Solution:** 003 | **Acc:** 14.4% | **Time:** 1.3s
- **Failure:** Weight space is too high-dimensional for random perturbation search.
- **Lesson:** Global search methods need structure (sparsity, subspace projection). See DeepZero (ICLR 2024).
- **Worth Revisiting?** No - ES (48.7%) is strictly better and also slow.

### F29 - Tropical Geometry Network
- **Solution:** 003 | **Acc:** 12.6% | **Time:** 39s
- **Failure:** Max-plus algebra alone is not discriminative enough. The argmax competition doesn't create useful features.
- **Lesson:** Tropical geometry is theoretically beautiful (polynomial-time training for 1-layer) but the combinatorial structure doesn't scale.
- **Worth Revisiting?** Maybe - try tropical + reservoir hybrid, or use tropical for architecture search.

### F30 - Entropy-Gated Standalone (from 001)
- **Solution:** 003 | **Acc:** 17.2% | **Time:** 21s
- **Failure:** Entropy is a good gating/regulation signal but terrible as sole learning signal.
- **Lesson:** Entropy gating works best as a COMPONENT (feature selection in reservoir, plasticity gate in 001).
- **Worth Revisiting?** No standalone - but keep using as component.

### F31 - Fractal/Chaos Attractor Learning
- **Solution:** 003 | **Acc:** 17.9% | **Time:** 108s
- **Failure:** Iterated contraction maps converge but the attractor basins don't separate classes well.
- **Lesson:** The perturbation-based optimization of attractor parameters is too noisy. Edge-of-chaos might help (see literature).
- **Worth Revisiting?** Low priority.

### F32 - Simplified DTP (Difference Target Propagation)
- **Solution:** 003 | **Acc:** 8.5% | **Time:** 19s
- **Failure:** Simplified numpy impl with small network. Inverse mappings didn't learn properly.
- **Lesson:** DTP needs careful initialization of inverse weights and proper DTP correction term. Paper reports 99.2%.
- **Worth Revisiting?** Yes - implement with PyTorch using paper's exact architecture.

### F33 - Simplified Dendritic Local Learning (DLL)
- **Solution:** 003 | **Acc:** 12.5% | **Time:** 7s
- **Failure:** Our 3-compartment pyramidal neuron model is too simplified. The apical-basal interaction needs proper feedback alignment.
- **Lesson:** ICML 2025 paper uses much more sophisticated architecture. Our random feedback projections don't provide useful top-down signal.
- **Worth Revisiting?** Yes - with proper implementation from paper's GitHub.

### F34 - Three-Factor Neuromodulated
- **Solution:** 003 | **Acc:** 11.7% | **Time:** 19s
- **Failure:** Global reward signal too sparse. The scalar "correct/incorrect" doesn't provide enough information.
- **Lesson:** Needs per-neuron eligibility traces + richer reward signal (not just binary correct/wrong).
- **Worth Revisiting?** Maybe - with dopamine-like per-layer heterogeneous signals (Cell 2025 paper).

### F35 - Prospective Configuration (simplified)
- **Solution:** 003 | **Acc:** 36.0% | **Time:** 78s
- **Failure:** Target activity inference doesn't converge properly. The top-down pseudo-inverse is too crude.
- **Lesson:** Nature Neuroscience 2024 paper uses proper variational inference for target finding.
- **Worth Revisiting?** Yes - implement with proper free energy inference.

### F36 - v-PuNN (p-adic Neural Network)
- **Solution:** 003 | **Acc:** 16.55% | **Time:** slow
- **Failure:** Our approximation of p-adic balls with Euclidean distances loses the ultrametric structure. VAPO optimizer finds no improvement.
- **Lesson:** p-adic networks REQUIRE native p-adic arithmetic. The ultrametric property (|x+y| <= max(|x|,|y|)) is essential.
- **Worth Revisiting?** YES - high priority. Paper reports 99.96% on hierarchical data. Need proper p-adic library.

### F37 - Ultra Reservoir on CIFAR-10
- **Solution:** 003 | **Acc:** 46.43% | **Time:** 503s
- **Failure:** Flat reservoirs can't capture 2D spatial patterns in 32x32 color images.
- **Lesson:** Need convolutional preprocessing (patches, Gabor filters) or convolutional reservoirs. The 784-dim flat representation works for MNIST/Fashion but not for spatial data.
- **Worth Revisiting?** YES - with patch-based + Gabor + convolutional reservoir (script 34, OOM).

### F38 - Conv Reservoir CIFAR-10 (script 34)
- **Solution:** 003 | **Acc:** OOM crash | **Time:** -
- **Failure:** 50k images * dense patches * reservoirs = out of memory in numpy.
- **Lesson:** Need PyTorch implementation with GPU batching. The approach is sound, just needs better engineering.
- **Worth Revisiting?** YES - in PyTorch with proper memory management.

### F39 - NoProp+Reservoir V2 on Fashion-MNIST
- **Solution:** 004 | **Acc:** OOM crash | **Time:** -
- **Failure:** 60k samples * 1500-dim reservoirs * 8 blocks = out of memory.
- **Lesson:** Need chunked ridge regression or PyTorch implementation. The architecture works, just needs memory optimization.
- **Worth Revisiting?** YES - with chunked computation or PyTorch.

## P01 LVS - falsifications and retractions (2026-04-24)

### F40 - Global RG-flow minimization (strong LVS form)
- **Solution:** P01 | **Optimum:** alpha_s(M_Z) = 0.048 | **Measured:** 0.1179 | **Reproduce:** `scripts/rigorous_alpha_s_test.py`
- **Hypothesis:** SM parameters at M_Z minimize `int_{M_Z}^{M_Pl} sum_i beta_i^2 dt` over the gauge sector.
- **Failure:** The minimum of the global flow action sits nowhere near the measured alpha_s. Strong form **falsified**.
- **Lesson:** LVS as a *global* action principle is ruled out. Only the *local* Planck-BC form (weak stationarity at M_Pl) remains viable.
- **Worth Revisiting?** No for the strong form. The Planck-BC form lives on as a conditional framework.

### F41 - "50% partial-LVS optimum" artifact
- **Solution:** P01 | **Retracted:** 2026-04 robustness test
- **Failure:** Earlier runs using only the relative metric sigma2 reported an optimum where couplings flatten ~50% from their measured values. Running the same scan under sigma1 (absolute) and sigma3 (sub-linear) shows no such optimum - the apparent minimum was a reparameterization artifact of sigma2. See `figures/fig_robustness_test.png`.
- **Lesson:** Never report a stationarity extremum under a single metric. Multi-metric agreement (sigma1/sigma2/sigma3) is now the minimum bar.
- **Worth Revisiting?** No - the artifact is now fully understood.

### F42 - "LVS predicts f_g = 0.010585 exactly" overclaim
- **Solution:** P01 | **Retracted:** 2026-04
- **Failure:** A dimensional-analysis coincidence was reported as a sharp prediction. Actual LVS output is a *range* consistent with f_g ~ 10^-2, not a specific digit string. The value also lacks distinctiveness - any UV completion producing similar stationarity would satisfy it.
- **Lesson:** Distinguish order-of-magnitude from precision predictions in papers. Never quote spurious digits from a dimensional argument.
- **Worth Revisiting?** No - replaced by honest Planck-BC framing in the rigorous preprint.

### F43 - d=3 / SU(3)xSU(2)xU(1) / DESI tuned GPU simulations
- **Solution:** P01 | **Verdict:** tuned, not predictive | **Archived:** `archives_biased_explorations/simulations_FPS/`
- **Failure:** GPU simulations producing "d=3" as the preferred dimensionality, the SM gauge group, or DESI-compatible expansion, were, on audit, sensitive to choices that had been tuned to yield those outcomes. They are illustrations, not evidence.
- **Lesson:** For tests of a selection principle like LVS, every free parameter must be pre-registered. Post-hoc tuning to known outcomes produces zero Bayesian evidence.
- **Worth Revisiting?** Only with pre-registered, blinded simulation protocols.

## P02 RAPC Modular Geometry - failed or limited toy gates (2026-04-24)

### F44 - Simple MDL compression as geometry selector
- **Solution:** P02 | **Best:** 6/20 sparse-geometric seeds | **Reproduce:** `solutions/P02_rapc_modular_geometry/source/rapc_phase_scan_toy.py`
- **Hypothesis:** A simple score `information - lambda * graph_complexity` is enough to make sparse connected geometry emerge from modular hypergraph seeds.
- **Failure:** The sparse-geometric phase exists but is narrow. Most seeds become fragmented or empty as lambda increases.
- **Lesson:** Compression alone is too weak. A locality/spectral term is needed.
- **Worth Revisiting?** Only as a baseline against spectral-locality selection.

### F45 - RAPC patch gluing without residual memory
- **Solution:** P02 | **Result:** mean_bridges = 0 | **Reproduce:** `solutions/P02_rapc_modular_geometry/source/rapc_patch_gluing_scan_toy.py`
- **Hypothesis:** After local patches form, weak candidate edges can glue fragmented patches into connected sparse geometry.
- **Failure:** The bridge rule added no bridges. The pair-only flow had already discarded the hypergraph information that might have mediated later bridges.
- **Lesson:** Multi-scale gluing needs residual modular memory or a separate weak-link candidate pool.
- **Worth Revisiting?** Yes - redesign bridge candidates and add a no-densification guard.

### F46 - Residual patch gluing with conservative bridge rule
- **Solution:** P02 | **Result:** sparse geometry stable at 9/20, but mean_bridges = 0 | **Reproduce:** `solutions/P02_rapc_modular_geometry/source/rapc_residual_patch_gluing_scan_toy.py`
- **Hypothesis:** Keeping a decaying residual copy of the microscopic hypergraph lets later bridge selection connect patches.
- **Failure:** The residual memory stabilized the spectral result but still did not add bridges under the current conservative rule.
- **Lesson:** The bottleneck is now the bridge objective itself, not merely loss of memory.
- **Worth Revisiting?** Yes - test aggressive and variational bridge objectives.

## Updated Meta-Lessons (from 003 lab)

8. **Reservoir computing is the gradient-free king.** Random fixed dynamics + simple readout beats all complex local/bio/exotic rules.
9. **Diversity > depth for gradient-free.** Multiple diverse simple systems >> one complex system.
10. **HD encoding is a free lunch.** Random bipolar projection adds robustness without any trainable parameters.
11. **Simplified paper implementations are misleading.** Many methods (DTP, DLL, FF, v-PuNN) report 98%+ but need exact architecture/framework to reproduce. Don't dismiss a method based on a quick numpy impl.
12. **CIFAR needs spatial features.** No flat/global approach works on 2D spatial data without convolutional preprocessing.
13. **Block independence + reservoir = powerful combo.** NoProp+Reservoir (95.04%) shows that combining paradigms can exceed both individually.
14. **The gradient-free barrier is real.** All attempts to eliminate gradients entirely (Hebbian, prototypes, HSIC, contrastive) cap at ~44% on MNIST. Local gradient (1-layer depth) remains necessary.
15. **Per-layer probes are the winning pattern.** DirectLocal (98.15%), MonoForward (98.12%), NoProp (97.89%) all use per-layer classification objectives with h.detach() between layers.
16. **CPU advantage grows with depth.** DirectLocal is 3.3x faster than backprop on CPU for 12 layers because backprop's backward pass is sequential while local updates are independent.
17. **DirectLocal works on Transformers.** Validated at 96.22% vs 97.20% BP on ViT-8, proving the paradigm extends beyond MLPs.

## Meta-lessons (from P01 methodological reset, 2026-04)

18. **Confirmation bias eats theory programmes alive.** Nine "passed" empirical tests for LVS turned out on audit to be a mix of pre-existing results (Shaposhnikov-Wetterich m_H), correlational fits (hadron masses), and non-distinctive constraints (d=3 selection). Passing a test means nothing unless the test could have failed.
19. **Distinguish strong and weak forms of every principle.** The strong form of LVS (global flow minimization) was directly falsifiable; the weak form (Planck-scale boundary condition) is only a conditional deduction. Papers must separate them explicitly.
20. **Robustness under metric choice is mandatory.** A stationarity result that exists under sigma2 but not under sigma1 or sigma3 is a parametrization artifact, not physics.
21. **Pre-register or perish for selection-principle tests.** Simulations whose free parameters are tuned to produce known outcomes carry no evidential weight. Every tunable knob must be frozen before the test.
22. **Report negative results.** The April 2026 reset turned a "confirmed" theory into an honest conditional framework. This is progress, not failure.
