"""RAPC residual-aware patch-gluing scan toy model.

Twelfth falsification gate:

    pair geometry flow + residual hypergraph memory
    -> patch bridges
    -> connected sparse geometry-

The first patch-gluing attempt added no bridges. Diagnosis: after each step we
rebuilt K only from surviving pair edges, discarding the microscopic hypergraph
residual that could later mediate bridges.

This script keeps a residual memory:

    K_current = pair_effective_flow + residual_strength * K_micro

Candidate edges are extracted from K_current, while the next pair graph is still
rebuilt sparsely. This tests whether weak hypergraph memory can glue fragments
without causing full densification.
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
from rapc_patch_gluing_scan_toy import glue_patches


@dataclass(frozen=True)
class ResidualPatchParams:
    n: int = 6
    seeds_per_lambda: int = 20
    lambdas: tuple[float, ...] = (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16, 0.20)
    steps: int = 6
    disconnect_cost: float = 0.25
    nu_gap: float = 0.18
    mu_degree: float = 0.035
    bridge_lambda_factor: float = 0.75
    residual_strength: float = 0.35
    residual_decay: float = 0.82
    output_csv: str = "rapc_residual_patch_gluing_scan_results.csv"


def run_one_flow(k_micro: np.ndarray, params: ResidualPatchParams, lambda_edges: float) -> dict[str, object]:
    pair_seed = np.zeros_like(k_micro)
    residual_weight = params.residual_strength
    final_edges: list[Edge] = []
    pre_phases = []
    post_edge_counts = []
    post_components = []
    post_largest = []
    added_bridges_total = 0

    for step in range(params.steps):
        k_current = pair_seed + residual_weight * k_micro
        candidates = candidate_edges(k_current, params.n)
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

        # Reuse the patch gluer, but pass a tiny adapter object with the same
        # fields it expects.
        adapter = type(
            "PatchAdapter",
            (),
            {
                "n": params.n,
                "disconnect_cost": params.disconnect_cost,
                "nu_gap": params.nu_gap,
                "mu_degree": params.mu_degree,
                "bridge_lambda_factor": params.bridge_lambda_factor,
            },
        )()
        glued = glue_patches(selection.edges, candidates, params.n, lambda_edges, adapter)
        added_bridges_total += max(0, len(glued) - len(selection.edges))
        post_stats = graph_stats(glued, params.n, step)
        post_edge_counts.append(post_stats.edge_count)
        post_components.append(post_stats.components)
        post_largest.append(post_stats.largest_component)
        final_edges = glued

        pair_seed = rebuild_pair_modular_seed(glued, params.n, damping=0.85)
        residual_weight *= params.residual_decay

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


def run_scan(params: ResidualPatchParams) -> list[dict[str, object]]:
    rows = []
    master_rng = np.random.default_rng(20260424)
    seed_values = master_rng.integers(0, 2**31 - 1, size=params.seeds_per_lambda)

    for lam in params.lambdas:
        for seed_index, seed_value in enumerate(seed_values):
            rng = np.random.default_rng(int(seed_value))
            k_micro = random_hypergraph_seed(params.n, rng)
            metrics = run_one_flow(k_micro, params, lam)
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
    params = ResidualPatchParams()
    print("RAPC residual-aware patch-gluing scan toy model")
    print("===============================================")
    print(
        f"n={params.n}, seeds_per_lambda={params.seeds_per_lambda}, steps={params.steps}, "
        f"residual_strength={params.residual_strength}, residual_decay={params.residual_decay}"
    )
    print()
    rows = run_scan(params)
    write_csv(rows, params.output_csv)
    print(summarize(rows, params.lambdas))
    print()
    print(f"wrote {params.output_csv}")


if __name__ == "__main__":
    main()
