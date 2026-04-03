---
id: "007"
name: Mono-Forward Learning
abbreviation: MF
domains: [ml, neuro]
category: local-learning
type: learning-rule
status: breakthrough
date_created: 2026-04-03
author: Fabien
tags: [mono-forward, per-layer-projection, local-learning, no-backprop, energy-efficient]

# Results
best_mnist: 98.12
best_cifar10: null

# References
core_principle: "Each layer independently classifies via a learned projection matrix M that maps activations to class logits. Simplest local learning rule that matches backprop."
key_equation: "G = h @ M^T; loss = CE(G, y)"
arxiv: "2501.09238"
paper_status: draft
github: null

# Cross-references
builds_on: []
enables: []
related_to: ["005", "006"]

# Technical
activation: relu
optimizer: adam
layers_optimal: 4
---

# 007 - Mono-Forward Learning (MF)

## Core Insight

From arXiv:2501.09238 (Gong, Li, Abdulla - University of Auckland, January 2025). Each layer independently classifies via a learned projection matrix M. The "goodness" G = activation @ M^T gives per-class scores, trained with local cross-entropy. **The original paper reports beating backprop on CIFAR-10 (56.99% vs 54.25%).**

This is the **simplest** local learning rule that matches backprop.

## Key Equation

```
for layer, M, bn, optimizer in zip(layers, projections, batchnorms, optimizers):
    h = relu(bn(linear(h / (h.norm(dim=1, keepdim=True) + 1e-4))))  # Forward
    logits = M(h)                 # Project to class space
    loss = cross_entropy(logits, y)  # Local loss
    loss.backward()               # Local gradient only
    optimizer.step()
    h = h.detach()                # CUT
```

## Results

### MNIST (15 epochs)

| Variant | Accuracy | Architecture |
|---------|----------|-------------|
| **Mono-Forward Wide** | **98.12%** | 784-1000-500-200-10 |
| Mono-Forward | 97.95% | 784-500-300-10 |
| Backprop baseline | 98.22% | Same dims |

### Published Results (original paper, CNN)
| Dataset | Mono-Forward | Backprop | Delta |
|---------|-------------|----------|-------|
| CIFAR-10 | **56.99%** | 54.25% | **+2.74%** |
| CIFAR-100 | **29.05%** | 27.64% | **+1.41%** |

Paper claims 41% energy reduction and 34% training speedup.

## Honest Assessment

### Strengths
- **Simplest** local learning rule (just a projection matrix per layer)
- Paper reports **beating** backprop on CIFAR-10/100
- 41% energy reduction, 34% faster
- Minimal code changes from standard training

### Limitations
- Our MLP implementation has small gap vs BP (0.1-0.3%)
- Paper uses CNN architectures (we tested MLP only)
- Still uses local backward within each layer
- Not yet tested on Transformers

## Version History

| Version | Change | MNIST | Status |
|---------|--------|-------|--------|
| V1 | Standard dims (784-500-300-10) | 97.95% | Breakthrough |
| V1-Wide | Wider (784-1000-500-200-10) | 98.12% | Breakthrough |

## Next Steps

1. Implement CNN version (as in original paper)
2. Reproduce CIFAR-10 result where MF beats BP
3. Compare with DirectLocal on same architecture
4. Test on Transformer blocks
