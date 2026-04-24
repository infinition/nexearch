---
title: "Rapc Modular Phase Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC modular-phase toy model results

This is the second RAPC falsification gate.

The first script, `rapc_bmv_toy.py`, imported a Newtonian phase:

```text
phi_ij = G m^2 tau / (hbar r_ij)
```

This script, `rapc_modular_phase_toy.py`, removes that import. It starts from a
faithful two-qubit state `rho_AB` and derives:

```text
K_AB = -log(rho_AB)
```

Then it keeps only the strictly nonlocal Pauli part of the modular interaction.
This is the finite-dimensional stand-in for:

```text
(A, omega, sigma^omega, coarse-graining) -> bilocal modular generator
```

## Falsification question

Can an invariant bilocal phase be extracted from modular data alone-

In this toy setting:

```text
rho_AB -> K_AB -> K_int -> U_mod = exp(-i s K_int)
```

If `K_int = 0`, the channel cannot entangle. If `K_int` contains a coherent
bilocal term, the channel can entangle.

## Results

### 1. Product local modular state

```text
mutual_information : ~0
k_int_norm         : ~0
output_concurrence : ~0
output_negativity  : ~0
sampled_power      : ~0
k_int_coeffs       : <none>
```

Interpretation:

```text
product modular data -> no bilocal generator -> no entanglement
```

This is the expected null test.

### 2. Diagonal bilocal modular state

Input modular generator:

```text
K = local terms + 0.35 ZZ
```

Extracted result:

```text
mutual_information : 0.0544631813243
k_int_norm         : 0.7
output_concurrence : 0.644217687238
output_negativity  : 0.322108843619
sampled_power      : 0.644217687238
k_int_coeffs       : ZZ: 0.35
```

Interpretation:

```text
modular correlations -> coherent ZZ generator -> BMV-style entanglement
```

For a `ZZ` modular generator, the phase invariant is:

```text
Delta_mod = 4 s J
```

and for `J = 0.35`, `s = 1`:

```text
C = |sin(Delta_mod / 2)| = |sin(0.7)| = 0.644217687238
```

The numerical result matches exactly.

### 3. Noncommuting bilocal modular state

Input modular generator:

```text
K = local terms + 0.35 XX
```

Extracted result:

```text
mutual_information : 0.0567868243801
k_int_norm         : 0.7
output_concurrence : ~0 on |++>
output_negativity  : ~0 on |++>
sampled_power      : 0.644217687238
k_int_coeffs       : XX: 0.35
```

Interpretation:

`XX` is bilocal and entangling in general, but `|++>` is an eigenstate of `XX`,
so the BMV-style `|++>` input does not entangle. The sampled entangling power is
nonzero, which confirms the generator is genuinely nonlocal.

## What RAPC gains

This toy model replaces:

```text
distance + external time + Newtonian potential
```

with:

```text
state rho_AB + modular Hamiltonian -log(rho_AB) + nonlocal projection
```

So RAPC passes a sharper finite-dimensional gate:

```text
correlations can define the bilocal phase generator
```

Instead of assuming a gravitational phase, the phase is read from the modular
structure of the state.

## Remaining imports

The toy model still imports:

```text
finite Type I Hilbert space
two-qubit tensor factorization
choice of rho_AB
choice of modular time s
Pauli-basis nonlocal projection
```

The next real RAPC question is therefore:

```text
Can the factorization/subalgebras and the modular parameter s emerge from
observer-accessible algebraic data rather than being chosen by hand-
```

The next target is not yet Einstein. It is:

```text
global algebra + observer/coarse-graining
-> selected subalgebras A_M1, A_M2
-> modular interaction K_int
-> BMV witness
```

That is the first version that would stop relying on an explicit qubit tensor
split.
