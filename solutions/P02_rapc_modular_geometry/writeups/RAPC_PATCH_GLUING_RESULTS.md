---
title: "Rapc Patch Gluing Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Patch-gluing RAPC scan testing whether fragmented spectral-locality patches can be connected by weak bridge edges."
tags: [RAPC, modular-geometry, patch-gluing, spectral-locality]
---

# RAPC Patch Gluing Results

## Question

Can local sparse components be connected by adding weak bridge edges after the spectral-locality selector forms patches?

## Result

```text
mean_bridges = 0
sparse_geometric fraction unchanged from the spectral-locality scan
```

Across the same random seeds and lambda values, the bridge rule did not add any edges. The final phase counts matched the spectral-locality baseline.

## Interpretation

This is a useful failure. The first gluing rule was too conservative, and the iterative pair graph had already discarded the microscopic hypergraph information that could have mediated later bridges.

## Lesson

Patch gluing probably needs either:

```text
residual modular memory
separate weak-link candidate pool
more aggressive bridge objective with no-densification guard
```

The failure is recorded as F45 in `archives/failed_approaches.md`.
