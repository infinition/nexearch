"""RAPC subalgebra-selection toy model.

Third falsification gate:

    global modular data -> selected subalgebras -> modular interaction -> BMV witness

The previous model chose the two qubits A/B by hand. Here we start with a
finite global algebra M_2^(tensor n), compute the modular Hamiltonian K=-log(rho),
scan its Pauli expansion, and select the pair of elementary subalgebras with the
largest strictly bilocal modular coupling.

This still imports a finite tensor factorization into elementary qubits. The
improvement is narrower but real: the BMV pair and its entangling axis are not
chosen by hand; they are selected from global modular data.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
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


def embedded_two_body(n: int, i: int, a: str, j: int, b: str) -> np.ndarray:
    chars = ["I"] * n
    chars[i] = a
    chars[j] = b
    return pauli_string("".join(chars))


def embedded_one_body(n: int, i: int, a: str) -> np.ndarray:
    chars = ["I"] * n
    chars[i] = a
    return pauli_string("".join(chars))


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


def unitary_from_hamiltonian(h: np.ndarray, modular_time: float) -> np.ndarray:
    evals, vecs = np.linalg.eigh(h)
    return (vecs * np.exp(-1j * modular_time * evals)) @ vecs.conj().T


def pauli_coefficient(op: np.ndarray, label: str) -> float:
    dim = op.shape[0]
    coeff = np.trace(op @ pauli_string(label)) / dim
    return float(np.real_if_close(coeff))


def all_pauli_labels(n: int) -> list[str]:
    return ["".join(chars) for chars in product("IXYZ", repeat=n)]


@dataclass(frozen=True)
class SelectedEdge:
    pair: tuple[int, int] | None
    strength: float
    axis: tuple[str, str] | None
    axis_coeff: float


def select_bilocal_edge(k_modular: np.ndarray, n: int, threshold: float = 1.0e-10) -> SelectedEdge:
    best_pair = None
    best_strength = 0.0
    best_axis = None
    best_axis_coeff = 0.0

    for i, j in combinations(range(n), 2):
        strength = 0.0
        local_axis = None
        local_coeff = 0.0
        for a in NON_ID:
            for b in NON_ID:
                label = ["I"] * n
                label[i] = a
                label[j] = b
                coeff = pauli_coefficient(k_modular, "".join(label))
                strength += coeff * coeff
                if abs(coeff) > abs(local_coeff):
                    local_axis = (a, b)
                    local_coeff = coeff
        if strength > best_strength:
            best_pair = (i, j)
            best_strength = strength
            best_axis = local_axis
            best_axis_coeff = local_coeff

    if best_strength <= threshold:
        return SelectedEdge(None, 0.0, None, 0.0)
    return SelectedEdge(best_pair, best_strength, best_axis, best_axis_coeff)


def selected_pair_hamiltonian(n: int, edge: SelectedEdge) -> np.ndarray:
    if edge.pair is None or edge.axis is None:
        return np.zeros((2**n, 2**n), dtype=complex)
    i, j = edge.pair
    a, b = edge.axis
    return edge.axis_coeff * embedded_two_body(n, i, a, j, b)


def eigenstate(pauli: str, sign: int = 1) -> np.ndarray:
    op = PAULIS[pauli]
    evals, vecs = np.linalg.eigh(op)
    idx = int(np.argmin(np.abs(evals - sign)))
    return vecs[:, idx]


def anticommuting_axis(axis: str) -> str:
    if axis == "Z":
        return "X"
    if axis == "X":
        return "Z"
    return "Z"


def initial_state_for_edge(n: int, edge: SelectedEdge) -> np.ndarray:
    states = [eigenstate("Z", +1) for _ in range(n)]
    if edge.pair is not None and edge.axis is not None:
        i, j = edge.pair
        a, b = edge.axis
        states[i] = eigenstate(anticommuting_axis(a), +1)
        states[j] = eigenstate(anticommuting_axis(b), +1)
    return kron_all(states)


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def reduce_to_pair(rho: np.ndarray, n: int, pair: tuple[int, int]) -> np.ndarray:
    keep = list(pair)
    trace_out = [idx for idx in range(n) if idx not in keep]
    tensor = rho.reshape([2] * (2 * n))
    for q in sorted(trace_out, reverse=True):
        tensor = np.trace(tensor, axis1=q, axis2=q + tensor.ndim // 2)
    # Move kept ket/bra axes into canonical pair order.
    return tensor.reshape(4, 4)


def partial_transpose_b_two_qubit(rho: np.ndarray) -> np.ndarray:
    return rho.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)


def negativity_two_qubit(rho: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(partial_transpose_b_two_qubit(rho))
    return float(np.sum(np.abs(evals[evals < 0.0])))


def concurrence_for_pure_state(psi_pair: np.ndarray) -> float:
    a, b, c, d = psi_pair
    return float(2.0 * abs(a * d - b * c))


def bmv_witness_from_selected_edge(k_modular: np.ndarray, n: int, modular_time: float) -> dict[str, object]:
    edge = select_bilocal_edge(k_modular, n)
    if edge.pair is None:
        return {
            "selected_pair": None,
            "selected_axis": None,
            "edge_strength": 0.0,
            "axis_coeff": 0.0,
            "pair_negativity": 0.0,
            "expected_concurrence": 0.0,
        }

    h_pair = selected_pair_hamiltonian(n, edge)
    psi0 = initial_state_for_edge(n, edge)
    psi = unitary_from_hamiltonian(h_pair, modular_time) @ psi0
    rho_pair = reduce_to_pair(density(psi), n, edge.pair)
    expected = abs(np.sin(2.0 * edge.axis_coeff * modular_time))
    return {
        "selected_pair": edge.pair,
        "selected_axis": edge.axis,
        "edge_strength": edge.strength,
        "axis_coeff": edge.axis_coeff,
        "pair_negativity": negativity_two_qubit(rho_pair),
        "expected_concurrence": float(expected),
    }


@dataclass(frozen=True)
class GlobalCase:
    name: str
    k_seed: np.ndarray
    modular_time: float = 1.0

    def rho(self) -> np.ndarray:
        return thermal_state(self.k_seed)


def local_only_case(n: int) -> GlobalCase:
    k = 0.2 * embedded_one_body(n, 0, "Z") - 0.15 * embedded_one_body(n, 1, "X")
    k += 0.1 * embedded_one_body(n, 2, "Z")
    return GlobalCase("local_only_global_state", k)


def hidden_bmv_pair_case(n: int) -> GlobalCase:
    k = 0.1 * embedded_one_body(n, 0, "Z") - 0.05 * embedded_one_body(n, 2, "Z")
    k += 0.35 * embedded_two_body(n, 0, "Z", 1, "Z")
    return GlobalCase("hidden_bmv_pair_global_state", k)


def competing_edges_case(n: int) -> GlobalCase:
    k = 0.2 * embedded_two_body(n, 0, "Z", 1, "Z")
    k += 0.45 * embedded_two_body(n, 1, "X", 2, "X")
    k += 0.05 * embedded_one_body(n, 0, "X")
    return GlobalCase("competing_edges_global_state", k)


def three_body_only_case(n: int) -> GlobalCase:
    label = ["I"] * n
    label[0] = "Z"
    label[1] = "Z"
    label[2] = "Z"
    k = 0.5 * pauli_string("".join(label))
    return GlobalCase("three_body_only_global_state", k)


def analyze_case(case: GlobalCase, n: int) -> dict[str, object]:
    rho = case.rho()
    k_modular = modular_hamiltonian(rho)
    witness = bmv_witness_from_selected_edge(k_modular, n, case.modular_time)
    return {
        "case": case.name,
        **witness,
    }


def print_result(result: dict[str, object]) -> None:
    print(result["case"])
    print("-" * len(str(result["case"])))
    print(f"selected_pair        : {result['selected_pair']}")
    print(f"selected_axis        : {result['selected_axis']}")
    print(f"edge_strength        : {result['edge_strength']:.12g}")
    print(f"axis_coeff           : {result['axis_coeff']:.12g}")
    print(f"pair_negativity      : {result['pair_negativity']:.12g}")
    print(f"expected_concurrence : {result['expected_concurrence']:.12g}")
    print()


def main() -> None:
    n = 3
    print("RAPC subalgebra-selection toy model")
    print("===================================")
    print()
    cases = [
        local_only_case(n),
        hidden_bmv_pair_case(n),
        competing_edges_case(n),
        three_body_only_case(n),
    ]
    for case in cases:
        print_result(analyze_case(case, n))


if __name__ == "__main__":
    main()
