---
id: "002"
name: Fixed-Point Substrate
abbreviation: FPS
category: physics-inspired
status: promising
date_created: 2026-04-03
author: Fabien
tags: [physics-inspired, gradient-free, local-learning, hebbian, fixed-point, equilibrium, implicit-network]
best_mnist: 96.44
best_fmnist: 77.15
best_cifar10: 42.24
backprop_mnist_ref: 98.04
backprop_cifar10_ref: 85.83
core_principle: "Intelligence emerges from fixed points in a learnable medium - the stable configuration IS the computation"
key_equation: "Z* = tanh(kappa * Lap(Z*) + W_mix @ Z* + alpha * X + beta)"
activation: tanh
optimizer: entropy-gated-hebbian
layers_optimal: null
---

# 002 - Fixed-Point Substrate (FPS)

## TL;DR
A computational medium that finds stable configurations (fixed points) instead of propagating signals through layers. Input X perturbs the medium, which collapses to equilibrium Z* = f(Z*). The medium's properties (conductivity, coupling, bias) are learned via local entropy-gated Hebbian rules. **Zero backpropagation. Constant memory. 96.44% on MNIST, 77.15% on Fashion-MNIST, 42.24% on CIFAR-10.**

Inspired by Fabien's LVS (Latent Vacuum Stationarity) theory: "La realite nait du point fixe" (It from Fix).

## Core Equation

```python
# The fixed-point map (iterated until convergence):
Z = tanh( kappa_3*Lap3(Z) + kappa_5*Lap5(Z) + kappa_7*Lap7(Z)
          + 0.5*W_mix@Z + alpha*X_proj + beta )

# Learning (all local, no backprop):
gate = sigmoid(H_local + 0.5)          # entropy gate
dkappa = lr * gate * (Z * error)       # Hebbian spatial coupling
dalpha = lr * gate * (X_proj * error)  # input-error correlation
dbeta  = lr * gate * error             # bias correction
dW_mix = lr * (Z_avg.T @ err_avg) / B # cross-channel Hebbian
```

## Version History

| Version | Architecture | MNIST | F-MNIST | CIFAR-10 | Key Change |
|---------|-------------|-------|---------|----------|------------|
| v0.1 | PDE temporal, spatial readout | 9.8% | - | - | Initial PDE approach |
| v0.2 | PDE, global avg pool | 19.8% | - | - | Better readout, still temporal |
| v0.4a | Fixed-point, 4x4, 48ch | 76.2% | - | - | Paradigm shift to Z*=f(Z*) |
| v0.4b | + 7x7 regions + variance | 85.2% | - | - | Better spatial readout |
| v0.4c | + spatial input filters, 64ch | 92.7% | - | - | Retinal receptive fields |
| **v0.5** | **96ch, multi-scale Lap, 2L readout, Anderson** | **96.44%** | **77.15%** | **42.24%** | **All levers** |

## Architecture

```
INPUT (1x28x28 or 3x32x32)
  |
  v
LEARNABLE SPATIAL FILTERS (96 x 5x5) -- retinal receptors
  |
  v
FIXED-POINT ITERATION (7 iters, Anderson accelerated):
  Z <- damped( tanh(sum_scales(kappa_s * Lap_s(Z)) + W_mix@Z + alpha*X + beta) )
  until converged
  |
  v
REGIONAL FEATURES: 7x7 grid, mean+var per channel = 9408 features
  |
  v
TWO-LAYER HEBBIAN READOUT: 9408 -> 256 -> 10
```

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Fixed-point not PDE | PDE needs many timesteps; fixed-point converges in 7 iters |
| Multi-scale Laplacian (3+5+7) | Short/mid/long range coupling in the medium |
| Learnable input filters | Each channel needs unique "view" of input |
| Anderson acceleration | Reduces 11 to 7 iterations |
| Spectral norm on W_mix | Guarantees contraction, ensures fixed point exists |
| Regional mean+variance | Global avg pool destroys spatial info |
| Two-layer Hebbian readout | Linear readout saturates at 85% |
| Entropy-gated learning | Update where uncertain, preserve stable regions |

## What Failed

| Variant | Result | Why |
|---------|--------|-----|
| PDE temporal (v0.1-v0.3) | 9.8-19.8% | Diffusion destroys spatial info |
| Global avg pool readout | 19.8% | Loses all spatial structure |
| Scalar input projection | 92.7% cap | Not enough channel diversity |
| Single-scale Laplacian | 85.2% cap | No long-range interaction |
| Linear readout | 85.2% cap | Cannot learn nonlinear boundaries |

## Files

- `core.py` - Standalone implementation (v0.5)
- `notebook.ipynb` - Experiment notebook
- `results/` - JSON results for all benchmarks

## Reproduction

```bash
python core.py --dataset mnist --epochs 50 --channels 96 --hidden 256
python core.py --dataset fmnist --epochs 50 --channels 96 --hidden 256
python core.py --dataset cifar10 --epochs 60 --channels 96 --hidden 384
```

---

## Next Steps / Roadmap

### Priority 1 - Improve CIFAR-10
- [ ] Multi-resolution substrate (multigrid: 8x8 -> 16x16 -> 32x32)
- [ ] Hierarchical fixed points (coarse-to-fine equilibrium)

### Priority 2 - Scale and Generalize
- [ ] Fashion-MNIST push to 85%+
- [ ] Test on CIFAR-100, STL-10

### Priority 3 - Theoretical Understanding
- [ ] Prove convergence guarantees (Banach fixed-point)
- [ ] Connection to DEQ networks - formal comparison
- [ ] Formalize link to LVS theory

### Speculative / Long-term
- [ ] Substrate as world model
- [ ] Sequence processing via perturbation chains
- [ ] Combine with Entropy-Gated Learning (001)
