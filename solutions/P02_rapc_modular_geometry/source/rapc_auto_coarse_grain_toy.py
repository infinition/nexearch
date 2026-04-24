"""RAPC automatic coarse-graining toy model.

Fifth falsification gate:

    global modular hypergraph
    -> automatically choose a coarse-graining map
    -> generate effective pair graph
    -> select BMV edge

The previous model showed that a chosen hidden/reference node can turn a
three-body modular hyperedge into a bilocal edge. This script stops choosing
that node by hand.

Algorithm:

1. Start from a global faithful state rho = exp(-K)/Z.
2. For every visible pair (i,j), trace out the complement.
3. Compute K_eff(i,j) = -log rho_ij.
4. Extract the strongest bilocal Pauli edge in K_eff.
5. Compare it to the direct bilocal coefficient already present in global K.
6. Select the pair with the largest generated coefficient:

       generated = effective - direct

This distinguishes direct pair geometry from geometry induced by coarse-graining
over hidden/reference degrees of freedom.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import numpy as np

from rapc_hypergraph_coarse_grain_toy import (
    NON_ID,
    bmv_witness_from_pair_edge,
    embedded,
    modular_hamiltonian,
    pauli_coefficient,
    partial_trace_keep,
    select_pair_edge,
    thermal_state,
)


@dataclass(frozen=True)
class Candidate:
    visible_pair: tuple[int, int] | None
    traced_out: tuple[int, ...]
    axis: tuple[str, str] | None
    effective_coeff: float
    direct_coeff: float
    generated_coeff: float
    generated_score: float
    effective_score: float
    pair_negativity: float
    expected_concurrence: float


def direct_pair_coeff(k_global: np.ndarray, n: int, pair: tuple[int, int], axis: tuple[str, str]) -> float:
    label = ["I"] * n
    label[pair[0]] = axis[0]
    label[pair[1]] = axis[1]
    return pauli_coefficient(k_global, "".join(label))


def scan_candidate(k_global: np.ndarray, rho_global: np.ndarray, n: int, pair: tuple[int, int]) -> Candidate:
    rho_pair = partial_trace_keep(rho_global, n, pair)
    k_pair = modular_hamiltonian(rho_pair)
    edge = select_pair_edge(k_pair)

    traced_out = tuple(idx for idx in range(n) if idx not in pair)
    if edge.axis is None:
        return Candidate(pair, traced_out, None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    direct = direct_pair_coeff(k_global, n, pair, edge.axis)
    generated = edge.coeff - direct
    witness = bmv_witness_from_pair_edge(edge, modular_time=1.0)
    return Candidate(
        visible_pair=pair,
        traced_out=traced_out,
        axis=edge.axis,
        effective_coeff=edge.coeff,
        direct_coeff=direct,
        generated_coeff=generated,
        generated_score=abs(generated),
        effective_score=abs(edge.coeff),
        pair_negativity=witness["pair_negativity"],
        expected_concurrence=witness["expected_concurrence"],
    )


def zero_candidate() -> Candidate:
    return Candidate(None, (), None, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


def auto_select(k_seed: np.ndarray, n: int) -> dict[str, Candidate]:
    rho_global = thermal_state(k_seed)
    k_global = modular_hamiltonian(rho_global)
    candidates = [scan_candidate(k_global, rho_global, n, pair) for pair in combinations(range(n), 2)]

    best_effective = max(candidates, key=lambda c: c.effective_score, default=zero_candidate())
    best_generated = max(candidates, key=lambda c: c.generated_score, default=zero_candidate())
    if best_effective.effective_score < 1.0e-10:
        best_effective = zero_candidate()
    if best_generated.generated_score < 1.0e-10:
        best_generated = zero_candidate()
    return {"best_effective": best_effective, "best_generated": best_generated}


@dataclass(frozen=True)
class AutoCase:
    name: str
    k_seed: np.ndarray


def local_only_case(n: int) -> AutoCase:
    k = 0.2 * embedded(n, {0: "Z"}) - 0.15 * embedded(n, {1: "X"})
    k += 0.1 * embedded(n, {2: "Z"}) + 0.07 * embedded(n, {3: "X"})
    return AutoCase("local_only", k)


def direct_pair_only_case(n: int) -> AutoCase:
    k = 0.32 * embedded(n, {0: "Z", 1: "Z"})
    k += 0.18 * embedded(n, {2: "Z"}) - 0.11 * embedded(n, {3: "X"})
    return AutoCase("direct_pair_only", k)


def single_hidden_reference_case(n: int) -> AutoCase:
    k = 0.5 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.4 * embedded(n, {2: "Z"})
    k += 0.08 * embedded(n, {3: "X"})
    return AutoCase("single_hidden_reference", k)


def competing_hidden_references_case(n: int) -> AutoCase:
    k = 0.42 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.35 * embedded(n, {2: "Z"})
    k += 0.58 * embedded(n, {1: "X", 2: "X", 3: "X"})
    k += 0.45 * embedded(n, {3: "X"})
    return AutoCase("competing_hidden_references", k)


def mixed_direct_and_generated_case(n: int) -> AutoCase:
    k = 0.25 * embedded(n, {0: "Z", 1: "Z"})
    k += 0.5 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.4 * embedded(n, {2: "Z"})
    return AutoCase("mixed_direct_and_generated", k)


def print_candidate(title: str, candidate: Candidate) -> None:
    print(title)
    print(f"  visible_pair        : {candidate.visible_pair}")
    print(f"  traced_out          : {candidate.traced_out}")
    print(f"  axis                : {candidate.axis}")
    print(f"  effective_coeff     : {candidate.effective_coeff:.12g}")
    print(f"  direct_coeff        : {candidate.direct_coeff:.12g}")
    print(f"  generated_coeff     : {candidate.generated_coeff:.12g}")
    print(f"  generated_score     : {candidate.generated_score:.12g}")
    print(f"  pair_negativity     : {candidate.pair_negativity:.12g}")
    print(f"  expected_concurrence: {candidate.expected_concurrence:.12g}")


def print_case(case: AutoCase, n: int) -> None:
    print(case.name)
    print("-" * len(case.name))
    result = auto_select(case.k_seed, n)
    print_candidate("best_effective", result["best_effective"])
    print_candidate("best_generated", result["best_generated"])
    print()


def main() -> None:
    n = 4
    print("RAPC automatic coarse-graining toy model")
    print("========================================")
    print()
    cases = [
        local_only_case(n),
        direct_pair_only_case(n),
        single_hidden_reference_case(n),
        competing_hidden_references_case(n),
        mixed_direct_and_generated_case(n),
    ]
    for case in cases:
        print_case(case, n)


if __name__ == "__main__":
    main()
