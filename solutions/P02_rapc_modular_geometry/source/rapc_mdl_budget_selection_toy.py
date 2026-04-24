"""RAPC MDL budget-selection toy model.

Eighth falsification gate:

    candidates edges
    -> choose graph size by a variational/MDL score
    -> iterate sparse flow

Previous step used a hand-chosen budget k. This script selects k by:

    score(G) = information_preserved(G) - lambda * complexity(G)

Toy definitions:

    information_preserved = sum |edge coeff| for selected edges
    complexity            = number of edges + disconnected_penalty

The selector scans k = 0..k_max and chooses the best maximum-spanning forest
under that budget. This is a toy MDL principle: keep the simplest graph that
preserves enough modular information.

The point is not that this exact score is fundamental. The point is to test
whether graph size can be selected instead of injected by hand.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import numpy as np

from rapc_hypergraph_coarse_grain_toy import (
    embedded,
    modular_hamiltonian,
    partial_trace_keep,
    select_pair_edge,
    thermal_state,
)
from rapc_iterated_flow_toy import Edge, FlowStats, graph_stats, rebuild_pair_modular_seed


@dataclass(frozen=True)
class MDLSelection:
    edges: list[Edge]
    score: float
    information: float
    complexity: float
    k: int
    components: int
    disconnected_penalty: float


@dataclass(frozen=True)
class MDLCase:
    name: str
    k_initial: np.ndarray
    lambda_complexity: float
    disconnect_cost: float = 0.12
    k_max: int | None = None
    damping: float = 0.85


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


def select_max_spanning_forest(edges: list[Edge], k: int) -> list[Edge]:
    if k <= 0:
        return []

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
    skipped_cycles = []
    for edge in edges:
        if union(edge.i, edge.j):
            selected.append(edge)
        else:
            skipped_cycles.append(edge)
        if len(selected) >= k:
            return selected

    # If k is larger than the forest size, allow cycle edges by descending weight.
    for edge in skipped_cycles:
        selected.append(edge)
        if len(selected) >= k:
            break
    return selected


def selection_score(
    selected: list[Edge],
    n: int,
    lambda_complexity: float,
    disconnect_cost: float,
    step: int,
) -> MDLSelection:
    stats = graph_stats(selected, n, step)
    information = sum(abs(edge.coeff) for edge in selected)
    disconnected_penalty = disconnect_cost * max(0, stats.components - 1)
    complexity = len(selected) + disconnected_penalty
    score = information - lambda_complexity * complexity
    return MDLSelection(
        edges=selected,
        score=score,
        information=information,
        complexity=complexity,
        k=len(selected),
        components=stats.components,
        disconnected_penalty=disconnected_penalty,
    )


def select_mdl_graph(
    edges: list[Edge],
    n: int,
    lambda_complexity: float,
    disconnect_cost: float,
    step: int,
    k_max: int | None,
) -> MDLSelection:
    upper = min(k_max if k_max is not None else len(edges), len(edges))
    candidates = [
        selection_score(
            select_max_spanning_forest(edges, k),
            n,
            lambda_complexity,
            disconnect_cost,
            step,
        )
        for k in range(upper + 1)
    ]
    # Deterministic tie break: simpler graph wins, then more information.
    return max(candidates, key=lambda item: (item.score, -item.k, item.information))


def iterate_mdl_flow(case: MDLCase, n: int, steps: int = 6) -> tuple[list[FlowStats], list[MDLSelection]]:
    k_seed = case.k_initial
    stats = []
    selections = []
    for step in range(steps):
        candidates = candidate_edges(k_seed, n)
        selection = select_mdl_graph(
            candidates,
            n,
            case.lambda_complexity,
            case.disconnect_cost,
            step,
            case.k_max,
        )
        selections.append(selection)
        stats.append(graph_stats(selection.edges, n, step))
        k_seed = rebuild_pair_modular_seed(selection.edges, n, case.damping)
    return stats, selections


def referenced_hypergraph_chain(n: int, lam: float) -> MDLCase:
    k = 0.52 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.42 * embedded(n, {1: "Z", 2: "Z", 3: "Z"})
    k += 0.46 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.36 * embedded(n, {2: "Z"})
    k += 0.28 * embedded(n, {3: "Z"})
    return MDLCase(f"referenced_chain_lambda_{lam}", k, lambda_complexity=lam)


def noisy_referenced_hypergraph(n: int, lam: float) -> MDLCase:
    rng = np.random.default_rng(23)
    k = 0.50 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.44 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.37 * embedded(n, {2: "Z"})
    k += 0.31 * embedded(n, {4: "Z"})
    for i, j in combinations(range(n), 2):
        noise = rng.normal(scale=0.045)
        if abs(noise) > 0.025:
            k += noise * embedded(n, {i: "X", j: "X"})
    return MDLCase(f"noisy_chain_lambda_{lam}", k, lambda_complexity=lam)


def scale_rich_seed(n: int, lam: float) -> MDLCase:
    """Seed with a few strong edges and many weak generated possibilities."""

    k = 0.62 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.55 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.40 * embedded(n, {1: "X", 4: "X", 5: "X"})
    k += 0.44 * embedded(n, {2: "Z"})
    k += 0.36 * embedded(n, {4: "Z"})
    k += 0.28 * embedded(n, {5: "X"})
    return MDLCase(f"scale_rich_seed_lambda_{lam}", k, lambda_complexity=lam, disconnect_cost=0.10)


def format_edges(edges: list[Edge], limit: int = 8) -> str:
    if not edges:
        return "<none>"
    parts = [f"{edge.i}-{edge.j}{edge.axis[0]}{edge.axis[1]}:{edge.coeff:+.4f}" for edge in edges[:limit]]
    if len(edges) > limit:
        parts.append("...")
    return ", ".join(parts)


def print_case(case: MDLCase, n: int) -> None:
    print(case.name)
    print("-" * len(case.name))
    stats, selections = iterate_mdl_flow(case, n)
    for stat, selection in zip(stats, selections):
        diameter = "None" if stat.diameter is None else str(stat.diameter)
        print(
            f"step={stat.step} k={selection.k} score={selection.score:.4f} "
            f"info={selection.information:.4f} complexity={selection.complexity:.4f} "
            f"edges={stat.edge_count} components={stat.components} "
            f"largest={stat.largest_component} diameter={diameter}"
        )
        print(f"  {format_edges(selection.edges)}")
    print()


def main() -> None:
    print("RAPC MDL budget-selection toy model")
    print("===================================")
    print()

    n5 = 5
    for lam in [0.03, 0.08, 0.14, 0.22]:
        print_case(referenced_hypergraph_chain(n5, lam), n5)

    for lam in [0.05, 0.12]:
        print_case(noisy_referenced_hypergraph(n5, lam), n5)

    n6 = 6
    for lam in [0.06, 0.12, 0.20]:
        print_case(scale_rich_seed(n6, lam), n6)


if __name__ == "__main__":
    main()
