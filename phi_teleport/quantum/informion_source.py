"""
Informion source with stimulated emission.

Solves the logistic equation for entanglement growth and provides
critical traversal time and required energy.
"""

import numpy as np
from typing import Tuple, Optional
from phi_teleport.constants import (
    DEFAULT_GAMMA_STIM,
    DEFAULT_GAMMA_DECAY,
    DEFAULT_OBJECT_RADIUS,
    INFORMION_ENERGY,
    EV_TO_JOULE,
)


class InformionSource:
    """Models stimulated emission of informions I⁰.

    Parameters
    -
    gamma_stim : float
        Stimulated emission coefficient [1/s].
    gamma_dec : float
        Decoherence coefficient [1/s].
    """

    def __init__(self, gamma_stim: float = DEFAULT_GAMMA_STIM,
                 gamma_dec: float = DEFAULT_GAMMA_DECAY):
        self.gamma_stim = gamma_stim
        self.gamma_dec = gamma_dec

    def dI_dt(self, I: float, u: float = 1.0) -> float:
        """Rate of change of mutual information I."""
        return self.gamma_stim * u * I * (1.0 - I) - self.gamma_dec * I

    def simulate(self, I0: float = 1e-40, duration: float = 200.0,
                 dt: float = 0.1, u_profile=None) -> Tuple[np.ndarray, np.ndarray]:
        """Simulate entanglement growth over time.

        Parameters
        -
        I0 : float
            Initial mutual information.
        duration : float
            Total simulation time [s].
        dt : float
            Time step [s].
        u_profile : callable or None
            Optional stimulation profile as a function of time.

        Returns
        -
        t : np.ndarray
            Time steps.
        I : np.ndarray
            Mutual information at each time step.
        """
        t = np.arange(0.0, duration, dt)
        I = np.zeros_like(t)
        I[0] = I0

        for i in range(1, len(t)):
            u = 1.0 if u_profile is None else u_profile(t[i])
            dI = self.dI_dt(I[i-1], u)
            I[i] = I[i-1] + dI * dt
            I[i] = max(0.0, min(1.0, I[i]))

        return t, I

    def critical_time(self, object_radius: float = DEFAULT_OBJECT_RADIUS,
                      I0: float = 1e-40, duration: float = 200.0,
                      dt: float = 0.1) -> Optional[float]:
        """Return the time at which the bridge becomes traversable.

        The bridge is traversable when the emergent distance falls below
        the object radius. Uses the relation d = ℓ_P / I.

        Returns
        -
        float or None
            Critical time in seconds, or None if never reached.
        """
        t, I = self.simulate(I0=I0, duration=duration, dt=dt)
        I_crit = 1e-35 / object_radius  # approximate ℓ_P / r
        for i in range(len(t)):
            if I[i] >= I_crit:
                return float(t[i])
        return None

    def required_energy(self, num_informions: float = 1e15) -> float:
        """Return the total energy for a given number of informions."""
        return num_informions * INFORMION_ENERGY * EV_TO_JOULE
