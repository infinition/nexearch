"""RAPC multi-scale patch-gluing scan toy model.

Eleventh falsification gate:

    local patches first
    -> weak bridge selection between patches
    -> connected sparse geometry without densification

The spectral-locality scan widened the geometric phase, but about half the
random seeds remained fragmented. This script tests whether a second-scale
"patch gluing" step can connect sparse components using weak candidate bridges.

Algorithm per flow step:

1. Generate all candidate effective pair edges from modular reductions.
2. Select a sparse local graph with the spectral-locality score.
3. Compute connected components: these are local patches.
4. Among unused candidate edges that cross components, add bridge edges only
   when they improve the same spectral-locality score.
5. Rebuild K from the patched graph and iterate.

The bridge step is intentionally conservative: it can add at most one bridge per
component merge, so it connects patches without making the graph dense.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import csv
import numpy as np

from rapc_hypergraph_coarse_grain_toy import embedded
from rapc_iterated_flow_toy import Edge, graph_stats, rebuild_pair_modular_seed
from rapc_mdl_budget_selection_toy import candidate_edges
from rapc_spectral_locality_scan_toy import (
    classify_phase,
    random_hypergraph_seed,
    select_spectral_graph,
    spectral_score,
)


@dataclass(frozen=True)
class PatchParams:
    n: int = 6
    seeds_per_lambda: int = 20
    lambdas: tuple[float, ...] = (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20)
    steps: int = 6
    disconnect_cost: float = 0.25
    nu_gap: float = 0.18
    mu_degree: float = 0.035
    bridge_lambda_factor: float = 0.75
    output_csv: str = "rapc_patch_gluing_scan_results.csv"


def component_labels(edges: list[Edge], n: int) -> list[int]:
    adjacency = {idx: set() for idx in range(n)}
    for edge in edges:
        adjacency[edge.i].add(edge.j)
        adjacency[edge.j].add(edge.i)

    labels = [-1] * n
    label = 0
    for node in range(n):
        if labels[node] != -1:
            continue
        stack = [node]
        labels[node] = label
        while stack:
            cur = stack.pop()
            for nxt in adjacency[cur]:
                if labels[nxt] == -1:
                    labels[nxt] = label
                    stack.append(nxt)
        label += 1
    return labels


def edge_key(edge: Edge) -> tuple[int, int, tuple[str, str]]:
    return (min(edge.i, edge.j), max(edge.i, edge.j), edge.axis)


def glue_patches(
    selected_edges: list[Edge],
    candidates: list[Edge],
    n: int,
    lambda_edges: float,
    params: PatchParams,
) -> list[Edge]:
    current = list(selected_edges)
    used = {edge_key(edge) for edge in current}
    bridge_lambda = lambda_edges * params.bridge_lambda_factor

    while True:
        labels = component_labels(current, n)
        if len(set(labels)) <= 1:
            return current

        base_score = spectral_score(
            current,
            n,
            bridge_lambda,
            params.disconnect_cost,
            params.nu_gap,
            params.mu_degree,
        ).score

        best_edge = None
        best_score = base_score
        for edge in candidates:
            if edge_key(edge) in used:
                continue
            if labels[edge.i] == labels[edge.j]:
                continue
            trial = current + [edge]
            trial_score = spectral_score(
                trial,
                n,
                bridge_lambda,
                params.disconnect_cost,
                params.nu_gap,
                params.mu_degree,
            ).score
            if trial_score > best_score + 1.0e-12:
                best_score = trial_score
                best_edge = edge

        if best_edge is None:
            return current
        current.append(best_edge)
        used.add(edge_key(best_edge))


def run_one_flow(k_seed: np.ndarray, params: PatchParams, lambda_edges: float) -> dict[str, object]:
    current = k_seed
    pre_phases = []
    post_edge_counts = []
    post_components = []
    post_largest = []
    added_bridges_total = 0
    final_edges: list[Edge] = []

    for step in range(params.steps):
        candidates = candidate_edges(current, params.n)
        selection = select_spectral_graph(
            candidates,
            params.n,
            lambda_edges,
            params.disconnect_cost,
            params.nu_gap,
            params.mu_degree,
        )
        pre_stats = graph_stats(selection.edges, params.n, step)
        pre_phases.append(classify_phase(pre_stats.edge_count, pre_stats.components, params.n))

        glued = glue_patches(selection.edges, candidates, params.n, lambda_edges, params)
        added_bridges_total += max(0, len(glued) - len(selection.edges))
        post_stats = graph_stats(glued, params.n, step)
        post_edge_counts.append(post_stats.edge_count)
        post_components.append(post_stats.components)
        post_largest.append(post_stats.largest_component)
        final_edges = glued
        current = rebuild_pair_modular_seed(glued, params.n, damping=0.85)

    final_stats = graph_stats(final_edges, params.n, params.steps - 1)
    final_selection = spectral_score(
        final_edges,
        params.n,
        lambda_edges,
        params.disconnect_cost,
        params.nu_gap,
        params.mu_degree,
    )
    return {
        "pre_final_phase": pre_phases[-1],
        "post_phase": classify_phase(final_stats.edge_count, final_stats.components, params.n),
        "final_edges": final_stats.edge_count,
        "final_components": final_stats.components,
        "final_largest": final_stats.largest_component,
        "final_diameter": "" if final_stats.diameter is None else final_stats.diameter,
        "final_info": final_selection.information,
        "final_score": final_selection.score,
        "final_gap": final_selection.algebraic_connectivity,
        "bridges_added_total": added_bridges_total,
        "stable_edge_count": len(set(post_edge_counts[-3:])) == 1,
        "stable_topology": len(set(post_components[-3:])) == 1 and len(set(post_largest[-3:])) == 1,
    }


def run_scan(params: PatchParams) -> list[dict[str, object]]:
    rows = []
    master_rng = np.random.default_rng(20260424)
    seed_values = master_rng.integers(0, 2**31 - 1, size=params.seeds_per_lambda)

    for lam in params.lambdas:
        for seed_index, seed_value in enumerate(seed_values):
            rng = np.random.default_rng(int(seed_value))
            k_seed = random_hypergraph_seed(params.n, rng)
            metrics = run_one_flow(k_seed, params, lam)
            rows.append({"lambda": lam, "seed_index": seed_index, **metrics})
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
        counts = {phase: sum(1 for row in subset if row["post_phase"] == phase) for phase in phases}
        pre_geo = sum(1 for row in subset if row["pre_final_phase"] == "sparse_geometric")
        stable_geo = sum(
            1
            for row in subset
            if row["post_phase"] == "sparse_geometric" and row["stable_edge_count"] and row["stable_topology"]
        )
        mean_edges = sum(float(row["final_edges"]) for row in subset) / total
        mean_bridges = sum(float(row["bridges_added_total"]) for row in subset) / total
        mean_gap = sum(float(row["final_gap"]) for row in subset) / total
        lines.append(
            f"lambda={lam:.2f} "
            f"pre_geo={pre_geo:02d}/{total} "
            f"empty={counts['empty']:02d}/{total} "
            f"frag={counts['fragmented_sparse']:02d}/{total} "
            f"geo={counts['sparse_geometric']:02d}/{total} "
            f"dense={counts['dense_nonlocal']:02d}/{total} "
            f"stable_geo={stable_geo:02d}/{total} "
            f"mean_edges={mean_edges:.2f} "
            f"mean_bridges={mean_bridges:.2f} "
            f"mean_gap={mean_gap:.3f}"
        )
    return "\n".join(lines)


def main() -> None:
    params = PatchParams()
    print("RAPC patch-gluing phase scan toy model")
    print("======================================")
    print(
        f"n={params.n}, seeds_per_lambda={params.seeds_per_lambda}, steps={params.steps}, "
        f"disconnect_cost={params.disconnect_cost}, nu_gap={params.nu_gap}, "
        f"mu_degree={params.mu_degree}, bridge_lambda_factor={params.bridge_lambda_factor}"
    )
    print()
    rows = run_scan(params)
    write_csv(rows, params.output_csv)
    print(summarize(rows, params.lambdas))
    print()
    print(f"wrote {params.output_csv}")


if __name__ == "__main__":
    main()
