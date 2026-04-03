---
id: "001"
name: Entropy-Gated Learning
abbreviation: EG
category: local-learning
status: breakthrough
date_created: 2026-04-03
author: Fabien
tags: [local-learning, no-backprop, entropy, hebbian, unsupervised-features]
best_mnist: 97.46
best_cifar10: 48.22
backprop_mnist_ref: 98.04
backprop_cifar10_ref: 85.83
core_principle: "Plasticity gated by local entropy — high entropy neurons learn, low entropy neurons stabilize"
key_equation: "dW_i = sigmoid(5*(H_i - 0.4)) * (0.50*recon + 0.25*decorr + 0.25*sparse)"
activation: sigmoid
optimizer: SGD+momentum (local, no global loss)
layers_optimal: 2
---

# 001 — Entropy-Gated Learning (EG)

## TL;DR
Each neuron adjusts its own plasticity based on its **local entropy**. No backpropagation needed in feature layers. Achieves **97.46% on MNIST** (backprop = 98.04%).

## Core Equation

```python
# Per neuron i:
H_i = -mean_batch[ y_i * log(y_i) + (1-y_i) * log(1-y_i) ]   # local entropy
plasticity_i = sigmoid(5 * (H_i - 0.4))                         # entropy gate

# Learning signals (all local):
reconstruction = y.T @ (x - y @ W) / batch_size     # autoencoder-like
decorrelation  = -(corr_offdiag @ W)                 # prevent redundancy
sparsity       = -(mean_activation - 0.12) * W       # control firing rate

# Weight update:
dW_i = plasticity_i * (0.50*reconstruction + 0.25*decorrelation + 0.25*sparsity)

# Stabilization:
momentum = 0.9 * momentum + dW           # SGD momentum
W += cosine_lr(step) * momentum           # cosine annealing
W *= (1 - 1e-5)                           # mild weight decay
clip(dW, max_norm=1.0)                    # gradient clipping
```

## Version History

### MNIST Evolution

| Phase | Version | Architecture | Acc | Epochs | Time/ep | Stable | Key Change | Verdict |
|-------|---------|-------------|-----|--------|---------|--------|------------|---------|
| 3 | **V1** | 2L [500,500] + linear probe | **86.85%** | 5 | ~13s | Yes | First working version. Entropy gate + recon + decorr + sparse | 🏆 First breakthrough |
| 4 | V2-EG | 3L [600,600,300] + linear probe | 87.91% | 20 | ~15s | Yes | Kaiming init, adaptive LR, wider | ✅ Stable, still climbing |
| 4 | V2-NTSO | 3L [600,600,300] + linear probe | 88.90% | 6→NaN | ~15s | **No** | Multi-signal: surprise+entropy+disagreement+temperature | ❌ Peaks at ep 6 then diverges |
| 4 | V2-Hybrid | 4L [700x3,350] + linear probe | 86.07% | 6→decline | ~16s | Partial | Combined EG + NTSO signals | ❌ Too complex, stagnates |
| 5 | **V3** | 2L [500,300] + linear probe | **92.81%** | 50 | ~17s | Yes | `@torch.no_grad`, cosine LR, momentum, grad clip | 🏆 Never plateaus |
| 5 | V3-3L | 3L [400,400,200] + linear probe | ~87% | 47 | ~24s | Yes | Deeper version | ⚠️ Slower convergence (credit assignment) |
| 6 | **V4** | **2L [700,400] + MLP probe** | **97.46%** | 89 | ~35s | Yes | Wider, MLP probe, chunked full decorr | 🏆 **BEST — 0.58% from backprop** |
| 6 | V4+aug | 2L [700,400] + MLP probe + augmentation | 95.98% | 100 | ~65s | Yes | Added RandomAffine | ⚠️ Aug HURTS local learning (-1.5%) |

### CIFAR-10 Attempts

| Phase | Version | Architecture | Acc | Epochs | Stable | Verdict | Failure Reason |
|-------|---------|-------------|-----|--------|--------|---------|----------------|
| 7 | Backprop ref | Conv(3→64→128)+FC | **85.83%** | 43 | Yes | Reference | — |
| 7 | EG-MLP | Dense [3072→1000→500] + MLP probe | 41.16% | 80 | Yes | ⚠️ Limited | No spatial inductive bias |
| 7 | EG-Conv V1 | Conv sigmoid + Dense | 10.00% | 4 | Yes | ❌ Dead-end | Sigmoid saturates conv layers |
| 7 | **EG-Conv V2** | Conv ReLU+LocalBN + Dense | **48.22%** | 6 | Yes | ⚠️ Limited | Channel-average Hebbian loses spatial info |

## Architecture (V4 — Best MNIST)

