---
id: "006"
name: NoProp Diffusion Learning
abbreviation: NPD
domains: [ml, neuro]
category: local-learning
type: learning-rule
status: breakthrough
date_created: 2026-04-03
author: Fabien
tags: [noprop, diffusion, denoising, local-learning, deepmind, no-backprop, block-independent]

# Results
best_mnist: 97.89
best_cifar10: null

# References
core_principle: "Each block independently denoises a noisy label embedding. No global forward or backward pass. Inspired by diffusion models (DeepMind, March 2025)."
key_equation: "z_pred = block(features, z_noisy, t); loss = MSE(z_pred, z_clean) + CE(proj(z_pred), y)"
arxiv: "2503.24322"
paper_status: draft
github: null

# Cross-references
builds_on: ["004"]
enables: []
related_to: ["005", "007"]

# Technical
activation: gelu
optimizer: adam
layers_optimal: 4
---

# 006 - NoProp Diffusion Learning (NPD)

## Core Insight

Inspired by diffusion models (arXiv:2503.24322, DeepMind March 2025). Each block independently learns to denoise a noisy label embedding. At training: sample noise level t, add noise to label, block predicts clean label. At inference: chain blocks to iteratively denoise from noise to prediction.

**Neither full forward nor full backward propagation is needed.**

## Key Equation

```
# Training (per block, independently):
t = rand(0, 1)                          # Random noise level
z_noisy = alpha(t) * z_clean + sigma(t) * noise
z_pred = block(features, z_noisy, t)     # Block denoises
loss = MSE(z_pred, z_clean) + CE(proj(z_pred), y)

# Inference (sequential denoising):
z = randn(B, label_dim)                  # Start from noise
for i, block in enumerate(blocks):
    t = 1.0 - i / n_blocks               # High noise -> low noise
    z = block(features, z, t)
prediction = output_proj(z)
```

## Results

### MNIST (15 epochs)

| Method | Accuracy | Type |
|--------|----------|------|
| Backprop | 98.22% | Global gradient |
| DirectLocal | 97.98% | Local gradient |
| **NoProp** | **97.89%** | **Block-independent** |

### Published Results (original paper)
| Dataset | NoProp-DT | Backprop | Gap |
|---------|-----------|----------|-----|
| MNIST | 99.47% | 99.46% | +0.01% |
| CIFAR-10 | 79.25% | 79.92% | -0.67% |
| CIFAR-100 | 45.93% | 45.85% | +0.08% |

## Honest Assessment

### Strengths
- Most radical departure: no full forward OR backward pass
- Published in top venue with strong results
- Memory savings: 44% less GPU memory
- Each block is truly independent

### Limitations
- Our implementation is simplified (not full flow-matching)
- Still uses local backward within each block
- Inference requires sequential chaining of blocks (not fully parallel)
- Label dimension is a hyperparameter

## Version History

| Version | Change | MNIST | Status |
|---------|--------|-------|--------|
| V1 | 4 blocks, cosine schedule, hidden=256 | 97.89% | Breakthrough |

## Next Steps

1. Implement full flow-matching objective from paper
2. Test on CIFAR-10 and CIFAR-100
3. Compare memory usage vs backprop
4. Continuous-time variant (NoProp-CT)
