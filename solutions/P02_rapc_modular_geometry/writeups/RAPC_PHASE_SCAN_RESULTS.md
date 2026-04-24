---
title: "Rapc Phase Scan Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC phase scan results

This is the ninth RAPC falsification gate.

Previous step:

```text
one or a few hand-designed seeds
-> MDL-selected graph size
```

This step:

```text
many random modular hypergraph seeds
many lambda values
-> classify final phase
```

The script is:

```text
rapc_phase_scan_toy.py
```

The raw CSV is:

```text
rapc_phase_scan_results.csv
```

## Phase Labels

The final graph after six MDL flow steps is classified as:

```text
empty
```

No effective links survive.

```text
fragmented_sparse
```

Some links survive, but the graph is disconnected.

```text
sparse_geometric
```

The graph is connected and sparse.

```text
dense_nonlocal
```

Too many links survive; locality is lost.

## Scan Parameters

```text
n = 6 nodes
20 random seeds per lambda
6 flow steps
disconnect_cost = 0.10
lambda values = 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20, 0.26
```

## Summary

```text
lambda=0.02 empty=00/20 frag=11/20 geo=06/20 dense=03/20 stable_geo=06/20 mean_edges=5.10 mean_info=0.423
lambda=0.04 empty=02/20 frag=14/20 geo=03/20 dense=01/20 stable_geo=03/20 mean_edges=3.55 mean_info=0.333
lambda=0.06 empty=03/20 frag=14/20 geo=02/20 dense=01/20 stable_geo=02/20 mean_edges=2.50 mean_info=0.270
lambda=0.08 empty=07/20 frag=12/20 geo=01/20 dense=00/20 stable_geo=01/20 mean_edges=1.45 mean_info=0.177
lambda=0.10 empty=10/20 frag=10/20 geo=00/20 dense=00/20 stable_geo=00/20 mean_edges=0.80 mean_info=0.107
lambda=0.12 empty=13/20 frag=07/20 geo=00/20 dense=00/20 stable_geo=00/20 mean_edges=0.40 mean_info=0.050
lambda=0.16 empty=18/20 frag=02/20 geo=00/20 dense=00/20 stable_geo=00/20 mean_edges=0.10 mean_info=0.016
lambda=0.20 empty=20/20 frag=00/20 geo=00/20 dense=00/20 stable_geo=00/20 mean_edges=0.00 mean_info=0.000
lambda=0.26 empty=20/20 frag=00/20 geo=00/20 dense=00/20 stable_geo=00/20 mean_edges=0.00 mean_info=0.000
```

## Main Result

The sparse geometric phase exists, but it is not broad under this simple rule.

Best region:

```text
lambda ~= 0.02 to 0.06
```

But even there, most seeds are fragmented rather than connected:

```text
lambda=0.02 -> 6/20 sparse_geometric
lambda=0.04 -> 3/20 sparse_geometric
lambda=0.06 -> 2/20 sparse_geometric
```

For larger lambda, the model collapses toward empty graphs.

## Interpretation

This is a productive failure.

RAPC's current toy MDL rule:

```text
score = information - lambda * complexity
```

is not enough to robustly produce connected sparse geometry from random
hypergraph seeds.

It produces three expected phases:

```text
low lambda     -> some dense/nonlocal risk
medium lambda  -> sparse but usually fragmented
high lambda    -> empty/no geometry
```

But the desired phase:

```text
connected sparse geometric graph
```

is too narrow.

## What This Falsifies

It weakly falsifies the naive claim:

```text
Any modular hypergraph plus simple MDL compression naturally yields geometry.
```

No. Not with this rule.

The emergence of geometry needs at least one more ingredient.

## Likely Missing Ingredient

The score punishes disconnection too weakly and too globally. It does not
explicitly reward local patch formation.

Possible improvements:

```text
stronger connected-patch reward
spectral gap / Laplacian smoothness
dimension estimator penalty
entropic area-law preference
multi-scale consistency
observer-accessibility constraint
```

The most natural next ingredient is:

```text
spectral geometry of the effective graph
```

Instead of asking only:

```text
how many edges-
```

ask:

```text
does the graph have a low-dimensional, smooth, local structure-
```

## Next Gate

Add a spectral-locality score:

```text
score = information
        - lambda * edge_complexity
        - mu * nonlocality_penalty
        + nu * connected_patch_reward
```

Practical graph diagnostics:

```text
components
diameter
average shortest path
Laplacian spectral gap
effective dimension estimate from ball growth
```

The next test should scan again and ask:

```text
Does adding a spectral/locality prior widen the sparse geometric phase-
```

That is the next real RAPC hurdle.