```
Input (784) ──→ [EG Layer: 784→700, sigmoid, LOCAL] ──→ [EG Layer: 700→400, sigmoid, LOCAL] ──→ [MLP Probe: 400→128→10, backprop]
                      ↑ no backprop                            ↑ no backprop                         ↑ only this uses gradients
```

- **Feature layers:** 100% local (entropy-gated Hebbian)
- **Probe head:** Small MLP with backprop (2.6% of total params)
- **Total params:** ~700K (local: ~680K, probe: ~18K)

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Sigmoid (not ReLU) for MNIST | Needed for binary entropy H = -y*log(y)-(1-y)*log(1-y) |
| 2 layers (not 3+) | Deeper = worse. Credit assignment problem without backprop |
| Reconstruction as primary signal | Pure Hebbian diverges. Reconstruction gives direction |
| Chunked decorrelation | Full NxN correlation matrix = OOM. Chunk by 64 |
| `@torch.no_grad()` | CRITICAL: without it, PyTorch builds graph → memory leak |
| Cosine LR | Linear decay too aggressive, constant too slow |
| Momentum 0.9 | Smooths noisy local updates, cheaper than Adam |

## What Failed (15 other approaches tested)

| Approach | Acc | Why it failed |
|----------|-----|---------------|
| Reaction-Diffusion (PDE) | 11% | Dynamics too slow to converge to useful features |
| Forward-Forward (Hinton) | NaN | Goodness threshold unstable |
| Wave Interference (complex) | NaN | Phase computation numerically unstable |
| Kuramoto Oscillators | NaN | Synchronization doesn't create discriminative features |
| Gossip Protocol | NaN | No error signal from topology alone |
| Learning by Disagreement | NaN | Same — needs SOME form of prediction error |
| Spectral Resonance | NaN | Frequency specialization doesn't help classification |
| Gradient-Free Contrastive | 11% | Diverges — cosine similarity too noisy |
| NTSO (multi-signal hybrid) | 89% | Unstable — competing signals cause divergence |
| Morphogenetic | ~10% | Morphogen dynamics too slow |
| Thermodynamic Free Energy | ~80% | Works but entropy-gating alone is simpler and better |
| Competitive Hebbian | ~75% | k-WTA too aggressive |
| Hyperbolic | ~30% | Poincare projection loses information |
| Optimal Transport | ~20% | Sinkhorn too expensive, softmax kills signal |
| Self-Organized Criticality | ~30% | Power-law avalanches not class-discriminative |

## Files

- `core.py` — Standalone implementation of EG (importable)
- `notebook.ipynb` — Full reproducible experiment notebook
- `results/` — JSON results for all versions

## Reproduction

```bash
cd solutions/001_entropy_gated_learning
python core.py --dataset mnist --epochs 100 --arch 700,400  # → 97.46%
```

---

## Next Steps / Roadmap

### Priority 1 — Close the CIFAR-10 Gap
- [ ] **Better spatial Hebbian for conv layers** — channel-wise average (V2) loses spatial info. Try patch-level correlation: correlate each output feature map position with its receptive field input, not just channel means.
- [ ] **Local Batch Norm with learnable affine** — V2 showed ReLU+LocalBN works for conv. Push further: make BN params learn locally too (match running stats).
- [ ] **Multi-scale features** — add skip connections between EG layers (purely local: concatenate, not residual add).

### Priority 2 — Depth Scaling
- [ ] **Layer-wise pretraining** — train layer 1 until entropy stabilizes, THEN add layer 2. Greedy layer-wise, like old deep belief nets but with entropy gating.
- [ ] **Local target propagation** — combine EG with difference target propagation for deeper networks (EG controls plasticity, DTP provides target signals).

### Priority 3 — Fully Local (No Probe Backprop)
- [ ] **Competitive readout** — replace MLP probe with k-nearest-neighbor on features, or local Hebbian classifier.
- [ ] **Contrastive probe** — Forward-Forward style goodness at the output layer instead of cross-entropy.

### Priority 4 — Theoretical Understanding
- [ ] **Free energy connection** — show that entropy-gated learning minimizes a variational free energy bound.
- [ ] **Convergence proof** — under what conditions does EG provably converge?
- [ ] **Information bottleneck** — does the entropy gate naturally implement an information bottleneck?

### Priority 5 — Speed / Scale
- [ ] **Benchmark vs backprop wall-clock** — local updates have no backward pass. On large models, is it faster?
- [ ] **Distributed training** — no gradient sync needed. Can we trivially parallelize across GPUs?
- [ ] **ImageNet-100 test** — scale to real-world dataset.

### Speculative / Long-term
- [ ] **EG as attention replacement** — can entropy-gated lateral competition replace softmax attention in transformers?
- [ ] **EG + spiking networks** — entropy of spike rates as plasticity gate (neuromorphic hardware compatible).
- [ ] **Meta-learning the entropy threshold** — learn the optimal threshold per layer, per task.
