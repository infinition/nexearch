---
title: "Rapc Mdl Budget Selection Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC MDL budget-selection results

This is the eighth RAPC falsification gate.

Previous step:

```text
choose budget k by hand
```

This step:

```text
choose graph size by a variational/MDL score
```

The script is:

```text
rapc_mdl_budget_selection_toy.py
```

## Plain Meaning

Instead of telling the model:

```text
keep exactly 4 links
```

we ask it:

```text
how many links are worth keeping-
```

The toy score is:

```text
score = information_preserved - lambda * graph_complexity
```

where:

```text
information_preserved = sum of absolute effective coupling strengths
graph_complexity      = number of links + penalty for disconnected pieces
```

So the model trades off:

```text
accuracy vs simplicity
```

This is a minimum-description-length style rule.

## Results: Three Phases

### 1. Low Complexity Penalty: Dense Phase

Example:

```text
referenced_chain_lambda_0.03
```

Output:

```text
step=0 k=7
step=1 k=8
step=2 k=9
step=3 k=10
step=4 k=10
step=5 k=10
```

Interpretation:

When links are cheap, the model keeps adding links. It flows toward a dense or
complete graph.

This is bad for spacetime locality.

### 2. Intermediate Complexity Penalty: Stable Sparse Phase

Example:

```text
referenced_chain_lambda_0.08
```

Output:

```text
step=0 k=7
step=1 k=7
step=2 k=7
step=3 k=7
step=4 k=7
step=5 k=7
```

The graph stays connected:

```text
components=1
diameter=2
```

Interpretation:

This is the best phase for RAPC so far:

```text
stable graph size
stable connected topology
running coupling strengths
```

This looks like a toy version of emergent geometry under renormalization.

### 3. High Complexity Penalty: Empty Phase

Example:

```text
referenced_chain_lambda_0.22
```

Output:

```text
step=0..5 k=0
```

Interpretation:

When links are too expensive, the best compressed model is empty. This destroys
geometry.

## Noisy Case

For:

```text
noisy_chain_lambda_0.05
```

the model starts with:

```text
k=5, connected
```

then slowly prunes:

```text
step=4 k=4
step=5 k=3
```

Interpretation:

The MDL rule can remove weaker/noisier links as the flow runs. That is useful,
but if the penalty is too high the graph fragments.

## Scale-Rich 6-Node Case

For a richer 6-node seed:

```text
lambda=0.06 -> k=4 then k=3
lambda=0.12 -> k=3 then collapse
lambda=0.20 -> k=2 then collapse
```

Interpretation:

The stable sparse phase is not automatic. It exists only in a window of the
complexity penalty. This resembles a phase diagram:

```text
low lambda        -> dense/nonlocal phase
intermediate lambda -> sparse geometric phase
high lambda       -> empty/no-geometry phase
```

## What RAPC Gains

RAPC now has a genuine toy selection principle:

```text
emergent geometry = best compressed graph of modular correlations
```

More precisely:

```text
geometry appears only in the intermediate MDL phase
```

That is a useful conceptual result. It says spacetime locality might not be a
generic consequence of quantum correlations. It might be a special stable phase
of modular information compression.

## New Falsification Rule

A candidate RAPC rule must show a robust sparse phase:

```text
not dense
not empty
stable under iteration
connected or locally patch-connected
BMV-capable links survive
```

If this phase requires extreme fine-tuning of `lambda`, RAPC is weak. If it
exists broadly across seeds and scales, RAPC becomes more interesting.

## Remaining Imports

The model still assumes:

```text
finite Type I factors
thermal state exp(-K)/Z
partial trace
Pauli basis
hand-chosen lambda
simple score = weight - lambda * complexity
damping parameter
```

The next hard step is:

```text
scan lambda and seeds systematically
to map the phase diagram
```

The key question:

```text
How wide is the sparse geometric phase-
```

That is now testable in code.
