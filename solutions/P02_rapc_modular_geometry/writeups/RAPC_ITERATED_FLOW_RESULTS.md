---
title: "Rapc Iterated Flow Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC iterated coarse-graining flow results

This is the sixth RAPC falsification gate.

Previous step:

```text
one global modular hypergraph
-> one automatic coarse-graining
-> one effective pair graph
```

This step iterates:

```text
K_t
-> rho_t = exp(-K_t)/Z
-> all pair reductions rho_ij
-> K_eff(ij) = -log(rho_ij)
-> thresholded effective pair graph
-> K_(t+1)
```

The script is:

```text
rapc_iterated_flow_toy.py
```

## Plain Meaning

This is a toy renormalization flow.

In ordinary language:

```text
hidden correlations
-> visible links
-> treat visible links as the new world
-> repeat
```

If the links become stable, RAPC has a candidate mechanism for emergent
geometry. If the links explode randomly or vanish generically, RAPC needs a
better selection principle.

## Results

### 1. No Reference Hypergraph

The seed contains higher-order modular terms but no reference/bias:

```text
Z0 Z1 Z2
Z2 Z3 Z4
```

Output:

```text
step 0..5: edges = 0
```

Interpretation:

No reference asymmetry means no pair geometry appears. This confirms the lesson
from the previous script:

```text
hypercorrelation alone is not enough
```

### 2. Referenced Hypergraph Chain

The seed contains overlapping hyperedges plus reference biases.

Output summary:

```text
step 0: edges=7  total=1.0424 diameter=2
step 1: edges=8  total=1.0947 diameter=2
step 2: edges=8  total=1.1729 diameter=2
step 3: edges=8  total=1.2857 diameter=2
step 4: edges=8  total=1.4515 diameter=2
step 5: edges=10 total=1.7975 diameter=1
```

Interpretation:

The flow does not settle. It densifies into an almost complete graph.

This is an important warning:

```text
reference-driven coarse-graining can create geometry,
but without a normalization/fixed-point rule it can overconnect everything
```

That would be bad for spacetime, because physical locality is sparse. A theory
where everything becomes close to everything is not our universe.

### 3. Competing Axes Hypergraph

The seed contains `ZZ` and `XX` hyperedges with different reference axes.

Output summary:

```text
step 0: edges=3 total=0.4525
step 1: edges=3 total=0.3830
step 2: edges=3 total=0.3246
step 3: edges=3 total=0.2753
step 4: edges=3 total=0.2337
step 5: edges=3 total=0.1984
```

Interpretation:

The topology is stable:

```text
1-2 XX
0-1 ZZ
3-4 ZZ
```

but the weights decay. This is a better sign than densification: the effective
graph has a stable skeleton, even if the coupling scale runs downward.

### 4. Dense Random Pair Seed

Output summary:

```text
step 0: edges=5
step 1: edges=4
step 2: edges=2
step 3: edges=2
step 4: edges=1
step 5: edges=0
```

Interpretation:

Random pair structure is not protected. The flow simplifies and then dies.

This is also useful: the rule is not merely preserving arbitrary noise. It can
erase unsupported structure.

## What RAPC Gains

The flow produced three distinct behaviors:

```text
no reference       -> empty fixed point
aligned reference  -> densification / overconnection
competing axes     -> stable topology with running weights
random pair seed   -> decay to empty
```

That is already a meaningful taxonomy.

The best RAPC signal so far is:

```text
stable topology + running coupling
```

because that resembles renormalization: the graph skeleton survives while the
coupling scale changes.

## New Falsification Rule

RAPC now needs a seventh gate:

```text
A valid coarse-graining rule must avoid generic densification.
```

Otherwise emergent geometry becomes nonlocal mush: too many pair links, no
light-cone-like locality, no sparse neighborhood structure.

So the next mathematical ingredient should be a normalization principle, for
example:

```text
fixed total modular information
fixed node degree / entropy budget
competition between axes
minimum-description-length selection
spectral normalization
```

The key idea:

```text
spacetime locality may be the stable sparse phase of a modular RG flow
```

not merely the existence of pairwise correlations.

## Remaining Imports

The model still assumes:

```text
finite Type I factors
thermal state exp(-K)/Z
partial trace
Pauli basis
hard threshold
damping parameter
fixed number of elementary nodes
```

The next step is to add a principled information budget:

```text
extract many candidate pair edges
select the sparse graph that preserves the most modular information
under a fixed complexity/entropy budget
```

That would replace the current crude threshold with something closer to a
physical selection principle.
