---
title: Nexearch - Multi-Domain Research Platform
author: Fabien
created: 2026-04-03
last_updated: 2026-04-03
total_solutions: 5
total_experiments: 36
status: active
domains: [ml, physics, quantum, cybersec, robotics, neuro, math]
---

# Nexearch - Multi-Domain Research Platform

> **Purpose:** Centralized registry of ALL research across Machine Learning, Physics, Quantum Computing, Cybersecurity, Robotics, Neuroscience, and Mathematics. Solutions cross-reference each other across domains (e.g., physics theory -> ML algorithm -> robotics application).
>
> **For LLM/agents:** Read this file first. See [AGENT_GUIDE.md](AGENT_GUIDE.md) for contribution instructions. Read [todo.md](todo.md) for ideas to explore next.

---

## Research Domains

| Domain | Tag | Description | Active Solutions |
|--------|-----|-------------|-----------------|
| **Machine Learning** | `ml` | Training algorithms, architectures, VLA/VLM/LLM | 001, 002, F01, F02, F03 |
| **Physics** | `physics` | Theoretical physics, LVS theory, statistical mechanics | 002 |
| **Quantum** | `quantum` | Quantum computing, quantum information, QEC | - |
| **Cybersecurity** | `cybersec` | Cryptography, PQC, adversarial robustness | - |
| **Robotics** | `robotics` | Embodied AI, manipulation, control | F01 |
| **Neuroscience** | `neuro` | Brain-inspired computing, biological plausibility | 001 |
| **Mathematics** | `math` | Pure/applied math supporting other research | - |

## Cross-Domain Knowledge Graph

```
LVS Theory (physics) --builds_on--> Fixed-Point Substrate (ml/physics)
Entropy Gating (neuro) --builds_on--> Entropy-Gated Learning (ml)
Entropy-Gated Learning (ml) --enables--> FluidVLA encoder (robotics)
Fixed-Point Substrate (ml) --enables--> World Model substrate (robotics)
Entropy-Gated (001) --related_to--> Fixed-Point Substrate (002)
```

---

## Research Categories

| Category | Tag | Description | Solutions |
|----------|-----|-------------|-----------|
| **Local Learning** | `local-learning` | Neurons learn from local signals only, no backprop through layers | 001 |
| **Gradient-Free** | `gradient-free` | No gradient computation at all (evolutionary, Hebbian, etc.) | 002 |
| **Transformer Alternatives** | `transformer-alt` | Architectures that replace attention/transformers entirely | — |
| **Neuromorphic** | `neuromorphic` | Spiking networks, event-driven, brain-like computation | — |
| **Physics-Inspired** | `physics-inspired` | From thermodynamics, quantum, statistical mechanics, etc. | 002 |
| **Hybrid Paradigms** | `hybrid` | Combine multiple paradigms (e.g., local + global, symbolic + neural) | — |
| **Training Efficiency** | `efficiency` | Same accuracy, fewer resources (less GPU, less data, less time) | — |
| **Novel Architectures** | `novel-arch` | Fundamentally new network topologies or computation models | - |
| **VLA (Vision-Language-Action)** | `vla` | End-to-end models from pixels+language to robot actions | F01 |
| **VLM (Vision-Language Model)** | `vlm` | Multimodal models combining vision and language | - |
| **LLM (Language Model)** | `llm` | Language models, tokenizers, novel LM architectures | F03 |
| **World Model** | `world-model` | Learn environment dynamics, predict future states | F02 |

### Solution Types

| Type | Description | Metrics |
|------|-------------|---------|
| `learning-rule` | Novel learning algorithm (local, gradient-free, etc.) | accuracy, convergence speed |
| `classifier` | Classification model | accuracy, F1 |
| `vla` | Vision-Language-Action model | success rate, task completion |
| `vlm` | Vision-Language model | accuracy, retrieval score |
| `llm` | Language model | perplexity, BLEU, ROUGE |
| `world-model` | Environment dynamics predictor | MSE, FID, prediction horizon |
| `encoder` | Feature extractor / representation learner | linear probe accuracy, kNN |
| `generator` | Generative model | FID, IS, LPIPS |

---

## Quick Navigation - All Solutions

