"""
Online system identification for teleportation bridge parameters.
"""

import numpy as np
from typing import Tuple


class OnlineSystemIdentifier:
    """Recursive least‑squares estimator for Γ_stim and Γ_dec.

    The model is: dI/dt = Γ_stim · u(t) · I · (1 - I) - Γ_dec · I.

    Parameters
    -
    forgetting_factor : float
        Exponential forgetting factor (0 < λ ≤ 1).
    initial_theta : tuple
        Initial guess for (Γ_stim, Γ_dec).
    """

    def __init__(self, forgetting_factor: float = 0.99,
                 initial_theta: Tuple[float, float] = (0.15, 0.05)):
        self.lam = forgetting_factor
        self.theta = np.array(initial_theta, dtype=float)  # [Γ_stim, Γ_dec]
        self.P = np.eye(2) * 1e3  # large initial covariance
        self.ready = False

    def update(self, I_prev: float, I_next: float, u: float, dt: float) -> None:
        """Update parameter estimates from a single transition observation."""
        # Regressor vector: [u·I·(1-I), -I]
        phi = np.array([
            u * I_prev * (1 - I_prev),
            -I_prev,
        ], dtype=float)
        # Predicted output (dI/dt · dt ≈ I_next - I_prev)
        y = (I_next - I_prev) / dt

        # RLS update
        gain = self.P @ phi / (self.lam + phi @ self.P @ phi)
        error = y - phi @ self.theta
        self.theta += gain * error
        self.P = (self.P - np.outer(gain, phi) @ self.P) / self.lam
        self.theta[0] = max(0.0, self.theta[0])  # Γ_stim must be positive
        self.theta[1] = max(0.0, self.theta[1])  # Γ_dec must be positive
        self.ready = True

    def get_params(self) -> Tuple[float, float]:
        """Return the current (Γ_stim, Γ_dec) estimates."""
        return float(self.theta[0]), float(self.theta[1])
