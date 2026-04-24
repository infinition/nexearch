"""RAPC iterated coarse-graining flow toy model.

Sixth falsification gate:

    Does repeated automatic coarse-graining flow toward a stable effective graph-

Earlier scripts showed:

    modular hypergraph -> one-step effective pair graph -> BMV witness

This script repeats the operation:

    K_t -> rho_t -> pair reductions -> K_(t+1)

At each step, every pair reduction `rho_ij` is converted into
`K_eff(ij) = -log(rho_ij)`, the strongest bilocal Pauli edge is extracted, weak
edges are thresholded, and the next modular seed is rebuilt from the surviving
pair edges.

This is still a Type-I finite toy. It is not a proof of geometry. It tests a
necessary behavior: if the RAPC coarse-graining rule produces arbitrary unstable
graphs, it is not a good route to emergent spacetime. Stable sparse graphs are a
better sign.
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


@dataclass(frozen=True)
class Edge:
    i: int
    j: int
    axis: tuple[str, str]
    coeff: float


@dataclass(frozen=True)
class FlowStats:
    step: int
    edge_count: int
    total_abs_weight: float
    max_abs_weight: float
    components: int
    largest_component: int
    mean_degree: float
    diameter: int | None


def extract_effective_edges(
    k_seed: np.ndarray,
    n: int,
    threshold: float,
    max_edges: int | None = None,
) -> list[Edge]:
    rho = thermal_state(k_seed)
    edges: list[Edge] = []
    for pair in combinations(range(n), 2):
        rho_pair = partial_trace_keep(rho, n, pair)
        k_pair = modular_hamiltonian(rho_pair)
        selected = select_pair_edge(k_pair)
        if selected.axis is None or abs(selected.coeff) < threshold:
            continue
        edges.append(Edge(pair[0], pair[1], selected.axis, selected.coeff))

    edges.sort(key=lambda edge: abs(edge.coeff), reverse=True)
    if max_edges is not None:
        return edges[:max_edges]
    return edges


def rebuild_pair_modular_seed(edges: list[Edge], n: int, damping: float) -> np.ndarray:
    dim = 2**n
    k_next = np.zeros((dim, dim), dtype=complex)
    for edge in edges:
        k_next += damping * edge.coeff * embedded(n, {edge.i: edge.axis[0], edge.j: edge.axis[1]})
    return k_next


def graph_stats(edges: list[Edge], n: int, step: int) -> FlowStats:
    adjacency = {idx: set() for idx in range(n)}
    for edge in edges:
        adjacency[edge.i].add(edge.j)
        adjacency[edge.j].add(edge.i)

    seen: set[int] = set()
    component_sizes = []
    for node in range(n):
        if node in seen:
            continue
        stack = [node]
        seen.add(node)
        size = 0
        while stack:
            cur = stack.pop()
            size += 1
            for nxt in adjacency[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        component_sizes.append(size)

    diameter = graph_diameter(adjacency) if len(component_sizes) == 1 and edges else None
    total_abs = sum(abs(edge.coeff) for edge in edges)
    max_abs = max((abs(edge.coeff) for edge in edges), default=0.0)
    return FlowStats(
        step=step,
        edge_count=len(edges),
        total_abs_weight=total_abs,
        max_abs_weight=max_abs,
        components=len(component_sizes),
        largest_component=max(component_sizes, default=0),
        mean_degree=2.0 * len(edges) / n,
        diameter=diameter,
    )


def graph_diameter(adjacency: dict[int, set[int]]) -> int:
    diameter = 0
    for start in adjacency:
        distance = {start: 0}
        queue = [start]
        for cur in queue:
            for nxt in adjacency[cur]:
                if nxt not in distance:
                    distance[nxt] = distance[cur] + 1
                    queue.append(nxt)
        diameter = max(diameter, max(distance.values(), default=0))
    return diameter


def iterate_flow(
    k_initial: np.ndarray,
    n: int,
    steps: int = 6,
    threshold: float = 0.04,
    damping: float = 0.85,
    max_edges: int | None = None,
) -> tuple[list[FlowStats], list[list[Edge]]]:
    k = k_initial
    stats = []
    history = []
    for step in range(steps):
        edges = extract_effective_edges(k, n, threshold, max_edges=max_edges)
        history.append(edges)
        stats.append(graph_stats(edges, n, step))
        k = rebuild_pair_modular_seed(edges, n, damping)
    return stats, history


@dataclass(frozen=True)
class FlowCase:
    name: str
    k_initial: np.ndarray
    threshold: float = 0.04
    damping: float = 0.85
    max_edges: int | None = None


def no_reference_hypergraph(n: int) -> FlowCase:
    k = 0.52 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.48 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    return FlowCase("no_reference_hypergraph", k)


def referenced_hypergraph_chain(n: int) -> FlowCase:
    k = 0.52 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.42 * embedded(n, {1: "Z", 2: "Z", 3: "Z"})
    k += 0.46 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.36 * embedded(n, {2: "Z"})
    k += 0.28 * embedded(n, {3: "Z"})
    return FlowCase("referenced_hypergraph_chain", k)


def competing_axes_hypergraph(n: int) -> FlowCase:
    k = 0.50 * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += 0.52 * embedded(n, {1: "X", 2: "X", 3: "X"})
    k += 0.47 * embedded(n, {2: "Z", 3: "Z", 4: "Z"})
    k += 0.35 * embedded(n, {2: "Z"})
    k += 0.40 * embedded(n, {3: "X"})
    return FlowCase("competing_axes_hypergraph", k, threshold=0.035)


def dense_random_pair_seed(n: int) -> FlowCase:
    rng = np.random.default_rng(11)
    k = np.zeros((2**n, 2**n), dtype=complex)
    axes = ["X", "Z"]
    for i, j in combinations(range(n), 2):
        coeff = rng.normal(scale=0.13)
        if abs(coeff) < 0.04:
            continue
        axis = axes[rng.integers(0, len(axes))]
        k += coeff * embedded(n, {i: axis, j: axis})
    return FlowCase("dense_random_pair_seed", k, threshold=0.055, damping=0.75, max_edges=7)


def format_edges(edges: list[Edge], limit: int = 8) -> str:
    if not edges:
        return "<none>"
    parts = []
    for edge in edges[:limit]:
        parts.append(f"{edge.i}-{edge.j}{edge.axis[0]}{edge.axis[1]}:{edge.coeff:+.4f}")
    if len(edges) > limit:
        parts.append("...")
    return ", ".join(parts)


def print_case(case: FlowCase, n: int) -> None:
    print(case.name)
    print("-" * len(case.name))
    stats, history = iterate_flow(
        case.k_initial,
        n,
        threshold=case.threshold,
        damping=case.damping,
        max_edges=case.max_edges,
    )
    for stat, edges in zip(stats, history):
        diameter = "None" if stat.diameter is None else str(stat.diameter)
        print(
            f"step={stat.step} edges={stat.edge_count} "
            f"total={stat.total_abs_weight:.4f} max={stat.max_abs_weight:.4f} "
            f"components={stat.components} largest={stat.largest_component} "
            f"mean_degree={stat.mean_degree:.2f} diameter={diameter}"
        )
        print(f"  {format_edges(edges)}")
    print()


def main() -> None:
    n = 5
    print("RAPC iterated coarse-graining flow toy model")
    print("============================================")
    print()
    cases = [
        no_reference_hypergraph(n),
        referenced_hypergraph_chain(n),
        competing_axes_hypergraph(n),
        dense_random_pair_seed(n),
    ]
    for case in cases:
        print_case(case, n)


if __name__ == "__main__":
    main()
