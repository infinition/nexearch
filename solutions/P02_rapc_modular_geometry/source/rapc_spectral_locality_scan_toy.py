"""RAPC spectral-locality phase scan toy model.

Tenth falsification gate:

    Does adding a spectral/locality prior widen the sparse geometric phase-

The previous scan used a simple MDL score:

    information - lambda * complexity

It produced a sparse connected phase, but the phase was narrow. Most random
seeds became fragmented or empty.

This script adds graph-locality terms:

    score = information
            - lambda_edges * edge_count
            - disconnect_cost * (components - 1)
            + nu_gap * algebraic_connectivity
            - mu_degree * degree_variance

This is still a toy rule. The aim is to test whether "geometry" needs a
spectral/locality prior in addition to compression.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import csv
import numpy as np

from rapc_hypergraph_coarse_grain_toy import embedded
from rapc_iterated_flow_toy import Edge, graph_stats, rebuild_pair_modular_seed
from rapc_mdl_budget_selection_toy import candidate_edges, select_max_spanning_forest


@dataclass(frozen=True)
class SpectralParams:
    n: int = 6
    seeds_per_lambda: int = 20
    lambdas: tuple[float, ...] = (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20)
    steps: int = 6
    disconnect_cost: float = 0.25
    nu_gap: float = 0.18
    mu_degree: float = 0.035
    output_csv: str = "rapc_spectral_locality_scan_results.csv"


@dataclass(frozen=True)
class SpectralSelection:
    edges: list[Edge]
    score: float
    information: float
    edge_count: int
    components: int
    algebraic_connectivity: float
    degree_variance: float


def random_hypergraph_seed(n: int, rng: np.random.Generator) -> np.ndarray:
    dim = 2**n
    k = np.zeros((dim, dim), dtype=complex)
    axes = ["X", "Z"]

    for node in range(n):
        if rng.random() < 0.55:
            axis = axes[rng.integers(0, len(axes))]
            coeff = rng.normal(loc=0.0, scale=0.30)
            if abs(coeff) > 0.08:
                k += coeff * embedded(n, {node: axis})

    for triple in combinations(range(n), 3):
        if rng.random() < 0.24:
            axis = axes[rng.integers(0, len(axes))]
            coeff = rng.normal(loc=0.0, scale=0.42)
            if abs(coeff) > 0.12:
                k += coeff * embedded(n, {triple[0]: axis, triple[1]: axis, triple[2]: axis})

    for pair in combinations(range(n), 2):
        if rng.random() < 0.16:
            axis = axes[rng.integers(0, len(axes))]
            coeff = rng.normal(loc=0.0, scale=0.09)
            if abs(coeff) > 0.035:
                k += coeff * embedded(n, {pair[0]: axis, pair[1]: axis})

    return k


def graph_spectral_metrics(edges: list[Edge], n: int) -> tuple[int, float, float]:
    adjacency = np.zeros((n, n), dtype=float)
    for edge in edges:
        weight = abs(edge.coeff)
        adjacency[edge.i, edge.j] += weight
        adjacency[edge.j, edge.i] += weight

    degrees = adjacency.sum(axis=1)
    laplacian = np.diag(degrees) - adjacency
    evals = np.linalg.eigvalsh(laplacian)
    algebraic_connectivity = float(evals[1]) if n > 1 else 0.0
    degree_variance = float(np.var(degrees))

    stats = graph_stats(edges, n, step=0)
    return stats.components, algebraic_connectivity, degree_variance


def spectral_score(
    edges: list[Edge],
    n: int,
    lambda_edges: float,
    disconnect_cost: float,
    nu_gap: float,
    mu_degree: float,
) -> SpectralSelection:
    components, gap, degree_variance = graph_spectral_metrics(edges, n)
    information = sum(abs(edge.coeff) for edge in edges)
    disconnected_penalty = disconnect_cost * max(0, components - 1)
    score = (
        information
        - lambda_edges * len(edges)
        - disconnected_penalty
        + nu_gap * gap
        - mu_degree * degree_variance
    )
    return SpectralSelection(
        edges=edges,
        score=float(score),
        information=float(information),
        edge_count=len(edges),
        components=components,
        algebraic_connectivity=gap,
        degree_variance=degree_variance,
    )


def select_spectral_graph(
    edges: list[Edge],
    n: int,
    lambda_edges: float,
    disconnect_cost: float,
    nu_gap: float,
    mu_degree: float,
) -> SpectralSelection:
    candidates = []
    for k in range(len(edges) + 1):
        selected = select_max_spanning_forest(edges, k)
        candidates.append(
            spectral_score(selected, n, lambda_edges, disconnect_cost, nu_gap, mu_degree)
        )
    return max(
        candidates,
        key=lambda item: (
            item.score,
            item.components == 1,
            -item.edge_count,
            item.information,
        ),
    )


def classify_phase(edge_count: int, components: int, n: int) -> str:
    if edge_count == 0:
        return "empty"
    complete_edges = n * (n - 1) // 2
    if edge_count >= int(0.55 * complete_edges):
        return "dense_nonlocal"
    if components == 1:
        return "sparse_geometric"
    return "fragmented_sparse"


def run_one_flow(k_seed: np.ndarray, params: SpectralParams, lambda_edges: float) -> dict[str, object]:
    edge_counts = []
    components = []
    largest_components = []
    final_selection: SpectralSelection | None = None
    current = k_seed

    for _step in range(params.steps):
        candidates = candidate_edges(current, params.n)
        final_selection = select_spectral_graph(
            candidates,
            params.n,
            lambda_edges,
            params.disconnect_cost,
            params.nu_gap,
            params.mu_degree,
        )
        stats = graph_stats(final_selection.edges, params.n, step=_step)
        edge_counts.append(stats.edge_count)
        components.append(stats.components)
        largest_components.append(stats.largest_component)
        current = rebuild_pair_modular_seed(final_selection.edges, params.n, damping=0.85)

    assert final_selection is not None
    final_stats = graph_stats(final_selection.edges, params.n, step=params.steps - 1)
    return {
        "phase": classify_phase(final_stats.edge_count, final_stats.components, params.n),
        "final_edges": final_stats.edge_count,
        "final_components": final_stats.components,
        "final_largest": final_stats.largest_component,
        "final_diameter": "" if final_stats.diameter is None else final_stats.diameter,
        "final_info": final_selection.information,
        "final_score": final_selection.score,
        "final_gap": final_selection.algebraic_connectivity,
        "final_degree_variance": final_selection.degree_variance,
        "stable_edge_count": len(set(edge_counts[-3:])) == 1,
        "stable_topology": len(set(components[-3:])) == 1 and len(set(largest_components[-3:])) == 1,
    }


def run_scan(params: SpectralParams) -> list[dict[str, object]]:
    rows = []
    master_rng = np.random.default_rng(20260424)
    seed_values = master_rng.integers(0, 2**31 - 1, size=params.seeds_per_lambda)

    for lam in params.lambdas:
        for seed_index, seed_value in enumerate(seed_values):
            rng = np.random.default_rng(int(seed_value))
            k_seed = random_hypergraph_seed(params.n, rng)
            metrics = run_one_flow(k_seed, params, lam)
            rows.append(
                {
                    "lambda": lam,
                    "seed_index": seed_index,
                    **metrics,
                }
            )
    return rows


def write_csv(rows: list[dict[str, object]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]], lambdas: tuple[float, ...]) -> str:
    phases = ["empty", "fragmented_sparse", "sparse_geometric", "dense_nonlocal"]
    lines = []
    for lam in lambdas:
        subset = [row for row in rows if row["lambda"] == lam]
        total = len(subset)
        counts = {phase: sum(1 for row in subset if row["phase"] == phase) for phase in phases}
        stable_geo = sum(
            1
            for row in subset
            if row["phase"] == "sparse_geometric" and row["stable_edge_count"] and row["stable_topology"]
        )
        mean_edges = sum(float(row["final_edges"]) for row in subset) / total
        mean_gap = sum(float(row["final_gap"]) for row in subset) / total
        mean_info = sum(float(row["final_info"]) for row in subset) / total
        lines.append(
            f"lambda={lam:.2f} "
            f"empty={counts['empty']:02d}/{total} "
            f"frag={counts['fragmented_sparse']:02d}/{total} "
            f"geo={counts['sparse_geometric']:02d}/{total} "
            f"dense={counts['dense_nonlocal']:02d}/{total} "
            f"stable_geo={stable_geo:02d}/{total} "
            f"mean_edges={mean_edges:.2f} "
            f"mean_gap={mean_gap:.3f} "
            f"mean_info={mean_info:.3f}"
        )
    return "\n".join(lines)


def main() -> None:
    params = SpectralParams()
    print("RAPC spectral-locality phase scan toy model")
    print("===========================================")
    print(
        f"n={params.n}, seeds_per_lambda={params.seeds_per_lambda}, steps={params.steps}, "
        f"disconnect_cost={params.disconnect_cost}, nu_gap={params.nu_gap}, "
        f"mu_degree={params.mu_degree}"
    )
    print()
    rows = run_scan(params)
    write_csv(rows, params.output_csv)
    print(summarize(rows, params.lambdas))
    print()
    print(f"wrote {params.output_csv}")


if __name__ == "__main__":
    main()
