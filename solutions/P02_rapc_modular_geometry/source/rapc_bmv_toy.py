"""Minimal RAPC/BMV toy model.

This is not a full Tomita-Takesaki or Type III construction. It is the first
falsification gate for the RAPC idea: can the effective gravitational channel
create entanglement between two initially separable path qubits-

We compare three channels:

1. quantum_bilocal_phase:
   A nonlocal phase U = exp(-i sum_ij phi_ij |ij><ij|). This is the finite
   dimensional stand-in for an algebraic/correlation-mediated gravitational
   channel. It can entangle iff the invariant phase
   delta = phi_LL + phi_RR - phi_LR - phi_RL is nonzero mod 2*pi.

2. mean_field_local:
   A product of local phase rotations. This represents a deterministic
   semiclassical mean field. It cannot entangle.

3. classical_stochastic_locc:
   A mixture of product phase rotations driven by a shared classical random
   variable. This represents a classical noisy mediator/LOCC channel. It cannot
   entangle an initially separable state.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


HBAR = 1.054_571_817e-34
G = 6.674_30e-11


@dataclass(frozen=True)
class BMVGeometry:
    """One-dimensional path geometry for two equal masses.

    Mass A paths are at x = +/- separation / 2.
    Mass B paths are centered at baseline, also +/- separation / 2.

    Basis order: |LL>, |LR>, |RL>, |RR>, where L/R are path labels for A/B.
    """

    mass_kg: float = 1.0e-14
    interaction_time_s: float = 1.0
    baseline_m: float = 2.0e-4
    separation_m: float = 1.0e-4

    def distances(self) -> np.ndarray:
        s = self.separation_m
        d = self.baseline_m
        if d <= s:
            raise ValueError("baseline_m must be larger than separation_m")
        x_a = np.array([-s / 2.0, +s / 2.0])
        x_b = d + np.array([-s / 2.0, +s / 2.0])
        return np.array(
            [
                abs(x_b[0] - x_a[0]),  # LL
                abs(x_b[1] - x_a[0]),  # LR
                abs(x_b[0] - x_a[1]),  # RL
                abs(x_b[1] - x_a[1]),  # RR
            ],
            dtype=float,
        )

    def gravitational_phases(self) -> np.ndarray:
        """Dimensionless phases G m^2 t / (hbar r_ij)."""

        kappa = G * self.mass_kg * self.mass_kg * self.interaction_time_s / HBAR
        return kappa / self.distances()


def ket_plus_plus() -> np.ndarray:
    return np.ones(4, dtype=complex) / 2.0


def density(psi: np.ndarray) -> np.ndarray:
    return np.outer(psi, psi.conj())


def quantum_bilocal_phase(phases: np.ndarray) -> np.ndarray:
    psi = ket_plus_plus() * np.exp(-1j * phases)
    return density(psi)


def mean_field_local(phases: np.ndarray) -> np.ndarray:
    """Best local additive approximation phi_ij ~= alpha_i + beta_j."""

    matrix = phases.reshape(2, 2)
    alpha = matrix.mean(axis=1)
    beta = matrix.mean(axis=0) - matrix.mean()
    local_phases = np.array(
        [alpha[0] + beta[0], alpha[0] + beta[1], alpha[1] + beta[0], alpha[1] + beta[1]]
    )
    psi = ket_plus_plus() * np.exp(-1j * local_phases)
    return density(psi)


def classical_stochastic_locc(samples: int = 400, noise_strength: float = 1.0) -> np.ndarray:
    """Mixture of product unitaries driven by a shared classical variable."""

    rng = np.random.default_rng(7)
    rho = np.zeros((4, 4), dtype=complex)
    for z in rng.normal(size=samples):
        # Shared random variable, but only local phases. This is LOCC.
        a = noise_strength * z
        b = -0.7 * noise_strength * z
        phases = np.array([a + b, a - b, -a + b, -a - b], dtype=float)
        psi = ket_plus_plus() * np.exp(-1j * phases)
        rho += density(psi)
    return rho / samples


def partial_transpose_b(rho: np.ndarray) -> np.ndarray:
    reshaped = rho.reshape(2, 2, 2, 2)
    return reshaped.transpose(0, 3, 2, 1).reshape(4, 4)


def negativity(rho: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(partial_transpose_b(rho))
    return float(np.sum(np.abs(evals[evals < 0.0])))


def concurrence_for_pure_state_rho(rho: np.ndarray) -> float:
    evals, vecs = np.linalg.eigh(rho)
    psi = vecs[:, int(np.argmax(evals))]
    a, b, c, d = psi
    return float(2.0 * abs(a * d - b * c))


def invariant_phase(phases: np.ndarray) -> float:
    return float(phases[0] + phases[3] - phases[1] - phases[2])


def run_case(geometry: BMVGeometry) -> dict[str, float]:
    phases = geometry.gravitational_phases()
    delta = invariant_phase(phases)
    rho_quantum = quantum_bilocal_phase(phases)
    rho_mean = mean_field_local(phases)
    rho_classical = classical_stochastic_locc()

    return {
        "phase_LL": float(phases[0]),
        "phase_LR": float(phases[1]),
        "phase_RL": float(phases[2]),
        "phase_RR": float(phases[3]),
        "delta": delta,
        "analytic_concurrence": abs(math.sin(delta / 2.0)),
        "quantum_concurrence": concurrence_for_pure_state_rho(rho_quantum),
        "quantum_negativity": negativity(rho_quantum),
        "mean_field_negativity": negativity(rho_mean),
        "classical_locc_negativity": negativity(rho_classical),
    }


def sweep_interaction_time(base: BMVGeometry) -> list[tuple[float, float]]:
    out = []
    for tau in np.geomspace(0.01, 100.0, 17):
        geom = BMVGeometry(
            mass_kg=base.mass_kg,
            interaction_time_s=float(tau),
            baseline_m=base.baseline_m,
            separation_m=base.separation_m,
        )
        result = run_case(geom)
        out.append((tau, result["analytic_concurrence"]))
    return out


def main() -> None:
    geometry = BMVGeometry()
    result = run_case(geometry)

    print("RAPC/BMV finite toy model")
    print("=========================")
    print(
        "geometry:",
        f"m={geometry.mass_kg:.2e} kg,",
        f"tau={geometry.interaction_time_s:.2f} s,",
        f"d={geometry.baseline_m:.2e} m,",
        f"s={geometry.separation_m:.2e} m",
    )
    print()
    for key, value in result.items():
        print(f"{key:27s} {value:.12g}")

    print()
    print("time sweep: tau_s -> concurrence")
    for tau, conc in sweep_interaction_time(geometry):
        print(f"{tau:10.5g} -> {conc:.12g}")


if __name__ == "__main__":
    main()
