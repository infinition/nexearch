"""RAPC sparse information-budget flow toy model.

Seventh falsification gate:

    many candidate effective edges
    -> fixed information/complexity budget
    -> sparse stable graph
    -> BMV-capable surviving links

The previous iterated flow used a hard threshold. That allowed one important
failure mode: aligned reference structures densified into a near-complete graph.

This script replaces thresholding with a sparse budget:

    keep at most k edges per step

and compares three selection rules:

1. top_weight:
   Keep the largest absolute effective couplings.

2. degree_capped:
   Keep large couplings but cap node degree. This is a crude locality prior.

3. tree_mdl:
   Keep a maximum spanning forest/tree. This is the strongest compression prior:
   connect the system with the smallest number of large explanatory links.

This is not yet a physical principle. It tests whether a compression constraint
can prevent nonlocal densification while preserving BMV-capable links.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import numpy as np

from rapc_hypergraph_coarse_grain_toy import (
    bmv_witness_from_pair_edge,
    embedded,
    modular_hamiltonian,
    partial_trace_keep,
    select_pair_edge,
    thermal_state,
)
from rapc_iterated_flow_toy import Edge, FlowStats, graph_stats, rebuild_pair_modular_seed


@dataclass(frozen=True)
class BudgetCase:
    name: str
    k_initial: np.ndarray
    budget: int
    damping: float = 0.85
    degree_cap: int = 2


def candidate_edges(k_seed: np.ndarray, n: int) -> list[Edge]:
    rho = thermal_state(k_seed)
    out = []
    for pair in combinations(range(n), 2):
        rho_pair = partial_trace_keep(rho, n, pair)
        k_pair = modular_hamiltonian(rho_pair)
        selected = select_pair_edge(k_pair)
        if selected.axis is None or abs(selected.coeff) < 1.0e-10:
            continue
        out.append(Edge(pair[0], pair[1], selected.axis, selected.coeff))
    out.sort(key=lambda edge: abs(edge.coeff), reverse=True)
    return out


def select_top_weight(edges: list[Edge], budget: int, degree_cap: int | None = None) -> list[Edge]:
    del degree_cap
    return edges[:budget]


def select_degree_capped(edges: list[Edge], budget: int, degree_cap: int | None = 2) -> list[Edge]:
    degrees: dict[int, int] = {}
    selected = []
    for edge in edges:
        if degrees.get(edge.i, 0) >= (degree_cap or 2):
            continue
        if degrees.get(edge.j, 0) >= (degree_cap or 2):
            continue
        selected.append(edge)
        degrees[edge.i] = degrees.get(edge.i, 0) + 1
        degrees[edge.j] = degrees.get(edge.j, 0) + 1
        if len(selected) >= budget:
            break
    return selected


def select_tree_mdl(edges: list[Edge], budget: int, degree_cap: int | None = None) -> list[Edge]:
    del degree_cap
    parent: dict[int, int] = {}

    def find(x: int) -> int:
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a: int, b: int) -> bool:
        root_a = find(a)
        root_b = find(b)
        if root_a == root_b:
            return False
        parent[root_b] = root_a
        return True

    selected = []
    for edge in edges:
        if union(edge.i, edge.j):
            selected.append(edge)
        if len(selected) >= budget:
            break
    return selected


SELECTORS = {
    "top_weight": select_top_weight,
    "degree_capped": select_degree_capped,
    "tree_mdl": select_tree_mdl,
}


def total_bmv_capacity(edges: list[Edge]) -> float:
    total = 0.0
    for edge in edges:
        # Reuse the two-qubit witness. Negativity is half concurrence for the
        # pure states used here, so sum of expected concurrence is a clear proxy.
        pair_edge = type("PairEdgeLike", (), {
            "axis": edge.axis,
            "coeff": edge.coeff,
        })()
        witness = bmv_witness_from_pair_edge(pair_edge, modular_time=1.0)
        total += witness["expected_concurrence"]
    return float(total)


def iterate_budget_flow(
    case: BudgetCase,
    n: int,
    selector_name: str,
    steps: int = 6,
) -> tuple[list[FlowStats], list[list[Edge]], list[float]]:
    selector = SELECTORS[selector_name]
    k = case.k_initial
    stats = []
    history = []
    capacities = []
    for step in range(steps):
        candidates = candidate_edges(k, n)
        selected = selector(candidates, case.budget, case.degree_cap)
        history.append(selected)
        stats.append(graph_stats(selected, n, step))
        capacities.append(total_bmv_capacity(selected))
        k = rebuild_pair_modular_seed(selected, n, case.damping)
    return stats, history, capacities


def referenced_hypergraph_chain(n: int) -> BudgetCase:
    k = 0.52 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.42 * embedded(n, {1: "Z", 2: "Z", 3: "Z"})
    k += 0.46 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.36 * embedded(n, {2: "Z"})
    k += 0.28 * embedded(n, {3: "Z"})
    return BudgetCase("referenced_hypergraph_chain", k, budget=4)


def noisy_referenced_hypergraph(n: int) -> BudgetCase:
    rng = np.random.default_rng(23)
    k = 0.50 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.44 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.37 * embedded(n, {2: "Z"})
    k += 0.31 * embedded(n, {4: "Z"})
    for i, j in combinations(range(n), 2):
        noise = rng.normal(scale=0.045)
        if abs(noise) > 0.025:
            k += noise * embedded(n, {i: "X", j: "X"})
    return BudgetCase("noisy_referenced_hypergraph", k, budget=4)


def competing_axes_hypergraph(n: int) -> BudgetCase:
    k = 0.50 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.52 * embedded(n, {1: "X", 2: "X", 3: "X"})
    k += 0.47 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.35 * embedded(n, {2: "Z"})
    k += 0.40 * embedded(n, {3: "X"})
    return BudgetCase("competing_axes_hypergraph", k, budget=3)


def format_edges(edges: list[Edge], limit: int = 8) -> str:
    if not edges:
        return "<none>"
    parts = [f"{edge.i}-{edge.j}{edge.axis[0]}{edge.axis[1]}:{edge.coeff:+.4f}" for edge in edges[:limit]]
    if len(edges) > limit:
        parts.append("...")
    return ", ".join(parts)


def print_flow(case: BudgetCase, n: int, selector_name: str) -> None:
    print(f"{case.name} / {selector_name}")
    print("-" * (len(case.name) + len(selector_name) + 3))
    stats, history, capacities = iterate_budget_flow(case, n, selector_name)
    for stat, edges, capacity in zip(stats, history, capacities):
        diameter = "None" if stat.diameter is None else str(stat.diameter)
        print(
            f"step={stat.step} edges={stat.edge_count} "
            f"total={stat.total_abs_weight:.4f} max={stat.max_abs_weight:.4f} "
            f"components={stat.components} largest={stat.largest_component} "
            f"mean_degree={stat.mean_degree:.2f} diameter={diameter} "
            f"bmv_capacity={capacity:.4f}"
        )
        print(f"  {format_edges(edges)}")
    print()


def main() -> None:
    n = 5
    print("RAPC sparse information-budget flow toy model")
    print("=============================================")
    print()
    cases = [
        referenced_hypergraph_chain(n),
        noisy_referenced_hypergraph(n),
        competing_axes_hypergraph(n),
    ]
    for case in cases:
        for selector_name in SELECTORS:
            print_flow(case, n, selector_name)


if __name__ == "__main__":
    main()
