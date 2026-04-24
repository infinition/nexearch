---
title: "Rapc Hypergraph Coarse Grain Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC hypergraph coarse-graining toy model results

This is the fourth RAPC falsification gate.

The previous script showed a productive failure:

```text
pure three-body modular term -> no pair selected by a pairwise scanner
```

This script tests the next possibility:

```text
higher-order modular correlation
-> coarse-grain a hidden/reference node
-> effective pairwise modular edge
-> BMV witness
```

The script is:

```text
rapc_hypergraph_coarse_grain_toy.py
```

## Setup

Start from a global modular Hamiltonian on three elementary factors. The key
hyperedge is:

```text
K = J Z0 Z1 Z2
```

A pairwise scan of the global `K` sees no `Z0 Z1` term. The pair edge is absent
before coarse-graining.

Then factor `2` is traced out:

```text
rho_01 = Tr_2 rho_012
K_01   = -log(rho_01)
```

The question is whether `K_01` contains an effective pair term.

## Results

### 1. Unbiased Hidden Node

```text
K = J Z0 Z1 Z2
```

Output:

```text
pre_best_pair_coeff : 0
selected_axis       : None
effective_coeff     : 0
pair_negativity     : 0
```

Interpretation:

An unbiased hidden node destroys the pair signal. Summing over `Z2 = +/- 1`
cancels the effective `Z0 Z1` distinction.

This matters conceptually:

```text
hypergraph structure alone is not enough
```

There must also be a reference/asymmetry/state condition.

### 2. Biased Hidden Node

```text
K = J Z0 Z1 Z2 + h Z2
```

Output:

```text
pre_best_pair_coeff : ~0
selected_axis       : ('Z', 'Z')
effective_coeff     : -0.177419370572
analytic_coeff      : -0.177419370572
pair_negativity     : 0.173719578459
expected_concurrence: 0.347439156917
```

Interpretation:

Before coarse-graining, there is still no direct pair edge. After tracing out
the biased reference node, an effective `Z0 Z1` modular interaction appears.

The exact diagonal decimation formula is:

```text
K_eff(z0,z1) = -log sum_z2 exp[-J z0 z1 z2 - h z2]
```

So the effective pair coefficient is:

```text
J_eff = -1/2 log[cosh(h + J) / cosh(h - J)]
```

The numerical result matches exactly.

### 3. Transverse Reference Node

```text
K = J Z0 Z1 X2 + h X2
```

Output:

```text
pre_best_pair_coeff : ~0
selected_axis       : ('Z', 'Z')
effective_coeff     : -0.177419370572
analytic_coeff      : -0.177419370572
pair_negativity     : 0.173719578459
expected_concurrence: 0.347439156917
```

Interpretation:

The hidden/reference node does not have to be `Z` specifically. It has to be
bias-aligned with the hyperedge axis that carries the hidden information.

### 4. Irrelevant Noncommuting Bias

```text
K = J Z0 Z1 Z2 + h X2
```

Output:

```text
pre_best_pair_coeff : ~0
selected_axis       : None
effective_coeff     : 0
pair_negativity     : 0
```

Interpretation:

A noncommuting bias that is not aligned with the hyperedge does not produce the
same pairwise edge in this simple thermal coarse-graining.

## What RAPC Gains

This is the first toy mechanism where a pairwise/geometric relation is not
fundamental. The relation:

```text
0 -- 1
```

appears only after coarse-graining:

```text
Z0 Z1 Z2 + reference state of node 2
-> effective Z0 Z1
```

So RAPC now has a finite proof-of-concept for:

```text
hypergraph modular substrate
-> observer/reference-dependent pair geometry
-> BMV-entangling edge
```

## Conceptual Lesson

The emergent geometry is not just "correlation strength." It is:

```text
correlation strength + coarse-graining choice + reference asymmetry
```

Without a reference condition, higher-order modular structure can remain
invisible to pairwise geometry.

This is a useful warning for the full RAPC program: an "observer" is not an
optional philosophical add-on. It may be mathematically necessary for pairwise
spacetime relations to emerge from hypergraph correlations.

## Remaining Imports

The model still assumes:

```text
finite Type I factors
an elementary tensor split
a chosen hidden/reference node
thermal state rho = exp(-K)/Z
partial trace as the coarse-graining rule
modular time parameter
```

The next hard step is to make the hidden/reference node selection automatic:

```text
global modular hypergraph
-> choose a coarse-graining map C_lambda
-> generate effective pair graph
-> select BMV edge
```

In other words:

```text
not just "does coarse-graining work-"
but "which coarse-graining is selected by the state/observer-"
```
