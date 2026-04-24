"""RAPC hypergraph coarse-graining toy model.

Fourth falsification gate:

    higher-order modular correlations
    -> observer/environment coarse-graining
    -> effective bilocal modular edge
    -> BMV witness

The previous model showed a productive failure: a purely pairwise selector
cannot see a modular Hamiltonian containing only a three-body term, e.g.

    K = J Z0 Z1 Z2

This script tests whether coarse-graining can turn such a hyperedge into an
effective pairwise edge. The key lesson is sharp:

    an unbiased hidden node does not generate a pair edge;
    a biased/reference hidden node does.

For diagonal Pauli examples this reproduces the exact classical decimation
formula:

    K_eff(z0,z1) = -log sum_z2 exp[-K(z0,z1,z2)]

but the implementation uses density matrices and partial traces, so the same
shape can later be extended to noncommuting finite examples.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import numpy as np


I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = {"I": I2, "X": X, "Y": Y, "Z": Z}
NON_ID = ["X", "Y", "Z"]


def kron_all(ops: list[np.ndarray]) -> np.ndarray:
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out


def pauli_string(label: str) -> np.ndarray:
    return kron_all([PAULIS[ch] for ch in label])


def embedded(n: int, terms: dict[int, str]) -> np.ndarray:
    label = ["I"] * n
    for idx, axis in terms.items():
        label[idx] = axis
    return pauli_string("".join(label))


def exp_hermitian(a: np.ndarray) -> np.ndarray:
    evals, vecs = np.linalg.eigh(a)
    return (vecs * np.exp(evals)) @ vecs.conj().T


def log_density(rho: np.ndarray) -> np.ndarray:
    evals, vecs = np.linalg.eigh(rho)
    if np.any(evals <= 1.0e-14):
        raise ValueError("rho must be faithful/full-rank")
    return (vecs * np.log(evals)) @ vecs.conj().T


def thermal_state(k_modular: np.ndarray) -> np.ndarray:
    unnormalized = exp_hermitian(-k_modular)
    return unnormalized / np.trace(unnormalized)


def modular_hamiltonian(rho: np.ndarray) -> np.ndarray:
    return -log_density(rho)


def partial_trace_keep(rho: np.ndarray, n: int, keep: tuple[int, ...]) -> np.ndarray:
    """Trace all factors except `keep`, preserving keep order."""

    keep = tuple(keep)
    trace = tuple(i for i in range(n) if i not in keep)
    letters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if 2 * n > len(letters):
        raise ValueError("too many factors for simple einsum labels")

    ket_labels = letters[:n]
    bra_labels = letters[n : 2 * n]
    for idx in trace:
        bra_labels[idx] = ket_labels[idx]

    out_labels = [ket_labels[idx] for idx in keep] + [bra_labels[idx] for idx in keep]
    expr = "".join(ket_labels + bra_labels) + "->" + "".join(out_labels)
    reduced = np.einsum(expr, rho.reshape([2] * (2 * n)))
    return reduced.reshape(2 ** len(keep), 2 ** len(keep))


def pauli_coefficient(op: np.ndarray, label: str) -> float:
    dim = op.shape[0]
    coeff = np.trace(op @ pauli_string(label)) / dim
    return float(np.real_if_close(coeff))


@dataclass(frozen=True)
class PairEdge:
    pair: tuple[int, int] | None
    axis: tuple[str, str] | None
    coeff: float
    strength: float


def select_pair_edge(k_pair: np.ndarray) -> PairEdge:
    best_axis = None
    best_coeff = 0.0
    best_strength = 0.0
    for a in NON_ID:
        for b in NON_ID:
            coeff = pauli_coefficient(k_pair, a + b)
            strength = coeff * coeff
            if strength > best_strength:
                best_axis = (a, b)
                best_coeff = coeff
                best_strength = strength
    if best_strength < 1.0e-12:
        return PairEdge(None, None, 0.0, 0.0)
    return PairEdge((0, 1), best_axis, best_coeff, best_strength)


def unitary_from_hamiltonian(h: np.ndarray, modular_time: float) -> np.ndarray:
    evals, vecs = np.linalg.eigh(h)
    return (vecs * np.exp(-1j * modular_time * evals)) @ vecs.conj().T


def eigenstate(pauli: str, sign: int = 1) -> np.ndarray:
    evals, vecs = np.linalg.eigh(PAULIS[pauli])
    idx = int(np.argmin(np.abs(evals - sign)))
    return vecs[:, idx]


def anticommuting_axis(axis: str) -> str:
    if axis == "Z":
        return "X"
    if axis == "X":
        return "Z"
    return "Z"


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def partial_transpose_b(rho: np.ndarray) -> np.ndarray:
    return rho.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)


def negativity(rho: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(partial_transpose_b(rho))
    return float(np.sum(np.abs(evals[evals < 0.0])))


def bmv_witness_from_pair_edge(edge: PairEdge, modular_time: float) -> dict[str, float]:
    if edge.axis is None:
        return {"pair_negativity": 0.0, "expected_concurrence": 0.0}

    a, b = edge.axis
    h = edge.coeff * pauli_string(a + b)
    psi0 = np.kron(eigenstate(anticommuting_axis(a), +1), eigenstate(anticommuting_axis(b), +1))
    psi = unitary_from_hamiltonian(h, modular_time) @ psi0
    expected_concurrence = abs(np.sin(2.0 * edge.coeff * modular_time))
    return {
        "pair_negativity": negativity(density(psi)),
        "expected_concurrence": float(expected_concurrence),
    }


def pairwise_scan_before_coarse_grain(k_global: np.ndarray, n: int) -> float:
    best = 0.0
    for i, j in combinations(range(n), 2):
        for a in NON_ID:
            for b in NON_ID:
                coeff = pauli_coefficient(k_global, "".join(
                    a if idx == i else b if idx == j else "I" for idx in range(n)
                ))
                best = max(best, abs(coeff))
    return best


@dataclass(frozen=True)
class HyperCase:
    name: str
    k_global: np.ndarray
    keep: tuple[int, int] = (0, 1)
    modular_time: float = 1.0
    analytic_coeff: float | None = None


def unbiased_hidden_node_case(j: float = 0.5) -> HyperCase:
    n = 3
    k = j * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    return HyperCase("unbiased_hidden_node", k, analytic_coeff=0.0)


def biased_hidden_node_case(j: float = 0.5, h: float = 0.4) -> HyperCase:
    n = 3
    k = j * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += h * embedded(n, {2: "Z"})
    coeff = -0.5 * np.log(np.cosh(h + j) / np.cosh(h - j))
    return HyperCase("biased_hidden_node", k, analytic_coeff=float(coeff))


def transverse_reference_case(j: float = 0.5, h: float = 0.4) -> HyperCase:
    n = 3
    k = j * embedded(n, {0: "Z", 1: "Z", 2: "X"})
    k += h * embedded(n, {2: "X"})
    coeff = -0.5 * np.log(np.cosh(h + j) / np.cosh(h - j))
    return HyperCase("transverse_reference_node", k, analytic_coeff=float(coeff))


def irrelevant_bias_case(j: float = 0.5, h: float = 0.4) -> HyperCase:
    n = 3
    k = j * embedded(n, {0: "Z", 1: "Z", 2: "Z"})
    k += h * embedded(n, {2: "X"})
    return HyperCase("irrelevant_noncommuting_bias", k, analytic_coeff=None)


def analyze_case(case: HyperCase) -> dict[str, object]:
    n = 3
    rho_global = thermal_state(case.k_global)
    k_global = modular_hamiltonian(rho_global)
    pre_best_pair_coeff = pairwise_scan_before_coarse_grain(k_global, n)

    rho_pair = partial_trace_keep(rho_global, n, case.keep)
    k_pair = modular_hamiltonian(rho_pair)
    edge = select_pair_edge(k_pair)
    witness = bmv_witness_from_pair_edge(edge, case.modular_time)

    return {
        "case": case.name,
        "pre_best_pair_coeff": pre_best_pair_coeff,
        "selected_axis": edge.axis,
        "effective_coeff": edge.coeff,
        "edge_strength": edge.strength,
        "analytic_coeff": case.analytic_coeff,
        **witness,
    }


def print_result(result: dict[str, object]) -> None:
    print(result["case"])
    print("-" * len(str(result["case"])))
    print(f"pre_best_pair_coeff : {result['pre_best_pair_coeff']:.12g}")
    print(f"selected_axis       : {result['selected_axis']}")
    print(f"effective_coeff     : {result['effective_coeff']:.12g}")
    if result["analytic_coeff"] is None:
        print("analytic_coeff      : <none>")
    else:
        print(f"analytic_coeff      : {result['analytic_coeff']:.12g}")
    print(f"edge_strength       : {result['edge_strength']:.12g}")
    print(f"pair_negativity     : {result['pair_negativity']:.12g}")
    print(f"expected_concurrence: {result['expected_concurrence']:.12g}")
    print()


def main() -> None:
    print("RAPC hypergraph coarse-graining toy model")
    print("=========================================")
    print()
    cases = [
        unbiased_hidden_node_case(),
        biased_hidden_node_case(),
        transverse_reference_case(),
        irrelevant_bias_case(),
    ]
    for case in cases:
        print_result(analyze_case(case))


if __name__ == "__main__":
    main()
