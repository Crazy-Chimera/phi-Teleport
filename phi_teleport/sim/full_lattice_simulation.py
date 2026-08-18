"""
Full qubit lattice simulation during bridge formation.
"""

import numpy as np
from typing import Tuple, List
from phi_teleport.quantum.decoherence_model import LindbladDecoherence


class FullLatticeSimulation:
    """Simulate the time evolution of the qubit lattice under decoherence.

    Parameters
    -
    n_qubits : int
        Total number of qubits (arranged in a square lattice).
    T1 : float
        Energy relaxation time (s).
    T2 : float
        Dephasing time (s).
    """

    def __init__(self, n_qubits: int = 1024,
                 T1: float = 1e-6, T2: float = 5e-7):
        self.n_qubits = n_qubits
        self.decoherence = LindbladDecoherence(T1=T1, T2=T2)
        self.coherence = np.ones(n_qubits, dtype=complex)

    def step(self, dt: float, coupling_strength: float) -> float:
        """Advance one time step and return average |coherence|."""
        gamma = self.decoherence.total_decoherence()
        protection = 1.0 / (1.0 + gamma / (coupling_strength + 1e-12))
        noise = np.random.normal(0, 0.01, self.n_qubits)
        decay = np.exp(-gamma * dt * protection) + noise * dt
        self.coherence *= decay
        self.coherence = np.clip(self.coherence, 0.0, 1.0)
        avg = np.mean(np.abs(self.coherence))
        return avg

    def run(self, duration: float = 20.0, dt: float = 0.01,
            coupling_schedule: callable = lambda t: 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """Run the full simulation and return time steps and average coherence."""
        t = np.arange(0, duration, dt)
        coh = np.zeros_like(t)
        for i, ti in enumerate(t):
            coupling = coupling_schedule(ti)
            coh[i] = self.step(dt, coupling)
        return t, coh
