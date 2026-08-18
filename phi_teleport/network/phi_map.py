"""
Global Φ‑map maintenance.
"""

import time
from typing import Dict, Tuple


class PhiMap:
    """A global map of Φ values across teleportation gates.

    Parameters
    -
    decay_factor : float
        How quickly old Φ values decay if not refreshed.
    """

    def __init__(self, decay_factor: float = 0.99):
        self.phi_values: Dict[str, float] = {}
        self.last_updated: Dict[str, float] = {}
        self.decay_factor = decay_factor

    def update(self, gate_id: str, phi: float) -> None:
        """Record a new Φ measurement for a gate."""
        self.phi_values[gate_id] = max(0.0, min(1.0, phi))
        self.last_updated[gate_id] = time.time()

    def get_phi(self, gate_id: str) -> float:
        """Return the current Φ for a gate, applying time decay."""
        raw = self.phi_values.get(gate_id, 0.5)
        updated = self.last_updated.get(gate_id, time.time())
        age = time.time() - updated
        decayed = raw * (self.decay_factor ** age)
        return max(0.0, min(1.0, decayed))

    def average_phi(self) -> float:
        """Return the average Φ over all known gates."""
        if not self.phi_values:
            return 0.5
        return sum(self.get_phi(g) for g in self.phi_values) / len(self.phi_values)

    def high_phi_gates(self, threshold: float = 0.7) -> list:
        """Return a list of gates with Φ above the threshold."""
        return [g for g in self.phi_values if self.get_phi(g) > threshold]
