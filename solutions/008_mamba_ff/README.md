---
id: "008"
name: Mamba-FF - SSM x Forward-Forward Hybrid
abbreviation: MFF
domains: [ml, neuro]
category: hybrid
type: learning-rule
status: promising
date_created: 2026-04-03
author: Fabien
tags: [local-learning, state-space-model, mamba, forward-forward, symba, no-backprop, sequence-modeling, selective-scan, goodness]

# Results
best_mnist: 95.37
best_cifar10: null

# References
core_principle: "Selective State Space dynamics (Mamba) for temporal compression + Forward-Forward goodness loss (SymBa) for local layer-wise learning - no backpropagation between layers, no BPTT through time"
key_equation: "h_t = A_bar * h_{t-1} + B_bar * x_t; g = mean(||output||^2); L = log(1 + exp(g_neg - g_pos))"
arxiv: null
paper_status: draft
github: null

# Cross-references
builds_on: ["001"]
enables: ["F03"]
related_to: ["005", "006", "007"]

# Technical
activation: silu
optimizer: adamw
layers_optimal: 4
---

# 008 - Mamba-FF: SSM x Forward-Forward Hybrid

> **TL;DR:** Combines Mamba's selective state space model (temporal memory via discretized ODE) with Forward-Forward's local goodness loss (SymBa variant). Achieves **95.37% on Sequential MNIST** with zero backpropagation between layers and zero BPTT through time. First successful marriage of SSM dynamics with local learning.

---

## Core Insight

The bottleneck of Mamba is BPTT (backprop through time). The bottleneck of Forward-Forward is lack of temporal memory. Combining them solves both:

