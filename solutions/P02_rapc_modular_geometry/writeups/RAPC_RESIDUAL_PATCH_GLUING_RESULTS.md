---
title: "Rapc Residual Patch Gluing Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Residual-aware RAPC patch-gluing scan retaining a decaying copy of the microscopic modular hypergraph during pair-graph flow."
tags: [RAPC, modular-geometry, residual-memory, patch-gluing]
---

# RAPC Residual Patch Gluing Results

## Question

If the pair graph keeps access to a decaying residual copy of the microscopic hypergraph, can fragmented patches become connected without densifying?

## Result

```text
lambda=0.02..0.20
sparse_geometric = 9/20
dense_nonlocal = 0/20
mean_bridges = 0
```

Residual memory stabilizes the spectral-locality result and removes dense cases at low lambda, but still does not produce bridge edges.

## Interpretation

The bottleneck is no longer only loss of hypergraph memory. The bridge objective itself is too conservative or not pointed at the right weak-link structure.

## Lesson

The next RAPC step is a bridge-specific variational rule:

```text
maximize patch connectivity gain
penalize densification
preserve weak modular information
test BMV capacity on surviving bridges
```

The limitation is recorded as F46 in `archives/failed_approaches.md`.
