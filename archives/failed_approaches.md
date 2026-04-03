---
purpose: Complete archive of all failed and abandoned approaches with detailed failure analysis
last_updated: 2026-04-03
total_failed: 15
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

## Meta-Lessons (What We Learned From All Failures)

1. **You need an error signal.** Pure topology/geometry/sync without prediction error → random walk → NaN.
2. **Simpler plasticity rules > complex ones.** One signal (entropy) beats 4 signals (NTSO).
3. **PDE dynamics are a dead-end** for learning. Their attractors don't align with classification.
4. **Sigmoid for dense, ReLU for conv.** Never use sigmoid in convolutional layers.
5. **Stability is more important than peak accuracy.** NTSO peaked higher (88.9%) than EG V2 (87.9%) but EG won in the end (97.46%) because it never diverged.
6. **2 layers optimal** for local learning. Deeper = worse credit assignment.
7. **Reconstruction is the key signal.** All successful approaches include "can I predict my input from my output?" as the primary learning driver.