- **Mamba SSM** handles temporal compression: `h_t = exp(delta*A) * h_{t-1} + delta*B * x_t`
- **Forward-Forward (SymBa)** handles layer decoupling: each layer trained independently with local contrastive loss
- **L2 normalization** between layers prevents magnitude leakage (Hinton's key insight)
- **Hybrid negative data**: 50% wrong label overlay + 50% temporal shuffle with correct labels

## Key Equations

### State Space Dynamics (from Mamba)
```
Continuous: h'(t) = A*h(t) + B*x(t), y(t) = C*h(t)
Discretized (ZOH): h_t = exp(delta*A) * h_{t-1} + delta*B * x_t
Selective: delta, B, C are input-dependent (learned projections)
```

### SymBa Loss (from Forward-Forward, improved)
```
g(x) = mean(||output(x)||^2)           # goodness = mean squared output norm
L = log(1 + exp(g_neg - g_pos))         # SymBa: direct contrast, no threshold
```

### Combined Mamba-FF Layer
```
1. SSM forward: h_t = A_bar * h_{t-1} + B_bar * x_t (temporal state)
2. Output: y_t = C * h_t + D * x_t (gated projection)
3. Goodness: g = mean(||y||^2) over time and features
4. Loss: L_symba = log(1 + exp(g_neg - g_pos))
5. Update: AdamW on THIS layer's params only
6. Pass to next: L2-normalize output, detach gradients
```

### Negative Data Generation (for sequences)
```
Label overlay: embed one-hot label in first K dims of each timestep
Temporal shuffle: permute row order (break temporal structure)
Hybrid: 50% wrong labels + 50% shuffled-correct (diverse negatives)
```

## Architecture

```
Input: (B, 28, 28) - MNIST rows as sequence
  |
  v
Linear(28+10, d_model) - input projection + label space
  |
  v
[MambaFFLayer x 4] - each trained independently:
  | LayerNorm -> Linear -> Conv1d -> SiLU -> SelectiveSSM -> Gate -> Linear
  | Goodness loss (SymBa) -> AdamW update -> L2 normalize -> detach
  v
Inference: try all 10 labels, pick highest total goodness
```

## Version History

| Version | Architecture | Loss | Negatives | MNIST | Epochs | Key Change | Status |
|---------|-------------|------|-----------|-------|--------|------------|--------|
| V1 | d64, 3L, bs128 | FF (threshold=2) | hybrid | 91.28% | 15 | First prototype, row-sequential MNIST | Promising |
| V2 | d128, 4L, bs128 | SymBa | hybrid | **95.37%** | 17/30 | SymBa loss + larger model + cosine LR + AdamW | **Best** |
| V2-final | d128, 4L, bs128 | SymBa | hybrid | ~95.4% | 19/30 | Same, more epochs (still climbing at cutoff) | Best (partial) |

### Detailed V1 Training Curve
```
Epoch  1: 72.92%    Epoch  6: 86.38%    Epoch 11: 89.83%
Epoch  2: 79.85%    Epoch  7: 87.65%    Epoch 12: 90.27%
Epoch  3: 82.34%    Epoch  8: 88.81%    Epoch 13: 90.62%
Epoch  4: 85.83%    Epoch  9: 88.81%    Epoch 14: 91.28% (best)
Epoch  5: 84.04%    Epoch 10: 88.06%    Epoch 15: 91.04%
```

### Detailed V2 Training Curve (SymBa + d128 + cosine LR)
```
Epoch  1: 83.24%    Epoch  7: 92.42%    Epoch 13: 93.31%
Epoch  2: 86.94%    Epoch  8: 92.79%    Epoch 14: 92.40%
Epoch  3: 88.37%    Epoch  9: 92.77%    Epoch 15: 94.16%
Epoch  4: 89.93%    Epoch 10: 93.90%    Epoch 16: 94.21%
Epoch  5: 89.60%    Epoch 11: 93.66%    Epoch 17: 95.37% (best)
Epoch  6: 90.70%    Epoch 12: 94.39%    Epoch 18: 94.41%
                                         Epoch 19: 95.39% (new best, cutoff)
```

## Baselines (Same Task: Row-Sequential MNIST)

| Model | Best | Backprop? | BPTT? | Notes |
|-------|------|-----------|-------|-------|
| Mamba + BPTT | **99.09%** | Yes (global) | Yes | Gold standard |
| Pure FF (Hinton MLP) | 94.50% | No (local) | N/A | Not sequential |
| **Mamba-FF V2 (ours)** | **95.37%** | **No (local)** | **No** | Sequential, no backprop |
| Mamba-FF V1 | 91.28% | No (local) | No | First attempt |
| Mamba-PC | 33.31% | Partial | No | Failed (weak signal) |
| Mamba-HYB (PC+FF) | 9.80% | No | No | Failed (loss conflict) |

**Gap to full backprop: 3.7%** (99.09% vs 95.37%)

## Failed Approaches (within this solution)

### Variant B: Mamba-PC (Predictive Coding)
- **Idea:** Replace FF goodness with temporal prediction error: `L = ||predictor(h_t) - h_{t+1}||^2`
- **Result:** 33.31% best, unstable (drops to 7.6%)
- **Why it failed:** Prediction error is self-supervised - it learns to predict next hidden state but provides NO discriminative signal. The classifier head receives representations that predict well temporally but don't distinguish digit classes. The detached PC loss starves the classifier of useful gradients.
- **Lesson:** Temporal prediction alone is not a sufficient learning signal for classification.

### Variant C: Mamba-HYB (PC + FF combined)
- **Idea:** Combined loss: `L = alpha * L_pc + (1-alpha) * L_ff` with alpha=0.5
- **Result:** 9.80% (random chance), completely dead
- **Why it failed:** The PC loss pulls activations toward temporal prediction (minimize prediction error), while FF pulls them toward contrastive discrimination (maximize goodness gap). These objectives conflict: PC wants smooth, predictable activations; FF wants maximally different activations for pos vs neg. At alpha=0.5, neither signal dominates and the network learns nothing.
- **Lesson:** Don't mix unsupervised temporal loss with contrastive discriminative loss at equal weight. If combining, FF must dominate (alpha < 0.1 for PC).

## Research Context

### What was explored
- 3 deep literature research agents searched in parallel: Forward-Forward (Hinton + SymBa + ASGE + SFF), Mamba/SSM (S4, S4D, Mamba-1, Mamba-2/SSD), and 7 backprop-free methods (Predictive Coding, Target Propagation, PEPITA, Hebbian, Perturbation, Equilibrium Propagation, SID)
- 40+ papers analyzed from 2022-2026
- Key finding from research: SymBa loss (direct contrast without threshold) converges faster than original FF
- Key finding: Predictive Coding temporal extension (tPC) looked promising on paper but failed in practice for discriminative tasks

### Key Implementation Details
- **Selective scan is sequential but only L=28 steps** (row-sequential MNIST) - fast enough in Python
- **L2 normalization between layers is CRITICAL** - without it, layer 2+ detect pos/neg from magnitude
- **Hybrid negatives (wrong labels + temporal shuffle) outperform either alone**
- **Cosine LR annealing** gives significant boost in later epochs (0.003 -> 1e-5)
- **AdamW with weight_decay=1e-4** + gradient clipping at 1.0 for stability

## Honest Assessment

**Strengths:**
- First successful SSM + local learning hybrid (novel contribution)
- 95.37% with zero backprop between layers on a SEQUENTIAL task
- Still climbing at epoch 19 - likely 96%+ with more training
- Biologically plausible: each layer learns independently, no global error signal

**Weaknesses:**
- 3.7% gap to full backprop Mamba (99.09%)
- Inference is 10x slower (must try all 10 labels)
- Not tested on CIFAR-10 or longer sequences
- V2 experiments cut short due to GPU OOM (other processes)
- The SSM within each layer still uses local autograd (not fully gradient-free)

**Open Questions:**
- Can we close the 3.7% gap with hard negative mining?
- Does this scale to longer sequences (512+ tokens)?
- Can we eliminate the per-label inference cost (auxiliary classifier)?
- Would Mamba-2 chunk decomposition enable chunk-local FF losses?

## Next Steps / Roadmap

1. **Complete V2 training** (30 epochs) and run hard negative variant
2. **CIFAR-10 test** with convolutional Mamba blocks
3. **Scalable inference** - add auxiliary classifier head (1 forward pass instead of 10)
4. **Longer sequences** - test on sCIFAR (sequential CIFAR, 1024 steps)
5. **FluidLM integration** - replace BPTT in FluidLM (F03) with Mamba-FF local learning
6. **Paper draft** - first SSM + local learning paper
