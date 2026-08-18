"""
Superconducting qubit array for teleportation nodes.

Models a two‑dimensional lattice of transmon qubits with tunable
tunneling, detuning, and coupling parameters. Computes local Φ from
decoherence and provides emergent distance.
"""

import numpy as np
from typing import Tuple
from phi_teleport.constants import (
    PLANCK_LENGTH,
    DEFAULT_QUBIT_ROWS,
    DEFAULT_QUBIT_COLS,
    DEFAULT_T1,
    DEFAULT_T2,
)
from phi_teleport.quantum.decoherence_model import LindbladDecoherence


class QubitArray:
    """Two‑dimensional transmon qubit array operating in annealing mode.

    Parameters
    -
    rows : int
        Number of rows in the lattice.
    cols : int
        Number of columns in the lattice.
    T1 : float
        Energy relaxation time [s].
    T2 : float
        Dephasing time [s].
    """

    def __init__(self, rows: int = DEFAULT_QUBIT_ROWS, cols: int = DEFAULT_QUBIT_COLS,
                 T1: float = DEFAULT_T1, T2: float = DEFAULT_T2):
        self.n_rows = rows
        self.n_cols = cols
        self.n_qubits = rows * cols
        self.T1 = T1
        self.T2 = T2

        # Tunneling energies Δ_i and detuning energies ε_i
        self.delta = np.full(self.n_qubits, 0.1)  # GHz
        self.epsilon = np.zeros(self.n_qubits)    # GHz

        # Coupling matrix J_ij (nearest neighbors only)
        self.J = np.zeros((self.n_qubits, self.n_qubits))
        self._initialize_couplings()

        # Decoherence model for Φ measurement
        self.decoherence = LindbladDecoherence(T1=T1, T2=T2)

    def _initialize_couplings(self):
        """Set up nearest‑neighbor couplings on the square lattice."""
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                idx = i * self.n_cols + j
                if i + 1 < self.n_rows:
                    self.J[idx, idx + self.n_cols] = 0.05
                    self.J[idx + self.n_cols, idx] = 0.05
                if j + 1 < self.n_cols:
                    self.J[idx, idx + 1] = 0.05
                    self.J[idx + 1, idx] = 0.05

    def measure_local_phi(self) -> float:
        """Measure local entanglement density Φ.

        Uses the inverse of the dephasing time T₂ as a proxy.
        """
        return self.decoherence.estimate_phi()

    def emergent_distance(self, information: float) -> float:
        """Return the emergent distance for a given mutual information."""
        if information <= 0:
            return float('inf')
        return PLANCK_LENGTH / information

    def set_couplings(self, J_matrix: np.ndarray):
        """Set the coupling matrix directly (for Compute optimization)."""
        if J_matrix.shape != (self.n_qubits, self.n_qubits):
            raise ValueError("Coupling matrix must have dimensions n_qubits x n_qubits")
        self.J = J_matrix.copy()

    def set_detuning(self, epsilon: np.ndarray):
        """Set detuning energies for all qubits."""
        if epsilon.shape != (self.n_qubits,):
            raise ValueError("Detuning array must have length n_qubits")
        self.epsilon = epsilon.copy()

    def set_tunneling(self, delta: np.ndarray):
        """Set tunneling energies for all qubits."""
        if delta.shape != (self.n_qubits,):
            raise ValueError("Tunneling array must have length n_qubits")
        self.delta = delta.copy()