| ID | Solution | Domains | Category | Status | Best Result | Paper | Builds On | Next Step |
|----|----------|---------|----------|--------|-------------|-------|-----------|-----------|
| 001 | [Entropy-Gated Learning](solutions/001_entropy_gated_learning/) | ml, neuro | local-learning | 🏆 Breakthrough | **97.46%** MNIST | draft | - | Spatial Hebbian for Conv |
| 002 | [Fixed-Point Substrate](solutions/002_fixed_point_substrate/) | ml, physics | physics-inspired | ✅ Promising | **96.44%** MNIST | draft | LVS theory | Multi-resolution substrate |
| F01 | [FluidVLA](https://github.com/infinition/FluidVLA) | ml, robotics | vla | 🔬 WIP | - | none | 001, 002 | Benchmark LIBERO |
| F02 | [FluidWorld](https://github.com/infinition/FluidWorld) | ml, robotics | world-model | 🔬 WIP | - | none | 002 | Benchmark MSE/FID |
| F03 | [FluidLM](https://github.com/infinition/FluidLM) | ml | llm | 🔬 WIP | - | none | - | Benchmark perplexity |

---

## Master Results Tables

### MNIST (Reference: Backprop MLP [700,400] = 98.04%)

#### Successful Approaches — Evolution of Entropy-Gated Learning

| Phase | ID | Algorithm | Equation | Acc | Ep | Time/ep | Stable | Evolution Notes |
|-------|----|-----------|----------|-----|----|---------|--------|-----------------|
| 3 | 001-v1 | Entropy-Gated V1 | `dW = sig(5*(H-0.5)) * (recon+decorr+var)` | 86.85% | 5 | 13s | Yes | First working local algo. Linear probe. |
| 4 | 001-v2-eg | EG V2 (optimized) | same, Kaiming init, adaptive LR | 87.91% | 20 | 15s | Yes | Wider [600x2,300], still climbing at ep 20 |
| 4 | 001-v2-ntso | NTSO V2 (multi-signal) | `plast = f(surprise,entropy,disagree,T)` | **88.90%** | 6 | 15s | **No** | Peak at ep 6, then diverges → NaN at ep 19 |
| 4 | 001-v2-hybrid | EG+NTSO Hybrid | combined 4 signals | 86.07% | 6 | 16s | Partial | Too complex → stagnates. Worse than pure EG. |
| 5 | **001-v3** | **EG V3 (stabilized)** | `+momentum +cosine_LR +grad_clip` | **92.81%** | 50 | 17s | Yes | **Key fix: `@torch.no_grad()`.** 2L > 3L confirmed. |
| 6 | **001-v4** | **EG V4 (push 95%+)** | wider [700,400] + MLP probe | **97.46%** | 89 | 35s | Yes | **BEST: 0.58% gap to backprop.** |
| 6 | 001-v4-aug | EG V4 + data augmentation | same + RandomAffine | 95.98% | 100 | 65s | Yes | Aug hurts local learning (-1.5%) |

#### Fixed-Point Substrate (002) - Evolution

| Phase | ID | Algorithm | Equation | Acc | Ep | Time/ep | Stable | Evolution Notes |
|-------|----|-----------|----------|-----|----|---------|--------|-----------------|
| 8 | 002-v0.1 | PDE Temporal | `dPhi/dt = D + R + S` | 9.80% | 5 | 24s | Yes | PDE dynamics = random level |
| 8 | 002-v0.2 | PDE + global pool | same, better readout | 19.80% | 10 | 21s | Yes | Diffusion destroys spatial info |
| 8 | 002-v0.4a | Fixed-Point 4x4 48ch | `Z* = f(Z*; kappa, alpha, beta)` | 76.20% | 40 | 20s | Yes | Paradigm shift to fixed-point |
| 8 | 002-v0.4b | + 7x7 regions + var | same + better readout | 85.18% | 40 | 35s | Yes | Regional variance captures texture |
| 8 | 002-v0.4c | + spatial filters 64ch | + learnable 5x5 filters | 92.73% | 40 | 30s | Yes | Retinal receptive fields |
| 8 | **002-v0.5** | **Full Power FPS** | `Z* = tanh(multi-Lap + mix + alpha*X + beta)` | **96.44%** | 50 | 35s | Yes | **All levers: 96ch, Anderson, 2L readout** |

#### Failed Approaches (16 algorithms tested)

| Phase | Algorithm | Category | Core Equation | Acc | Ep | Failure Mode | Lesson |
|-------|-----------|----------|---------------|-----|----|-------------|--------|
| 1 | Forward-Forward (Hinton) | local-learning | goodness > threshold | 9.80% | 5 | NaN from ep 1 | Goodness threshold unstable |
| 1 | Predictive Coding | local-learning | prediction error minimization | crash | 0 | Dimension mismatch bug | Complex to implement correctly |
| 1 | Equilibrium Propagation | local-learning | contrastive Hebbian | — | 0 | Not completed | Killed with batch |
| 2 | Reaction-Diffusion | physics-inspired | `du/dt = f(u) + D*laplacian + input` | 11.35% | 4 | Stuck at random | PDE attractors ≠ classification |
| 2 | Thermodynamic Free Energy | physics-inspired | `F = E - T*S`, minimize F locally | — | 0 | Not completed | Ideas reused in NTSO |
| 2 | Wave Interference | physics-inspired | complex phase alignment | — | 0 | Not completed | Phase arithmetic NaN-prone |
| 2 | Kuramoto Oscillators | physics-inspired | `dtheta = omega + K*sin(diff)` | — | 0 | Not completed | Sync = uniform, not discriminative |
| 2 | Gossip Protocol | gradient-free | neighbor belief averaging | — | 0 | Not completed | Averaging destroys information |
| 3 | Learning by Disagreement | gradient-free | `dW = disagree * sign(neighbor-y) * x` | 9.80% | 5 | NaN | No error signal from topology alone |
| 3 | Gradient-Free Contrastive | gradient-free | preserve cosine neighborhoods | 11.35% | 5 | Loss explodes | Cosine similarity too noisy |
| 3 | Spectral Resonance | physics-inspired | `response = drive * sig(freq)` | 9.80% | 5 | NaN | Frequencies drift unbounded |
| 1 | InfoMax | local-learning | maximize H(output) | — | 0 | Not completed | Killed with baselines batch |
| 1 | Competitive Hebbian (kWTA+Oja) | gradient-free | `dW = y*(x - W*y)`, k-WTA | — | 0 | Not completed | Killed with baselines batch |
| 1 | Diff Target Propagation | local-learning | local inverse + DTP target | — | 0 | Not completed | Killed with baselines batch |

#### Frontier Concepts (designed, not benchmarked — code exists in `local_learning_lab/frontier_algorithms.py`)

| Phase | Algorithm | Category | Core Idea | Code Status | Priority to Test |
|-------|-----------|----------|-----------|-------------|-----------------|
| 2 | Morphogenetic Learning | physics-inspired | Cells differentiate via local morphogen gradients (dev biology) | Implemented | Medium |
| 2 | Active Inference (Friston) | local-learning | Each neuron minimizes its own variational free energy | Implemented | High |
| 2 | Cellular Automata Learning | novel-arch | CA rule network learns to produce good local updates (meta-learning) | Implemented | Medium |
| 2 | Hyperbolic Geometry Learning | novel-arch | Neurons in Poincare disk, Mobius transformations as layers | Implemented | Low |
| 2 | Optimal Transport Learning | novel-arch | Sinkhorn iteration as weight matrix, transport plan = connectivity | Implemented | Low |
| 2 | Self-Organized Criticality | physics-inspired | Sandpile dynamics, power-law avalanches as feature extraction | Implemented | Medium |

### CIFAR-10 (Reference: Backprop Conv = 85.83%)

| Phase | ID | Algorithm | Architecture | Acc | Ep | Stable | Verdict | Gap to BP |
|-------|----|-----------|-------------|-----|----|--------|---------|-----------|
| 7 | ref | Backprop Conv | Conv(3→64→128)+FC+Dropout | **85.83%** | 43 | Yes | Reference | — |
| 7 | 001-cifar-v2 | **EG-Conv V2** (ReLU+LocalBN) | EGConv(3→64→128→256)+Pool+EGDense | **48.22%** | 6 | Yes | ⚠️ Limited | -37.6% |
| 7 | 001-cifar-mlp | EG-MLP (flatten 3072d) | EGDense(3072→1000→500) | 41.16% | 80 | Yes | ⚠️ Limited | -44.7% |
| 7 | 001-cifar-v1 | EG-Conv V1 (Sigmoid) | EGConv sigmoid | 10.00% | 4 | Yes | ❌ Dead-end | killed |
| 8 | **002-cifar** | **FPS v0.5** | FPS 96ch 384h 8x8reg | **42.24%** | 60 | Yes | ✅ Promising | -43.6%, still climbing |

### Fashion-MNIST (Reference: Backprop MLP ~ 89%)

| Phase | ID | Algorithm | Architecture | Acc | Ep | Stable | Verdict | Gap to BP |
|-------|----|-----------|-------------|-----|----|--------|---------|-----------|
| 8 | **002-fmnist** | **FPS v0.5** | FPS 96ch 256h 7x7reg | **77.15%** | 50 | Yes | ✅ Promising | -11.9% |

---

## Solution Registry

### 001 — Entropy-Gated Learning (EG)

- **Category:** `local-learning`
- **Status:** 🏆 Breakthrough on MNIST, ⚠️ Limited on CIFAR-10
- **Folder:** [solutions/001_entropy_gated_learning/](solutions/001_entropy_gated_learning/)
- **Date:** 2026-04-03
- **Core Idea:** Each neuron controls its own plasticity based on its LOCAL ENTROPY. High entropy = uncertain = learn fast. Low entropy = confident = stay stable.

**Core Equation:**
```
plasticity_i = sigmoid(k * (H_i - threshold))
H_i = -mean_batch[ y*log(y) + (1-y)*log(1-y) ]

dW_i = plasticity_i * (0.50*recon + 0.25*decorr + 0.25*sparse)
```

**Components:** Entropy Gate, Reconstruction, Decorrelation, Sparsity, SGD+Momentum, Cosine LR, Gradient Clipping

**What failed (15 approaches):** PDE-based (too slow), Phase-based (NaN), Pure topology (no signal), Multi-signal hybrids (unstable), Sigmoid Conv (saturation)

### 002 - Fixed-Point Substrate (FPS)

- **Category:** `physics-inspired`, `gradient-free`
- **Status:** ✅ Promising on MNIST (96.44%), ✅ Promising on F-MNIST (77.15%), ✅ Promising on CIFAR-10 (42.24%)
- **Folder:** [solutions/002_fixed_point_substrate/](solutions/002_fixed_point_substrate/)
- **Date:** 2026-04-03
- **Core Idea:** Intelligence emerges from finding fixed points in a learnable computational medium. Input perturbs the medium, which collapses to equilibrium. The stable configuration IS the computation. Inspired by LVS theory: "La realite nait du point fixe."

**Core Equation:**
```
Z* = tanh( kappa_3*Lap3(Z*) + kappa_5*Lap5(Z*) + kappa_7*Lap7(Z*) + W_mix@Z* + alpha*X + beta )

Learning: gate = sigmoid(H_local + 0.5); dW = lr * gate * Hebbian_correlation
```

**Components:** Multi-scale Laplacian coupling, learnable spatial input filters, entropy-gated Hebbian learning, Anderson acceleration, two-layer nonlinear readout, spectral normalization

**Key Properties:** Zero backpropagation, constant memory O(grid), 7-iteration convergence, GPU-native (all conv/matmul ops)

---

## Datasets Available

| Dataset | Location | Size | Classes | Shape | Available |
|---------|----------|------|---------|-------|-----------|
| MNIST | `datasets/MNIST/` | 60K/10K | 10 | 1x28x28 | Yes |
| CIFAR-10 | `datasets/CIFAR10/` | 50K/10K | 10 | 3x32x32 | Yes |

---

## How to Add a New Solution

1. Copy `_template/` to `solutions/NNN_solution_name/`
2. Fill in `README.md` YAML frontmatter (category, tags, equations)
3. Implement in `core.py` (standalone CLI) + `notebook.ipynb` (imports core, adds visuals)
4. Use `benchmarks/utils.py` for standardized dataloading from `datasets/`
5. Save results JSON to `results/`
6. **Update this README.md** — add row to Quick Navigation + Master Results + Solution Registry

---

## Research Methodology

### Standard Benchmarks

| Dataset | Epochs | Batch Size | Backprop Baseline |
|---------|--------|------------|-------------------|
| MNIST | 100 | 256 | 98.04% (MLP) |
| CIFAR-10 | 100 | 128 | 85.83% (Conv) |
| CIFAR-100 | 100 | 128 | TBD |
| ImageNet-subset | TBD | TBD | TBD |

### Status Codes

- 🏆 **Breakthrough** — Within 3% of SOTA/backprop on target dataset
- ✅ **Promising** — Learns above random, steady improvement
- ⚠️ **Limited** — Works on easy tasks, fails on harder ones
- ❌ **Failed** — Doesn't learn or diverges

### What to Report

Every solution MUST report:
1. **Accuracy** on standard benchmarks
2. **Training time** per epoch
3. **Stability** (does it diverge? plateau? oscillate?)
4. **Param count** (total, and which parts use backprop if any)
5. **Core equation** (the update rule or architecture novelty)

---

## Open Research Directions

### Local Learning
1. CIFAR-10 gap: spatial Hebbian for conv layers
2. Depth scaling: credit assignment beyond 2 layers
3. Fully local probe (no backprop at all)
4. Theoretical connection to free energy principle

### Transformer Alternatives
5. Can attention be replaced by local competition/synchronization?
6. State-space models (Mamba, S4) vs local learning hybrids
7. Can EG-style entropy gating replace softmax attention?

### Gradient-Free
8. Evolutionary strategies at scale
9. Random feedback alignment + entropy gating
10. Can forward-only algorithms match backprop on ImageNet?

### Novel Architectures
11. Hyperbolic neural networks for hierarchical data
12. Topological data analysis as network architecture
13. Continuous-depth networks (Neural ODEs) with local rules

### Efficiency
14. Can local learning be faster than backprop? (no backward pass)
15. Memory efficiency: no activation storage needed
16. Distributed training without gradient synchronization
