---
id: "005"
name: Direct Local Learning
abbreviation: DLL
domains: [ml, neuro]
category: local-learning
type: learning-rule
status: breakthrough
date_created: 2026-04-03
author: Fabien
tags: [local-learning, per-layer-probe, detach, parallel-training, transformer, no-backprop]

# Results
best_mnist: 98.15
best_cifar10: 56.47

# References
core_principle: "Each layer has its own classifier probe and optimizer. Gradient NEVER flows between layers (h.detach()). All layers train in parallel."
key_equation: "h = layer(h); loss = CE(probe(h), y); loss.backward(); h = h.detach()"
arxiv: null
paper_status: draft
github: null

# Cross-references
builds_on: ["001"]
enables: []
related_to: ["006", "007", "003"]

# Technical
activation: relu
optimizer: adam
layers_optimal: 4
---

# 005 - Direct Local Learning (DLL)

## Core Insight

Each layer in a neural network can learn independently with its own classifier probe and optimizer. The key operation is `h = h.detach()` between layers, which **cuts all gradient flow** between layers. Each layer receives the same target labels and optimizes its own local cross-entropy loss.

## Key Equation

```
for layer, probe, optimizer in zip(layers, probes, optimizers):
    h = layer(h)                      # Forward through this layer only
    loss = cross_entropy(probe(h), y)  # Local loss (per-layer)
    loss.backward()                    # Gradient LOCAL to this layer only
    optimizer.step()                   # Independent update
    h = h.detach()                     # CUT - no global backprop
```

## Properties

- **100% parallélisable**: all layers update independently
- **No global backward pass**: gradient limited to 1 layer depth
- **Memory O(1) per layer** vs O(N) for backprop
- **3.3x faster on CPU** for 12-layer networks (backprop bottlenecked by sequential backward)
- **Works on Transformers**: 96.22% vs 97.20% BP on MNIST ViT (8 blocks)

## Results

### MNIST (MLP: 784-500-300-10)

| Variant | Accuracy | Epochs | Architecture |
|---------|----------|--------|-------------|
| DirectLocal v1 | 97.94% | 20 | Linear probes |
| **DirectLocal v2** | **98.15%** | 20 | 2-layer MLP probes + dropout |
| Backprop baseline | 98.06% | 20 | Same dims, global BP |

### MNIST Deep (784-1000-500-300-100-10)

| Variant | Accuracy | Gap vs BP |
|---------|----------|-----------|
| DirectLocal | 98.01% | -0.26% |
| Backprop | 98.27% | - |

### CIFAR-10 (3072-2000-1000-500-10)

| Variant | Accuracy | Gap vs BP |
|---------|----------|-----------|
| DirectLocal v2 | **56.47%** | **+0.09%** |
| Backprop | 56.38% | - |

### Transformer (ViT-tiny, MNIST)

| Architecture | BP | DirectLocal | Gap |
|-------------|-----|-------------|-----|
| 4 blocks, d=64 | 97.01% | 96.21% | -0.80% |
| 8 blocks, d=64 | 97.20% | 96.22% | -0.98% |

### CPU vs GPU Timing (synthetic data, 1 epoch)

| Depth | CPU BP | CPU DL | **DL Speedup** |
|-------|--------|--------|----------------|
| 3 layers | 13.9s | 14.6s | 0.95x |
| 8 layers | 15.3s | 12.5s | **1.22x** |
| 12 layers | 23.0s | 6.9s | **3.33x** |

## Relation to Existing Work

- Similar to "Greedy Layer-wise Training" (Bengio et al., 2007) but trains ALL layers simultaneously
- Related to "Decoupled Greedy Learning" (Belilovsky et al., 2020)
- Related to "Local Learning with Auxiliary Networks" (Belilovsky et al., 2019)
- Our key contribution: validated that with BatchNorm + deeper probes, the gap to backprop is <0.3%

## Honest Assessment

### Strengths
- Matches backprop on MNIST and CIFAR-10
- Works on Transformers (<1% gap)
- 3.3x CPU speedup for deep networks
- Simple to implement (5 lines of code change from standard training)

### Limitations
- Still uses `loss.backward()` locally (gradient within each layer)
- Probes add ~20% extra parameters
- GPU advantage does not exist (CUDA kernels optimized for global BP)
- Not tested at GPT/LLM scale

## Version History

| Version | Change | MNIST | CIFAR-10 | Status |
|---------|--------|-------|----------|--------|
| V1 | Linear probes + detach | 97.71% | - | Breakthrough |
| V1-deep | 5-layer architecture | 98.01% | - | Breakthrough |
| V2 | 2-layer MLP probes + dropout | **98.15%** | **56.47%** | Breakthrough |
| V2-TF-4 | Transformer 4 blocks | 96.21% | - | Promising |
| V2-TF-8 | Transformer 8 blocks | 96.22% | - | Promising |

## Next Steps / Roadmap

1. Test on GPT-2 scale language modeling
2. Implement multi-threaded C++ version (1 thread per layer)
3. Combine with NoProp denoising for fully decoupled blocks
4. Test on ImageNet with ResNet/ViT architectures
5. Benchmark on FPGA/neuromorphic hardware
