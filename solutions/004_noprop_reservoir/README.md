---
id: "004"
name: NoProp-Reservoir
abbreviation: NPR
domains: [ml, neuro]
category: gradient-free
type: learning-rule
status: promising
date_created: 2026-04-03
author: Fabien
tags: [gradient-free, reservoir-computing, noprop, diffusion, denoising, block-independent, parallel-training, closed-form, original-invention]

# Results
best_mnist: 95.04
best_fashion_mnist: null
best_cifar10: null

# References
core_principle: "Chain of reservoir-based denoisers where each block trains independently in closed form via ridge regression"
key_equation: "y_est = chain_b(reservoir_b(features, y_est_prev) @ W_out_b)"
arxiv: null
paper_status: none
github: null

# Cross-references
builds_on: ["003"]
enables: []
related_to: ["001", "002"]

# Technical
activation: tanh
optimizer: none
layers_optimal: 8
---

# NoProp-Reservoir (NPR) - ORIGINAL INVENTION

## TL;DR

A **novel architecture** that combines NoProp's block-independent training (CoLLAs 2025) with reservoir computing (our best gradient-free paradigm). Each block is a reservoir-based denoiser trained via ridge regression (closed form). All blocks train **independently and in parallel**. Achieves **95.04% on MNIST** with **zero gradients, zero iterations, zero backprop**.

## Why This is Novel

| Property | Standard NoProp | NoProp+Reservoir (Ours) |
|----------|----------------|------------------------|
| Block training | Local backprop within block | **Closed-form ridge regression** |
| Block architecture | MLP with learnable weights | **Fixed random reservoir + readout** |
| Training iterations | Multiple epochs per block | **Single solve (one-shot)** |
| Gradient computation | Local gradients within block | **ZERO gradients anywhere** |
| MNIST accuracy | 80.0% (our impl) | **95.04%** |

## Core Equation

```
Architecture: Chain of B denoising blocks, each with:
  - Random projection: P_b in R^{input x proj_dim}   (FIXED)
  - Random reservoir: W_in_b, W_res_b                 (FIXED)
  - Readout: W_out_b                                   (ONLY trainable part)

Training (each block independently, can be parallel):
  features_b = tanh(X @ P_b)
  noise_b ~ N(0, sigma_b^2)       # sigma_b decreasing schedule
  combined = [features_b | y_clean + noise_b]
  H_b = reservoir(combined)        # Fixed dynamics: tanh(drive + state @ W_res)
  W_out_b = (H_b^T H_b + lambda I)^{-1} H_b^T y_clean   # CLOSED FORM

Inference (sequential chain):
  y_est = random_noise(batch_size, n_classes)
  For b = 1..B:
    features_b = tanh(X @ P_b)
    H_b = reservoir([features_b | y_est])
    y_est = H_b @ W_out_b           # Refined estimate
  prediction = argmax(y_est)
```

## Version History

| Version | Date | MNIST | Key Change |
|---------|------|-------|------------|
| V1 (script #33) | 2026-04-03 | 91.80% | 6 blocks, 1000-dim reservoirs, proof of concept |
| **V2 (script #35)** | **2026-04-03** | **95.04%** | **8 blocks, 1500-dim, diverse spectral radii** |

## Architecture

```
Training (all blocks in parallel):
  Block 1: [features_1, y+noise_high] -> Reservoir_1(sr=0.80) -> Ridge -> W_out_1
  Block 2: [features_2, y+noise_mid]  -> Reservoir_2(sr=0.82) -> Ridge -> W_out_2
  ...
  Block 8: [features_8, y+noise_low]  -> Reservoir_8(sr=0.95) -> Ridge -> W_out_8

Inference (sequential refinement):
  y_est = noise
    -> Block 1 denoises -> y_est_1
      -> Block 2 refines -> y_est_2
        -> ... -> Block 8 -> y_final
```

### Key Parameters (V2)
- 8 blocks with reservoir sizes 1500
- Noise schedule: linearly decreasing from 2.0 to 0.05
- Spectral radii: 0.80 to 0.95 (increasing with block)
- Sparsity: 0.02 to 0.05 (increasing with block)
- Feature projections: 300-600 dim (varied per block for diversity)
- Regularization lambda: 0.05

## Key Design Decisions

| Decision | Chosen | Rejected | Why |
|----------|--------|----------|-----|
| Block type | Random reservoir | MLP (original NoProp) | Closed-form training, no gradients at all |
| Training method | Ridge regression | Iterative SGD | One-shot, mathematically optimal for linear readout |
| Noise schedule | Linear decrease | Constant, cosine | Simple, works well. Cosine could improve. |
| Block diversity | Different projections + spectral radii | Identical blocks | Diversity is key lesson from Ultra Reservoir |
| Multi-pass inference | Tested 1,5,10 passes | Single pass | No improvement from averaging (95.04% for all) |

## What Failed

1. **Multiple inference passes don't help** (1-pass = 5-pass = 10-pass = 95.04%). The chain already converges in one pass.
2. **V1 with smaller reservoirs** (1000-dim): 91.8%. Size matters for reservoir expressiveness.
3. **Fashion-MNIST**: OOM crash with 60k samples * 1500-dim reservoirs * 8 blocks. Needs chunked computation.

## Files

- `core.py` - Standalone NoProp+Reservoir implementation
- `results/v1_mnist.json` - V1 results (91.8%)
- `results/v2_mnist.json` - V2 results (95.04%)
- Full scripts: `../../gradient-free-lab/scripts/33_noprop_reservoir.py` and `35_noprop_reservoir_v2.py`

## Reproduction

```bash
cd gradient-free-lab/scripts
python 33_noprop_reservoir.py     # V1: 91.8% (~2min)
python 35_noprop_reservoir_v2.py  # V2: 95.04% (~5min, needs ~16GB RAM)
```

## Next Steps / Roadmap

### Priority 1
- Fix OOM for Fashion-MNIST (chunked ridge regression)
- Cosine noise schedule (from diffusion models literature)
- More blocks (12-16) with smaller reservoirs to fit in RAM

### Priority 2
- PyTorch implementation for GPU acceleration
- Convolutional variant for CIFAR-10 (patch-level reservoirs)
- Compare with published NoProp results on same benchmarks

### Priority 3
- Theoretical analysis: why does the denoising chain converge?
- Connection to score-based diffusion models
- Write ICML/NeurIPS paper

### Speculative
- Online version: recursive least squares for streaming data
- Neuromorphic implementation: reservoir on SpiNNaker
- Combine with entropy gating (001) for adaptive block activation
