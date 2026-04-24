---
title: "Rapc Sparse Budget Flow Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC sparse information-budget flow results

This is the seventh RAPC falsification gate.

Previous flow:

```text
threshold all sufficiently strong edges
```

Problem:

```text
aligned reference structures can densify into near-complete graphs
```

This flow:

```text
many candidate edges
-> fixed information/complexity budget
-> sparse effective graph
-> BMV-capable surviving links
```

The script is:

```text
rapc_sparse_budget_flow_toy.py
```

## Plain Meaning

The earlier model allowed too many roads to appear. If every place connects to
every other place, there is no useful geometry. Real space is local: you have a
small neighborhood, not direct roads to everything.

This script asks:

```text
Can a compression rule keep only a small number of important links-
```

If yes, then locality might come from an information budget.

## Selection Rules

The script compares three rules:

```text
top_weight
```

Keep the strongest links.

```text
degree_capped
```

Keep strong links, but prevent any node from having too many neighbors.

```text
tree_mdl
```

Keep a maximum spanning tree/forest. This is the strongest compression rule:
explain connectivity with as few links as possible.

## Results

### 1. Referenced Hypergraph Chain

Without budget, this case densified toward a complete graph.

With budget:

```text
top_weight / degree_capped:
  edges stay fixed at 4
  graph remains sparse
  but one node can remain disconnected

tree_mdl:
  edges stay fixed at 4
  graph is connected
  diameter stays 4
```

Representative `tree_mdl` output:

```text
step=0 edges=4 total=0.6462 components=1 diameter=4
step=5 edges=4 total=0.2867 components=1 diameter=4
```

Interpretation:

The tree/MDL rule prevents nonlocal densification while preserving a connected
effective geometry.

The weights run downward, but the skeleton is stable:

```text
stable sparse topology + running coupling
```

This is the best RAPC signal so far.

### 2. Noisy Referenced Hypergraph

All three rules converge to the same sparse connected skeleton:

```text
0-1 ZZ
3-4 ZZ
2-3 ZZ
0-4 XX
```

The graph remains connected with diameter 4 while weights decay.

Interpretation:

The sparse budget suppresses noise without destroying the useful structure. This
is encouraging: the rule is not hypersensitive to small random pair terms.

### 3. Competing Axes Hypergraph

All rules keep the same three-edge structure:

```text
1-2 XX
0-1 ZZ
3-4 ZZ
```

The graph has two components and stable topology, with decreasing weights.

Interpretation:

The compression rule preserves two disconnected effective sectors. This may be
fine if the seed really has disconnected sectors. But for spacetime emergence,
one would need an additional criterion selecting large connected components or
observer-accessible connected patches.

## What RAPC Gains

The key improvement is:

```text
locality from budget, not from arbitrary threshold
```

The flow now avoids the earlier failure mode:

```text
reference alignment -> everything connects to everything
```

Instead we can force:

```text
few links, high explanatory weight, stable topology
```

This resembles a minimum-description-length principle:

```text
the best emergent geometry is the shortest graph that preserves the most
modular information
```

## BMV Capacity

The surviving links remain BMV-capable. The total BMV proxy decreases as
couplings run downward, but does not vanish immediately:

```text
referenced_chain / tree_mdl:
  bmv_capacity step 0 = 1.2682
  bmv_capacity step 5 = 0.5713
```

So the compression rule does not merely erase physical interaction. It preserves
entangling links while simplifying the graph.

## New Candidate RAPC Principle

A serious RAPC candidate should not say:

```text
all correlations become geometry
```

It should say:

```text
geometry is the sparse compression of modular correlations under an information
budget
```

This is much stronger and more physical.

## Remaining Imports

The model still assumes:

```text
finite Type I factors
thermal state exp(-K)/Z
partial trace
Pauli basis
hand-chosen budget k
hand-chosen selection rule
damping parameter
```

The next hard step is to stop choosing the budget by hand.

Possible next rule:

```text
choose k by MDL:
score = information_preserved - lambda * graph_complexity
```

Then the graph size itself would be selected by a variational principle instead
of manually fixed.
