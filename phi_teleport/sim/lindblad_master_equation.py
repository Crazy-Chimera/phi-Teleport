"""
Numerical Lindblad master equation for a small chain of qubits.
"""

import numpy as np
from scipy.linalg import expm
from typing import List, Tuple


def sigma_x(n: int, site: int) -> np.ndarray:
    """Pauli X operator on site `site` of an n‑qubit chain."""
    I2 = np.eye(2, dtype=complex)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    op = 1
    for i in range(n):
        op = np.kron(op, X if i == site else I2)
    return op

def sigma_z(n: int, site: int) -> np.ndarray:
    """Pauli Z operator on site `site` of an n‑qubit chain."""
    I2 = np.eye(2, dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    op = 1
    for i in range(n):
        op = np.kron(op, Z if i == site else I2)
    return op

def lindblad_superoperator(H: np.ndarray,
                           L_ops: List[np.ndarray],
                           gamma: List[float]) -> np.ndarray:
    """Build the Lindblad superoperator in matrix form."""
    dim = H.shape[0]
    I = np.eye(dim, dtype=complex)
    H_term = -1j * (np.kron(I, H) - np.kron(H.T, I))
    L_super = H_term
    for L_k, g in zip(L_ops, gamma):
        Lk = np.array(L_k, dtype=complex)
        term1 = g * np.kron(Lk.conj(), Lk)
        LdagL = Lk.conj().T @ Lk
        term2 = -0.5 * g * (np.kron(I, LdagL) + np.kron(LdagL.T, I))
        L_super += term1 + term2
    return L_super


class LindbladChainSimulator:
    """Simulate a small qubit chain using the full Lindblad equation.

    Parameters
    -
    n_qubits : int
        Number of qubits (2–4).
    J : float
        Ising coupling strength between nearest neighbors.
    gamma_decay : float
        Decoherence rate for amplitude damping.
    gamma_dephase : float
        Dephasing rate.
    """

    def __init__(self, n_qubits: int = 2, J: float = 0.1,
                 gamma_decay: float = 0.01, gamma_dephase: float = 0.02):
        if not 2 <= n_qubits <= 4:
            raise ValueError("Only 2–4 qubits are supported.")
        self.n = n_qubits
        self.J = J
        self.gamma_decay = gamma_decay
        self.gamma_dephase = gamma_dephase
        self.dim = 2 ** n_qubits

    def build_hamiltonian(self) -> np.ndarray:
        """Ising Hamiltonian: H = -J Σ Z_i Z_{i+1}."""
        H = np.zeros((self.dim, self.dim), dtype=complex)
        for i in range(self.n - 1):
            H -= self.J * (sigma_z(self.n, i) @ sigma_z(self.n, i+1))
        return H

    def build_lindblad_ops(self) -> Tuple[List[np.ndarray], List[float]]:
        """Return Lindblad operators and their rates."""
        L_ops = []
        gamma = []
        for i in range(self.n):
            lowering = (sigma_x(self.n, i) + 1j * sigma_x(self.n, i)) / 2
            L_ops.append(lowering)
            gamma.append(self.gamma_decay)
        for i in range(self.n):
            L_ops.append(sigma_z(self.n, i))
            gamma.append(self.gamma_dephase)
        return L_ops, gamma

    def initial_bell_state(self) -> np.ndarray:
        """Return the maximally entangled Bell state between first two qubits."""
        if self.n < 2:
            raise ValueError("Need at least 2 qubits for Bell state.")
        bell = np.zeros((4, 4), dtype=complex)
        bell[0, 0] = 0.5
        bell[0, 3] = 0.5
        bell[3, 0] = 0.5
        bell[3, 3] = 0.5
        rho = bell
        for _ in range(self.n - 2):
            rho = np.kron(rho, np.eye(2, dtype=complex) / 2.0)
        return rho

    def run(self, duration: float = 10.0, dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate the master equation and return time and concurrence."""
        H = self.build_hamiltonian()
        L_ops, gamma = self.build_lindblad_ops()
        L_super = lindblad_superoperator(H, L_ops, gamma)

        t = np.arange(0, duration, dt)
        rho = self.initial_bell_state()
        concurrence = np.zeros_like(t)

        for i, _ in enumerate(t):
            concurrence[i] = self._concurrence(rho)
            rho_vec = rho.reshape(-1)
            rho_vec = expm(L_super * dt) @ rho_vec
            rho = rho_vec.reshape(self.dim, self.dim)
            rho = (rho + rho.conj().T) / 2
            rho = rho / np.trace(rho)

        return t, concurrence

    def _concurrence(self, rho: np.ndarray) -> float:
        """Compute concurrence for a two‑qubit subsystem."""
        if self.n == 2:
            rho_ab = rho
        else:
            dim_rest = 2 ** (self.n - 2)
            rho_ab = np.zeros((4, 4), dtype=complex)
            for i in range(4):
                for j in range(4):
                    val = 0.0
                    for k in range(dim_rest):
                        val += rho[i*dim_rest + k, j*dim_rest + k]
                    rho_ab[i, j] = val

        sigma_y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        R = rho_ab @ (sigma_y @ rho_ab.conj() @ sigma_y)
        eigvals = np.sort(np.sqrt(np.maximum(np.real(np.linalg.eigvals(R)), 0)))
        if len(eigvals) < 4:
            return 0.0
        concurrence = max(0.0, eigvals[-1] - eigvals[-2] - eigvals[-3] - eigvals[-4])
        return float(concurrence)
