---
title: "Rapc Subalgebra Selection Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC subalgebra-selection toy model results

This is the third RAPC falsification gate.

Previous step:

```text
chosen rho_AB -> K_AB = -log(rho_AB) -> chosen pair A/B -> K_int -> BMV witness
```

This step:

```text
global rho -> K = -log(rho) -> selected pair/subalgebras -> K_int -> BMV witness
```

The script is:

```text
rapc_subalgebra_selection_toy.py
```

## What changed

The BMV pair is no longer chosen by hand. The algorithm:

1. Starts from a finite global algebra `M_2^(tensor n)`.
2. Computes the modular Hamiltonian `K = -log(rho)`.
3. Expands `K` in the global Pauli basis.
4. Scores every pair of elementary subalgebras by strictly bilocal modular
   coupling strength.
5. Selects the strongest pair and strongest Pauli axis.
6. Builds the BMV witness from that selected modular interaction.

This still imports a finite elementary tensor factorization. So it is not yet a
fully background-free RAPC model. But it does stop choosing `M1` and `M2`
directly.

## Results

### 1. Local-only global state

```text
selected_pair        : None
selected_axis        : None
edge_strength        : 0
pair_negativity      : 0
expected_concurrence : 0
```

Interpretation:

```text
purely local modular data -> no selected BMV pair -> no false entanglement
```

This is the null sanity check.

### 2. Hidden BMV pair

The seed modular generator contains a hidden `ZZ` interaction between factors
`0` and `1`, but the BMV routine is not told this.

Output:

```text
selected_pair        : (0, 1)
selected_axis        : ('Z', 'Z')
edge_strength        : 0.1225
axis_coeff           : 0.35
pair_negativity      : 0.322108843619
expected_concurrence : 0.644217687238
```

Interpretation:

```text
global modular data -> selected pair -> selected ZZ generator -> BMV entanglement
```

The pair negativity is exactly half the expected pure-state concurrence, as it
should be for a two-qubit pure state.

### 3. Competing edges

The global state contains two bilocal interactions:

```text
0.20 Z0 Z1
0.45 X1 X2
```

Output:

```text
selected_pair        : (1, 2)
selected_axis        : ('X', 'X')
edge_strength        : 0.2025
axis_coeff           : 0.45
pair_negativity      : 0.391663454814
expected_concurrence : 0.783326909627
```

Interpretation:

The selection rule correctly picks the dominant modular edge, not the first
edge in the construction.

### 4. Three-body-only global state

The seed modular generator contains only:

```text
0.50 Z0 Z1 Z2
```

Output:

```text
selected_pair        : None
selected_axis        : None
edge_strength        : 0
pair_negativity      : 0
expected_concurrence : 0
```

Interpretation:

This is a productive failure. A purely pairwise subalgebra-selection rule cannot
see an irreducibly three-body modular interaction.

This tells us the next RAPC fork:

```text
Option A: fundamental modular geometry is pairwise/bilocal first.
Option B: fundamental modular geometry is hypergraph-like, and pairwise
          geometry emerges only after coarse-graining.
```

If RAPC chooses option B, the next algorithm must coarse-grain higher-order
modular terms into effective bilocal edges.

## What RAPC gains

RAPC now has a sharper finite chain:

```text
global state rho
-> modular Hamiltonian K
-> selected subalgebras by bilocal modular strength
-> selected interaction generator
-> BMV witness
```

This is the first toy version of:

```text
global algebra + observer/coarse-graining
-> subalgebras A_M1, A_M2
-> modular interaction K_int
-> gravitational entanglement witness
```

## What remains imported

The model still assumes:

```text
finite Type I algebra
elementary tensor factors
Pauli basis
pairwise scoring rule
modular time parameter
```

The next hard step is to replace the pairwise graph by a coarse-grained
hypergraph:

```text
higher-order modular correlations
-> effective pairwise information geometry
-> selected BMV edge
```

That is the first place where a non-geometric RAPC substrate could begin to
generate an emergent geometry instead of merely selecting an existing pair.
