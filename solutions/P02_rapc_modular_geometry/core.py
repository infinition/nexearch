"""RAPC Modular Geometry - solution entry point.

This file keeps the Nexearch solution runnable from its root directory.
The detailed toy experiments live in `source/`.
"""

from __future__ import annotations

from pathlib import Path
import csv
import sys


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))


def load_csv(name: str) -> list[dict[str, str]]:
    path = ROOT / "results" / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def phase_field(row: dict[str, str]) -> str:
    return row.get("phase") or row.get("post_phase") or row.get("pre_final_phase") or ""


def summarize_phase_csv(name: str) -> str:
    rows = load_csv(name)
    if not rows:
        return f"{name}: missing"

    by_lambda: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_lambda.setdefault(row["lambda"], []).append(row)

    lines = [name]
    for lam in sorted(by_lambda, key=lambda value: float(value)):
        subset = by_lambda[lam]
        geo = sum(1 for row in subset if phase_field(row) == "sparse_geometric")
        dense = sum(1 for row in subset if phase_field(row) == "dense_nonlocal")
        empty = sum(1 for row in subset if phase_field(row) == "empty")
        frag = sum(1 for row in subset if phase_field(row) == "fragmented_sparse")
        lines.append(
            f"  lambda={float(lam):.2f}: geo={geo}/{len(subset)}, "
            f"frag={frag}, dense={dense}, empty={empty}"
        )
    return "\n".join(lines)


def run_bmv_gate() -> None:
    from rapc_bmv_toy import BMVGeometry, run_case

    result = run_case(BMVGeometry())
    print("BMV gate")
    print(f"  quantum_concurrence: {result['quantum_concurrence']:.12g}")
    print(f"  quantum_negativity : {result['quantum_negativity']:.12g}")
    print(f"  mean_field_neg     : {result['mean_field_negativity']:.12g}")
    print(f"  classical_locc_neg : {result['classical_locc_negativity']:.12g}")


def main() -> None:
    print("RAPC Modular Geometry")
    print("=====================")
    run_bmv_gate()
    print()
    for csv_name in [
        "rapc_phase_scan_results.csv",
        "rapc_spectral_locality_scan_results.csv",
        "rapc_patch_gluing_scan_results.csv",
        "rapc_residual_patch_gluing_scan_results.csv",
    ]:
        print(summarize_phase_csv(csv_name))
        print()


if __name__ == "__main__":
    main()
