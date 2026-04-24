"""Finite modular RAPC toy model.

Goal
----
Replace the imported Newtonian phase of `rapc_bmv_toy.py` by a phase generated
from modular data.

Given a faithful two-qubit state rho_AB, define the modular Hamiltonian:

    K_AB = -log(rho_AB)

Then remove the purely local modular pieces:

    K_int = K_AB - K_A tensor I - I tensor K_B

where K_A = -log(rho_A) and K_B = -log(rho_B). The remaining operator is the
finite-dimensional analogue of a non-factorizing modular/correlation term.

The falsification gate:

    If K_int = 0, modular evolution cannot entangle |++>.
    If K_int contains a coherent bilocal term, modular evolution can entangle.

This still uses Type I matrices, so it is only a toy model. But it no longer
imports a background distance r_ij or Newtonian phase Gm^2 t / hbar r.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = {"I": I2, "X": X, "Y": Y, "Z": Z}


def kron(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.kron(a, b)


def exp_hermitian(a: np.ndarray) -> np.ndarray:
    evals, vecs = np.linalg.eigh(a)
    return (vecs * np.exp(evals)) @ vecs.conj().T


def log_density(rho: np.ndarray) -> np.ndarray:
    evals, vecs = np.linalg.eigh(rho)
    if np.any(evals <= 1.0e-14):
        raise ValueError("rho must be faithful/full-rank for a finite modular log")
    return (vecs * np.log(evals)) @ vecs.conj().T


def thermal_state(k_modular: np.ndarray) -> np.ndarray:
    unnormalized = exp_hermitian(-k_modular)
    return unnormalized / np.trace(unnormalized)


def partial_trace_a(rho: np.ndarray) -> np.ndarray:
    return np.trace(rho.reshape(2, 2, 2, 2), axis1=0, axis2=2)


def partial_trace_b(rho: np.ndarray) -> np.ndarray:
    return np.trace(rho.reshape(2, 2, 2, 2), axis1=1, axis2=3)


def modular_hamiltonian(rho: np.ndarray) -> np.ndarray:
    return -log_density(rho)


def traceless(a: np.ndarray) -> np.ndarray:
    return a - np.trace(a) * np.eye(a.shape[0], dtype=complex) / a.shape[0]


def nonlocal_pauli_projection(a: np.ndarray) -> np.ndarray:
    """Keep only Pauli terms with no identity factor.

    The subtraction K_AB - K_A - K_B is physically motivated, but in a finite
    Hilbert-Schmidt decomposition it can still leave local-looking terms. For
    the BMV gate we want the strictly non-factorizing part.
    """

    out = np.zeros_like(a, dtype=complex)
    for left_name, left in PAULIS.items():
        for right_name, right in PAULIS.items():
            if left_name == "I" or right_name == "I":
                continue
            basis = kron(left, right)
            coeff = np.trace(a @ basis) / 4.0
            out += coeff * basis
    return (out + out.conj().T) / 2.0


def modular_interaction(rho_ab: np.ndarray) -> np.ndarray:
    rho_a = partial_trace_b(rho_ab)
    rho_b = partial_trace_a(rho_ab)
    k_ab = modular_hamiltonian(rho_ab)
    k_a = modular_hamiltonian(rho_a)
    k_b = modular_hamiltonian(rho_b)
    k_int = k_ab - kron(k_a, I2) - kron(I2, k_b)
    return nonlocal_pauli_projection(traceless((k_int + k_int.conj().T) / 2.0))


def pauli_coefficients(a: np.ndarray) -> dict[str, float]:
    coeffs = {}
    for left_name, left in PAULIS.items():
        for right_name, right in PAULIS.items():
            name = left_name + right_name
            basis = kron(left, right)
            coeff = np.trace(a @ basis) / 4.0
            if abs(coeff) > 1.0e-10:
                coeffs[name] = float(np.real_if_close(coeff))
    return coeffs


def ket_plus_plus() -> np.ndarray:
    return np.ones(4, dtype=complex) / 2.0


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def unitary_from_hamiltonian(h: np.ndarray, modular_time: float) -> np.ndarray:
    evals, vecs = np.linalg.eigh(h)
    return (vecs * np.exp(-1j * modular_time * evals)) @ vecs.conj().T


def evolve_plus_plus(h: np.ndarray, modular_time: float) -> np.ndarray:
    psi = unitary_from_hamiltonian(h, modular_time) @ ket_plus_plus()
    return density(psi)


def partial_transpose_b(rho: np.ndarray) -> np.ndarray:
    return rho.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)


def negativity(rho: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(partial_transpose_b(rho))
    return float(np.sum(np.abs(evals[evals < 0.0])))


def concurrence_for_pure_state_rho(rho: np.ndarray) -> float:
    evals, vecs = np.linalg.eigh(rho)
    psi = vecs[:, int(np.argmax(evals))]
    a, b, c, d = psi
    return float(2.0 * abs(a * d - b * c))


def mutual_information(rho_ab: np.ndarray) -> float:
    def entropy(rho: np.ndarray) -> float:
        evals = np.linalg.eigvalsh(rho)
        evals = evals[evals > 1.0e-14]
        return float(-np.sum(evals * np.log(evals)))

    rho_a = partial_trace_b(rho_ab)
    rho_b = partial_trace_a(rho_ab)
    return entropy(rho_a) + entropy(rho_b) - entropy(rho_ab)


@dataclass(frozen=True)
class ModularCase:
    name: str
    rho: np.ndarray
    modular_time: float = 1.0


def product_case() -> ModularCase:
    k = 0.4 * kron(Z, I2) - 0.2 * kron(I2, Z)
    return ModularCase("product_local_modular_state", thermal_state(k))


def diagonal_correlated_case() -> ModularCase:
    k = 0.2 * kron(Z, I2) - 0.1 * kron(I2, Z) + 0.35 * kron(Z, Z)
    return ModularCase("diagonal_bilocal_modular_state", thermal_state(k))


def noncommuting_correlated_case() -> ModularCase:
    k = 0.2 * kron(Z, I2) - 0.1 * kron(I2, Z) + 0.35 * kron(X, X)
    return ModularCase("noncommuting_bilocal_modular_state", thermal_state(k))


def product_state(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> np.ndarray:
    def qubit(theta: float, phi: float) -> np.ndarray:
        return np.array(
            [np.cos(theta / 2.0), np.exp(1j * phi) * np.sin(theta / 2.0)],
            dtype=complex,
        )

    return np.kron(qubit(theta_a, phi_a), qubit(theta_b, phi_b))


def entangling_power_sample(h: np.ndarray, modular_time: float) -> float:
    """Small deterministic product-state sample for basis-independent sanity."""

    angles = [
        (np.pi / 2.0, 0.0),
        (np.pi / 2.0, np.pi / 2.0),
        (np.pi / 3.0, 0.0),
        (2.0 * np.pi / 3.0, np.pi / 3.0),
        (np.pi / 4.0, np.pi / 5.0),
    ]
    u = unitary_from_hamiltonian(h, modular_time)
    best = 0.0
    for theta_a, phi_a in angles:
        for theta_b, phi_b in angles:
            psi = u @ product_state(theta_a, phi_a, theta_b, phi_b)
            best = max(best, concurrence_for_pure_state_rho(density(psi)))
    return best


def analyze_case(case: ModularCase) -> dict[str, object]:
    k_int = modular_interaction(case.rho)
    rho_out = evolve_plus_plus(k_int, case.modular_time)
    coeffs = pauli_coefficients(k_int)
    return {
        "case": case.name,
        "mutual_information": mutual_information(case.rho),
        "k_int_norm": float(np.linalg.norm(k_int)),
        "k_int_coeffs": coeffs,
        "output_concurrence": concurrence_for_pure_state_rho(rho_out),
        "output_negativity": negativity(rho_out),
        "sampled_entangling_power": entangling_power_sample(k_int, case.modular_time),
    }


def print_result(result: dict[str, object]) -> None:
    print(result["case"])
    print("-" * len(str(result["case"])))
    print(f"mutual_information : {result['mutual_information']:.12g}")
    print(f"k_int_norm        : {result['k_int_norm']:.12g}")
    print(f"output_concurrence : {result['output_concurrence']:.12g}")
    print(f"output_negativity  : {result['output_negativity']:.12g}")
    print(f"sampled_power      : {result['sampled_entangling_power']:.12g}")
    print("k_int_coeffs:")
    coeffs = result["k_int_coeffs"]
    if coeffs:
        for name, value in sorted(coeffs.items()):
            print(f"  {name}: {value:.12g}")
    else:
        print("  <none>")
    print()


def main() -> None:
    print("RAPC modular-phase toy model")
    print("============================")
    print()
    for case in [product_case(), diagonal_correlated_case(), noncommuting_correlated_case()]:
        print_result(analyze_case(case))


if __name__ == "__main__":
    main()
