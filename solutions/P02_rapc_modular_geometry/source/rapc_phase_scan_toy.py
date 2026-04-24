"""RAPC phase scan toy model.

Ninth falsification gate:

    Is the sparse geometric phase robust across seeds and lambda-

This script generates many random modular hypergraph seeds, runs the MDL
budget-selection flow, and classifies the final effective graph.

Phase labels:

    empty              no edges
    fragmented_sparse  sparse but disconnected
    sparse_geometric   connected and sparse
    dense_nonlocal     too many links

The goal is not numerical physics. The goal is to test whether RAPC's
"geometric phase" is a broad regime of the toy rule or a finely tuned accident.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import csv
import numpy as np

from rapc_hypergraph_coarse_grain_toy import embedded
from rapc_mdl_budget_selection_toy import MDLCase, iterate_mdl_flow


@dataclass(frozen=True)
class ScanParams:
    n: int = 6
    seeds_per_lambda: int = 20
    lambdas: tuple[float, ...] = (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20, 0.26)
    steps: int = 6
    disconnect_cost: float = 0.10
    output_csv: str = "rapc_phase_scan_results.csv"


@dataclass(frozen=True)
class FinalMetrics:
    phase: str
    final_edges: int
    final_components: int
    final_largest: int
    final_diameter: int | None
    final_info: float
    final_score: float
    stable_edge_count: bool
    stable_topology: bool


def random_hypergraph_seed(n: int, rng: np.random.Generator) -> np.ndarray:
    dim = 2**n
    k = np.zeros((dim, dim), dtype=complex)

    axes = ["X", "Z"]

    # Reference biases: enough asymmetry to let hyperedges project to pair edges.
    for node in range(n):
        if rng.random() < 0.55:
            axis = axes[rng.integers(0, len(axes))]
            coeff = rng.normal(loc=0.0, scale=0.30)
            if abs(coeff) > 0.08:
                k += coeff * embedded(n, {node: axis})

    # Three-body hyperedges are the main microscopic substrate.
    for triple in combinations(range(n), 3):
        if rng.random() < 0.24:
            axis = axes[rng.integers(0, len(axes))]
            coeff = rng.normal(loc=0.0, scale=0.42)
            if abs(coeff) > 0.12:
                k += coeff * embedded(n, {triple[0]: axis, triple[1]: axis, triple[2]: axis})

    # Small direct pair contamination/noise.
    for pair in combinations(range(n), 2):
        if rng.random() < 0.16:
            axis = axes[rng.integers(0, len(axes))]
            coeff = rng.normal(loc=0.0, scale=0.09)
            if abs(coeff) > 0.035:
                k += coeff * embedded(n, {pair[0]: axis, pair[1]: axis})

    return k


def classify_phase(edge_count: int, components: int, n: int) -> str:
    if edge_count == 0:
        return "empty"
    complete_edges = n * (n - 1) // 2
    if edge_count >= int(0.55 * complete_edges):
        return "dense_nonlocal"
    if components == 1:
        return "sparse_geometric"
    return "fragmented_sparse"


def final_metrics(case: MDLCase, n: int, steps: int) -> FinalMetrics:
    stats, selections = iterate_mdl_flow(case, n, steps=steps)
    final_stat = stats[-1]
    final_selection = selections[-1]

    edge_counts = [stat.edge_count for stat in stats[-3:]]
    component_counts = [stat.components for stat in stats[-3:]]
    largest_counts = [stat.largest_component for stat in stats[-3:]]
    stable_edge_count = len(set(edge_counts)) == 1
    stable_topology = len(set(component_counts)) == 1 and len(set(largest_counts)) == 1

    return FinalMetrics(
        phase=classify_phase(final_stat.edge_count, final_stat.components, n),
        final_edges=final_stat.edge_count,
        final_components=final_stat.components,
        final_largest=final_stat.largest_component,
        final_diameter=final_stat.diameter,
        final_info=final_selection.information,
        final_score=final_selection.score,
        stable_edge_count=stable_edge_count,
        stable_topology=stable_topology,
    )


def run_scan(params: ScanParams) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    master_rng = np.random.default_rng(20260424)
    seed_values = master_rng.integers(0, 2**31 - 1, size=params.seeds_per_lambda)

    for lam in params.lambdas:
        for seed_index, seed_value in enumerate(seed_values):
            rng = np.random.default_rng(int(seed_value))
            k_seed = random_hypergraph_seed(params.n, rng)
            case = MDLCase(
                name=f"random_seed_{seed_index}_lambda_{lam}",
                k_initial=k_seed,
                lambda_complexity=lam,
                disconnect_cost=params.disconnect_cost,
            )
            metrics = final_metrics(case, params.n, params.steps)
            rows.append(
                {
                    "lambda": lam,
                    "seed_index": seed_index,
                    "phase": metrics.phase,
                    "final_edges": metrics.final_edges,
                    "final_components": metrics.final_components,
                    "final_largest": metrics.final_largest,
                    "final_diameter": "" if metrics.final_diameter is None else metrics.final_diameter,
                    "final_info": metrics.final_info,
                    "final_score": metrics.final_score,
                    "stable_edge_count": metrics.stable_edge_count,
                    "stable_topology": metrics.stable_topology,
                }
            )
    return rows


def write_csv(rows: list[dict[str, object]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]], lambdas: tuple[float, ...]) -> str:
    lines = []
    phases = ["empty", "fragmented_sparse", "sparse_geometric", "dense_nonlocal"]
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
        mean_info = sum(float(row["final_info"]) for row in subset) / total
        lines.append(
            f"lambda={lam:.2f} "
            f"empty={counts['empty']:02d}/{total} "
            f"frag={counts['fragmented_sparse']:02d}/{total} "
            f"geo={counts['sparse_geometric']:02d}/{total} "
            f"dense={counts['dense_nonlocal']:02d}/{total} "
            f"stable_geo={stable_geo:02d}/{total} "
            f"mean_edges={mean_edges:.2f} "
            f"mean_info={mean_info:.3f}"
        )
    return "\n".join(lines)


def main() -> None:
    params = ScanParams()
    print("RAPC phase scan toy model")
    print("=========================")
    print(
        f"n={params.n}, seeds_per_lambda={params.seeds_per_lambda}, "
        f"steps={params.steps}, disconnect_cost={params.disconnect_cost}"
    )
    print()
    rows = run_scan(params)
    write_csv(rows, params.output_csv)
    print(summarize(rows, params.lambdas))
    print()
    print(f"wrote {params.output_csv}")


if __name__ == "__main__":
    main()
