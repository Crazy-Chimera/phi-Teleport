"""
Pontryagin‑based optimal informion injection.

Solves the optimal control problem:

    minimize  ∫₀ᵀ u(t) dt

subject to

    dI/dt = Γ_stim · u(t) · I · (1 - I) - Γ_dec · I,
    I(0) = I0,
    I(T) ≥ I_target,
    0 ≤ u(t) ≤ u_max.

Uses shooting method to find the switching time for bang‑bang control.
"""

import numpy as np
from typing import Tuple
from phi_teleport.constants import (
    DEFAULT_GAMMA_STIM,
    DEFAULT_GAMMA_DECAY,
)


class PontryaginOptimizer:
    """Optimal informion injection using Pontryagin's minimum principle.

    Parameters
    -
    gamma_stim : float
        Maximum stimulated emission rate when u(t)=1.
    gamma_decay : float
        Decoherence rate.
    u_max : float
        Maximum allowed control input (normalized).
    """

    def __init__(self, gamma_stim: float = DEFAULT_GAMMA_STIM,
                 gamma_decay: float = DEFAULT_GAMMA_DECAY,
                 u_max: float = 1.0):
        self.gamma_stim = gamma_stim
        self.gamma_decay = gamma_decay
        self.u_max = u_max

    def _dynamics(self, I: np.ndarray, u: np.ndarray, dt: float) -> np.ndarray:
        """Advance I one step using the controlled logistic equation."""
        dI = self.gamma_stim * u * I * (1.0 - I) - self.gamma_decay * I
        return I + dI * dt

    def _simulate_with_switch(self, I0: float, T: float, dt: float,
                              t_switch: float) -> Tuple[np.ndarray, np.ndarray, float]:
        """Simulate using u(t)=u_max for t<t_switch, then u(t)=0."""
        n_steps = int(T / dt)
        t = np.linspace(0, T, n_steps)
        I = np.zeros_like(t)
        u = np.zeros_like(t)
        I[0] = I0
        for i in range(1, n_steps):
            u_i = self.u_max if t[i] < t_switch else 0.0
            u[i] = u_i
            I[i] = self._dynamics(I[i-1], u_i, dt)
            I[i] = max(0.0, min(1.0, I[i]))
        cost = np.sum(u) * dt
        return t, I, cost

    def solve(self, I0: float, I_target: float,
              T: float = 200.0, dt: float = 0.1,
              tol: float = 1e-12) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return time steps, optimal information trajectory, and control profile."""
        # Check if target is reachable with full control from start.
        t_full, I_full, _ = self._simulate_with_switch(I0, T, dt, T)
        if I_full[-1] < I_target:
            return t_full, I_full, np.full_like(t_full, self.u_max)

        # Check if coasting from start already reaches target.
        t_coast, I_coast, _ = self._simulate_with_switch(I0, T, dt, 0.0)
        if I_coast[-1] >= I_target:
            return t_coast, I_coast, np.zeros_like(t_coast)

        # Bisection on switching time.
        lo, hi = 0.0, T
        for _ in range(200):
            mid = (lo + hi) / 2.0
            _, I_mid, _ = self._simulate_with_switch(I0, T, dt, mid)
            if I_mid[-1] >= I_target:
                hi = mid
            else:
                lo = mid
        t_switch = (lo + hi) / 2.0
        t, I, u = self._simulate_with_switch(I0, T, dt, t_switch)
        return t, I, u

    def total_effort(self, I0: float, I_target: float,
                     T: float = 200.0, dt: float = 0.1) -> float:
        _, _, u = self.solve(I0, I_target, T, dt)
        return float(np.sum(u) * dt)
