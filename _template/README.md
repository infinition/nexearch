---
id: "NNN"
name: Solution Name
abbreviation: SHORT
category: local-learning  # local-learning | gradient-free | transformer-alt | neuromorphic | physics-inspired | hybrid | efficiency | novel-arch
status: promising         # breakthrough | promising | limited | failed
date_created: YYYY-MM-DD
author: Fabien
tags: []
best_mnist: null
best_cifar10: null
backprop_mnist_ref: 98.04
backprop_cifar10_ref: 85.83
core_principle: "One sentence description of the core idea"
key_equation: "dW = ..."
activation: relu
optimizer: describe
layers_optimal: null
---

# NNN — Solution Name

## TL;DR
One paragraph summary of the approach and results.

## Core Equation

```python
# Write the key update rule here
```

## Version History

| Version | Architecture | MNIST | CIFAR-10 | Key Change |
|---------|-------------|-------|----------|------------|
| V1 | ... | ...% | — | Initial |

## Architecture

```
Describe the network architecture here.
```

## Key Design Decisions

| Decision | Why |
|----------|-----|
| ... | ... |

## What Failed

| Variant | Result | Why |
|---------|--------|-----|
| ... | ... | ... |

## Files

- `core.py` — Standalone implementation
- `notebook.ipynb` — Full experiment notebook
- `results/` — JSON results

## Reproduction

```bash
python core.py --dataset mnist --epochs 100
```

---

## Next Steps / Roadmap

### Priority 1 — Improve Accuracy
- [ ] ...

### Priority 2 — Scale to Harder Datasets
- [ ] ...

### Priority 3 — Theoretical Understanding
- [ ] ...

### Speculative / Long-term
- [ ] ...
