---
title: "Rapc Bmv Results"
type: article
date: 2026-04-24
author: Fabien
solution: "P02"
status: draft
abstract: "Gate-by-gate RAPC technical note for modular geometry toy experiments."
tags: [RAPC, modular-geometry, quantum-gravity, toy-model]
---

# RAPC/BMV toy model results

This note records the first technical falsification gate for the RAPC idea.

## Scope

The script `rapc_bmv_toy.py` is a finite-dimensional toy model. It does not
implement Type III von Neumann algebras, Tomita-Takesaki theory, or Witten's
crossed product. It tests only the minimal BMV-like question:

> Can the effective gravitational channel create entanglement between two
> initially separable path qubits-

If the answer were no even in this toy model, RAPC would fail its first BMV
gate. If the answer is yes, the model only survives this gate; it does not prove
the full framework.

## Model

Two equal masses are represented by path qubits:

```text
|L>_A, |R>_A and |L>_B, |R>_B
```

The initial state is separable:

```text
|psi_0> = |+>_A |+>_B
```

The quantum/RAPC-like gravitational channel is represented by a bilocal phase:

```text
U = diag(exp(-i phi_LL), exp(-i phi_LR), exp(-i phi_RL), exp(-i phi_RR))
```

with Newtonian phases:

```text
phi_ij = G m^2 tau / (hbar r_ij)
```

The entangling invariant is:

```text
Delta = phi_LL + phi_RR - phi_LR - phi_RL
```

For the equal superposition initial state, the concurrence is:

```text
C = |sin(Delta / 2)|
```

Local phases can change individual `phi_ij`, but they cannot change `Delta`.
So `Delta` is the finite toy analogue of the non-LOCC gravitational part.

## Baseline run

Parameters:

```text
m   = 1e-14 kg
tau = 1 s
d   = 2e-4 m
s   = 1e-4 m
```

Output:

```text
Delta                     = -0.210963979011
analytic_concurrence      = 0.105286491615
quantum_concurrence       = 0.105286491615
quantum_negativity        = 0.0526432458073
mean_field_negativity     ~= 0
classical_locc_negativity = 0
```

## Interpretation

The result separates the channels cleanly:

```text
bilocal quantum/RAPC-like phase -> entanglement
deterministic mean field        -> no entanglement
classical stochastic LOCC       -> no entanglement
```

This is exactly the BMV logic in miniature: a purely classical mediator
represented as local operations plus shared randomness cannot entangle two
initially separable systems. A bilocal phase can.

## What RAPC gains

RAPC survives the first finite-dimensional BMV gate if its effective
coarse-grained gravitational channel contains a genuine bilocal modular phase,
not merely local phases or shared classical noise.

In algebraic language, the future RAPC derivation must produce an effective
non-factorizing map:

```text
Phi_AB != Phi_A tensor Phi_B
```

and not only an observer-dependent classical stochastic field.

## What remains unproven

The toy model imports several structures that RAPC must eventually derive:

```text
path qubits
spatial distances r_ij
Newtonian phase G m^2 tau / (hbar r)
external interaction time tau
finite Type I Hilbert representation
```

So the next hard task is not to rerun this model. It is to replace the imported
Newtonian phase by a phase generated from:

```text
(global algebra A, state omega, modular flow sigma^omega, coarse-graining C_lambda)
```

The precise target is:

```text
modular/crossed-product data -> invariant bilocal phase Delta
```

If RAPC can derive `Delta` without assuming a background distance and external
time, it becomes a serious candidate framework. If it cannot, the BMV success
above belongs only to ordinary quantum gravity intuition, not to RAPC.
