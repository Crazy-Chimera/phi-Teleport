"""
Physically motivated decoherence model using minimal Lindblad relaxation.
For a transmon qubit with energy relaxation time T1 and dephasing time T2,
the total decoherence rate is Γ = 1/(2T1) + 1/T2.
The local entanglement density Φ is estimated from the inverse of T2.
"""

import numpy as np


class LindbladDecoherence:
    """Computes decoherence rates from temperature and coupling strengths.

    Parameters
    -
    T1 : float
        Energy relaxation time in seconds.
    T2 : float
        Dephasing time in seconds.
    """

    def __init__(self, T1: float = 1e-6, T2: float = 5e-7):
        self.T1 = T1
        self.T2 = T2

    def gamma_relaxation(self) -> float:
        """Energy relaxation rate Γ1 = 1/T1."""
        return 1.0 / self.T1

    def gamma_dephasing(self) -> float:
        """Pure dephasing rate Γφ = 1/T2 - 1/(2T1)."""
        return max(0.0, 1.0 / self.T2 - 1.0 / (2.0 * self.T1))

    def total_decoherence(self) -> float:
        """Total decoherence rate Γ = Γ1/2 + Γφ."""
        return 0.5 * self.gamma_relaxation() + self.gamma_dephasing()

    def estimate_phi(self) -> float:
        """Estimate local Φ from dephasing time: Φ = 1 - exp(-T2 / T_ref)."""
        T_ref = 1e-5  # reference time in seconds
        return 1.0 - np.exp(-self.T2 / T_ref)
