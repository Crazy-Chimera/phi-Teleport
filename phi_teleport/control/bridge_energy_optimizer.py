"""
Bridge energy optimizer – computes a time‑varying stimulation profile
that minimizes the total number of informions for a given fidelity.
"""

import numpy as np
from typing import Tuple, List
from phi_teleport.constants import (
    PLANCK_LENGTH,
    DEFAULT_OBJECT_RADIUS,
    DEFAULT_GAMMA_STIM,
    DEFAULT_GAMMA_DECAY,
    INFORMION_ENERGY,
    EV_TO_JOULE,
)


class BridgeEnergyOptimizer:
    """Optimize informion usage during bridge activation.

    Parameters
    -
    gamma_decay : float
        Decoherence rate of the entanglement channel.
    fidelity_target : float
        Minimum acceptable fidelity at the end of the activation.
    max_stim_rate : float
        Maximum allowed stimulation rate.
    """

    def __init__(self, gamma_decay: float = DEFAULT_GAMMA_DECAY,
                 fidelity_target: float = 0.999999,
                 max_stim_rate: float = 1.0):
        self.gamma_decay = gamma_decay
        self.fidelity_target = fidelity_target
        self.max_stim_rate = max_stim_rate

    def optimize(self, I0: float, target_I: float,
                 duration: float = 200.0, dt: float = 0.1) -> Tuple[np.ndarray, np.ndarray, float]:
        """Return time steps, stimulation profile, and total informion count."""
        t = np.arange(0, duration, dt)
        I = np.zeros_like(t)
        stim_profile = np.zeros_like(t)
        I[0] = I0

        for i in range(1, len(t)):
            current_I = I[i-1]
            remaining = max(0.0, target_I - current_I)
            rate = min(self.max_stim_rate, remaining / (dt * 10.0))
            rate += self.gamma_decay

            stim_profile[i] = rate
            dI = rate * current_I * (1 - current_I) - self.gamma_decay * current_I
            I[i] = max(0.0, min(1.0, current_I + dI * dt))

        total_informions = np.sum(stim_profile * I) * dt
        energy = total_informions * INFORMION_ENERGY * EV_TO_JOULE
        return t, stim_profile, energy
